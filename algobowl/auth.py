import requests
import flask
import flask_login
from cryptography.fernet import InvalidToken
from .fernet import fernet
from .model import db, User

__all__ = ('login_manager', 'token_auth', 'MPAPILoginManager',
           'login_blueprint', 'login', 'logout')


class LoginManagerProxy:
    def __init__(self):
        self._login_manager = None

    def init_app(self, app):
        if app.config.get('AUTH_TYPE') == 'MPAPI':
            self._login_manager = MPAPILoginManager(app.config['MPAPI_URL'])
        else:
            raise ValueError("Unknown AUTH_TYPE")
        self._login_manager.init_app(app)
        app.register_blueprint(login_blueprint)

    def __getattr__(self, name):
        return getattr(self._login_manager, name)


login_manager = LoginManagerProxy()
login_blueprint = flask.Blueprint('auth', __name__)


@login_blueprint.route('/login')
def login():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))

    return login_manager.login()


@flask_login.login_required
@login_blueprint.route('/logout')
def logout():
    return login_manager.logout()


def token_auth(request, user_from_id):
    try:
        token = request.authorization.password
    except AttributeError:
        return None

    if request.authorizaion.username != 'token':
        return None

    try:
        username = fernet.decrypt(token.encode('ascii'))
    except InvalidToken:
        return flask.abort(403)

    return user_from_id(username)


class MPAPILoginManager(flask_login.LoginManager):
    def __init__(self, mpapi_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s = requests.Session()
        self.mpapi_url = mpapi_url.rstrip('/')
        self.unauthorized_handler(self.login)
        self.needs_refresh_handler(self.login)
        self.request_loader(self.load_from_request)
        self.user_loader(self.user_from_id)

    @property
    def mpapi_sso(self) -> str:
        return self.mpapi_url + '/sso'

    @property
    def mpapi_fetch(self) -> str:
        return self.mpapi_url + '/fetch'

    @property
    def mpapi_slo(self) -> str:
        return self.mpapi_url + '/slo'

    def info(self, username: str) -> str:
        r = self.s.get(self.mpapi_url + '/uid/' + username)
        r.raise_for_status()
        data = r.json()
        if data['result'] != 'success':
            raise ValueError('No such MPAPI user')
        return data['attributes']

    def login(self):
        return flask.redirect("{}?return={}"
                              .format(self.mpapi_sso, flask.request.url))

    def logout(self):
        flask_login.logout_user()
        return flask.redirect(self.mpapi_slo)

    def user_from_id(self, id):
        user = User.query.filter_by(username=id).one_or_none()
        if not user:
            info = self.info(id)
            user = User(username=id,
                        email=info['mail'],
                        full_name=info['first'] + ' ' + info['sn'])
            db.session.add(user)
            db.session.commit()
        return user

    def load_from_request(self, request):
        user = token_auth(request, self.user_from_id)
        if user:
            return user

        tkt = request.args.get('tkt')
        if tkt:
            r = self.s.post(self.mpapi_fetch, data={'tkt': tkt})
            r.raise_for_status()
            username = r.json()['uid']
            user = self.user_from_id(username)
            flask_login.login_user(user)
            flask.abort(flask.redirect(flask.request.base_url))

        return None
