import tg
import algobowl.model
from algobowl.model import DBSession
from tg import expose, flash, require, url, lurl
from tg import redirect, tmpl_context
from tg import predicates
from tg.exceptions import HTTPFound
from repoze.who.api import get_api

from algobowl.config.app_cfg import AdminConfig
from algobowl.lib.base import BaseController
from tgext.admin.controller import AdminController
from algobowl.controllers.error import ErrorController
from algobowl.controllers.group import GroupsController
from algobowl.controllers.competition import CompetitionsController

__all__ = ['RootController']


class RootController(BaseController):
    admin = AdminController(
        algobowl.model,
        DBSession,
        config_type=AdminConfig)
    error = ErrorController()
    group = GroupsController()
    competition = CompetitionsController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "algobowl"

    @expose('algobowl.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose()
    def algobowl(self):
        """Redirect for old route to homepage"""
        redirect(url('/'))

    @expose()
    def login(self):
        if not tg.request.identity:
            who_api = get_api(tg.request.environ)
            return who_api.challenge()
        redirect(url('/'))

    @expose()
    @require(predicates.not_anonymous())
    def logout(self):
        who_api = get_api(tg.request.environ)
        headers = who_api.logout()
        return HTTPFound(headers=headers)

    @expose()
    def post_login(self, came_from=lurl('/')):
        if tg.request.identity:
            user = tg.request.identity['user']
            flash("Welcome, {}!".format(user), 'success')
            u = tg.request.relative_url(str(came_from),
                                        to_application=True)
            if not u.startswith(tg.request.application_url):
                flash("Dangerous redirect prevented", "warning")
                redirect('/')
            redirect(u)
        else:
            flash("Login failure", 'error')
            redirect('/')
