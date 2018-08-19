import flask
import flask_admin
import flask_login
import flask_admin.contrib.sqla as sqla
from . import model
from . import login_manager


class ModelView(sqla.ModelView):
    def is_accessible(self):
        return getattr(flask_login.current_user, "admin", False)

    def inaccessible_callback(self, name, **kwargs):
        if flask_login.current_user.is_anonymous:
            return login_manager.login()
        return flask.abort(403)


admin = flask_admin.Admin(
    name='AlgoBOWL Administration',
    template_mode='bootstrap3')

admin.add_view(ModelView(model.Competition, model.db.session))
admin.add_view(ModelView(model.User, model.db.session))
admin.add_view(ModelView(model.Group, model.db.session))
admin.add_view(ModelView(model.Input, model.db.session))
admin.add_view(ModelView(model.Output, model.db.session))
admin.add_view(ModelView(model.VerificationProtest, model.db.session))
admin.add_view(ModelView(model.Evaluation, model.db.session))
