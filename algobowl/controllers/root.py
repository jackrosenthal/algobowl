import tg
from repoze.who.api import get_api
from tg import expose, flash, lurl, predicates, redirect, require, tmpl_context, url
from tg.exceptions import HTTPFound
from tgext.admin.controller import AdminController

import algobowl.controllers.file_redirector as file_redirector
import algobowl.controllers.pref as pref_controller
import algobowl.controllers.setup as setup_controller
import algobowl.model
from algobowl.config.app_cfg import AdminConfig
from algobowl.controllers import api
from algobowl.controllers.competition import CompetitionsController
from algobowl.controllers.error import ErrorController
from algobowl.controllers.group import GroupsController
from algobowl.lib.base import BaseController
from algobowl.model import DBSession

__all__ = ["RootController"]


class RootController(BaseController):
    admin = AdminController(algobowl.model, DBSession, config_type=AdminConfig)
    api = api.ApiController()
    setup = setup_controller.SetupController()
    pref = pref_controller.PrefController()
    error = ErrorController()
    group = GroupsController()
    competition = CompetitionsController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "algobowl"

    @expose("algobowl.templates.index")
    def index(self):
        """Handle the front-page."""
        return dict(page="index")

    @expose()
    def algobowl(self):
        """Redirect for old route to homepage"""
        redirect(url("/"))

    @expose("algobowl.templates.privacy")
    def privacy(self):
        return dict(page="privacy")

    @expose("algobowl.templates.tos")
    def tos(self):
        return dict(page="tos")

    @expose()
    def files(self, filename):
        file_redirector.redirect_to_file(filename)

    @expose()
    def login(self):
        if not tg.request.identity:
            tg.request.environ["repoze.who.challenge"] = "mpapi"
            who_api = get_api(tg.request.environ)
            return who_api.challenge()
        redirect(url("/"))

    @expose()
    def glogin(self):
        if not tg.request.identity:
            tg.request.environ["repoze.who.challenge"] = "glogin"
            who_api = get_api(tg.request.environ)
            return who_api.challenge()
        redirect(url("/"))

    @expose()
    @require(predicates.not_anonymous())
    def logout(self):
        who_api = get_api(tg.request.environ)
        headers = who_api.logout()
        return HTTPFound(headers=headers)

    @expose()
    def post_login(self, came_from=lurl("/")):
        if tg.request.identity:
            user = tg.request.identity["user"]
            flash("Welcome, {}!".format(user), "success")
            u = tg.request.relative_url(str(came_from), to_application=True)
            if not u.startswith(tg.request.application_url):
                flash("Dangerous redirect prevented", "warning")
                redirect("/")
            redirect(u)
        else:
            flash("Login failure", "error")
            redirect("/")
