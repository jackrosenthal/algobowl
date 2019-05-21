import tg
import requests
import transaction
from urllib.parse import urlencode
from webob import Request
from cryptography.fernet import InvalidToken
from tg.exceptions import HTTPFound
from zope.interface import implementer
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger
from tg.configuration.auth import TGAuthMetadata
from algobowl.model import User, DBSession


@implementer(IAuthenticator)
class APITokenAuthenticator(BasicAuthPlugin):
    def __init__(self, *args, realm='basic', **kwargs):
        super().__init__(*args, realm=realm, **kwargs)

    def authenticate(self, environ, identity):
        """
        Return username if the provided identity is a valid API
        token, ``None`` otherwise.
        """
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None

        if login != 'token':
            return None

        try:
            username = tg.app_globals.fernet.decrypt(password.encode('ascii'))
        except InvalidToken:
            return None

        identity['user'] = User.from_username(username)
        if identity['user']:
            return username
        return None


def user_from_mpapi_attributes(attrs):
    return User(
        id=attrs['uidNumber'],
        username=attrs['uid'],
        full_name=attrs['first'] + ' ' + attrs['sn'],
        email=attrs['mail'])


@implementer(IIdentifier, IChallenger, IAuthenticator)
class MPAPIAuthenticator:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s = requests.Session()

    def identify(self, environ):
        request = Request(environ)
        try:
            ticket = request.GET['tkt']
        except KeyError:
            return None

        return {'login': ticket, 'identifier': 'mpapi'}

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins']['cookie']
        return rememberer

    def remember(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        headers = rememberer.forget(environ, identity)
        headers.append(('Location', self.mpapi_slo))
        return headers

    def authenticate(self, environ, identity):
        try:
            ticket = identity['login']
        except KeyError:
            return None

        if identity['identifier'] != 'mpapi':
            return None

        r = requests.post(self.mpapi_fetch, data={'tkt': ticket})
        r.raise_for_status()
        data = r.json()
        if data['result'] != 'success':
            raise ValueError('MPAPI Failure')
        username = data['uid']

        identity['user'] = User.from_username(username)
        if identity['user']:
            return username
        else:
            user = user_from_mpapi_attributes(data['attributes'])
            DBSession.add(user)
            DBSession.flush()
            transaction.commit()
            return username

    @property
    def mpapi_url(self) -> str:
        return tg.config['auth.mpapi.url'].rstrip('/')

    @property
    def mpapi_sso(self) -> str:
        return self.mpapi_url + '/sso'

    @property
    def mpapi_fetch(self) -> str:
        return self.mpapi_url + '/fetch'

    @property
    def mpapi_slo(self) -> str:
        return self.mpapi_url + '/slo'

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Provide ``IChallenger`` interface.
        """
        request = Request(environ)
        return_url = tg.url(
            request.application_url + '/post_login',
            {'came_from': request.path_qs})
        headers = [
            ('Location',
                '{}?{}'.format(
                    self.mpapi_sso,
                    urlencode({'return': return_url}))),
            *forget_headers,
            *((h, v) for h, v in app_headers if h.lower() == 'set-cookie')]
        return HTTPFound(headers=headers)


class AuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth, *args, **kwargs):
        self.sa_auth = sa_auth
        super().__init__(*args, **kwargs)

    def get_user(self, identity, userid):
        return DBSession.query(User).filter_by(username=userid).first()

    def get_groups(self, identity, userid):
        return ['admin'] if identity['user'].admin else []

    def get_permissions(self, identity, userid):
        return ['admin'] if identity['user'].admin else []
