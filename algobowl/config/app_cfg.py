"""
Default configuration for AlgoBOWL
----------------------------------

Configuration in this file is overridden by the paste config.
"""

import tg
from depot.manager import DepotManager
from markupsafe import Markup
from repoze.who.interfaces import IChallenger
from tg.configuration import AppConfig, milestones
from tg.support.converters import asbool
from tgext.admin.config import AdminConfig
from tgext.admin.layouts import BootstrapAdminLayout
from tgext.admin.widgets import BootstrapAdminTableFiller

import algobowl
from algobowl import model
from algobowl.config.auth import AuthMetadata, GoogleAuth, MPAPIAuthenticator, TokenAuth

base_config = AppConfig()
base_config.renderers = []
base_config["flash.default_status"] = "primary"

# True to prevent dispatcher from striping extensions
# For example /socket.io would be served by "socket_io"
# method instead of "socket".
base_config.disable_request_extensions = False

# Set None to disable escaping punctuation characters to "_"
# when dispatching methods.
# Set to a function to provide custom escaping.
base_config.dispatch_path_translator = True

base_config.use_toscawidgets = False
base_config.use_toscawidgets2 = True

base_config.package = algobowl

base_config.renderers.append("json")
base_config.renderers.append("kajiki")
base_config["templating.kajiki.strip_text"] = False
base_config.default_renderer = "kajiki"

base_config["site.branding.name"] = "AlgoBOWL"
base_config["site.edu"] = True

# Configure Sessions, store data as JSON to avoid pickle security issues
base_config["session.enabled"] = True
base_config["session.data_serializer"] = "json"

# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession

# Configure the authentication backend
base_config.auth_backend = "sqlalchemy"
base_config.sa_auth.cookie_secret = "aa8deb7d-a235-4f8d-807a-6497a8bb26af"
base_config.sa_auth.authmetadata = AuthMetadata(base_config.sa_auth)
base_config["identity.allow_missing_user"] = False

authenticators = [
    ("token", TokenAuth()),
    ("mpapi", MPAPIAuthenticator()),
    ("glogin", GoogleAuth()),
]

base_config.sa_auth.authenticators = authenticators
base_config.sa_auth.identifiers = [
    ("default", None),
    *authenticators,
]
base_config.sa_auth.challengers = [
    auth for auth in authenticators if IChallenger.providedBy(auth[1])
]

base_config["auth.mpapi.url"] = "https://mastergo.mines.edu/mpapi"
base_config["depot.storage_path"] = "/tmp/depot"


def variable_provider():
    return {"asbool": asbool}


base_config.variable_provider = variable_provider


def config_ready():
    """Executed once the configuration is ready."""
    # Configure default depot
    DepotManager.configure("default", tg.config)


milestones.config_ready.register(config_ready)


class AdminTableFiller(BootstrapAdminTableFiller):
    def __actions__(self, obj):
        primary_fields = self.__provider__.get_primary_fields(self.__entity__)
        pklist = "/".join(map(lambda x: str(getattr(obj, x)), primary_fields))

        return Markup(
            """
    <a href="{pklist}/edit" class="btn btn-secondary">
        <i class="fas fa-pen fa-fw"></i>
    </a>
    <form method="POST" action="{pklist}" style="display: inline">
        <input type="hidden" name="_method" value="DELETE" />
        <button type="submit" class="btn btn-danger"
                onclick="return confirm('Are you sure?')">
            <i class="fas fa-trash fa-fw"></i>
        </button>
    </form>""".format(
                pklist=pklist
            )
        )


class AdminLayout(BootstrapAdminLayout):
    template_index = "algobowl.templates.admin.index"
    crud_templates = {
        "get_all": ["kajiki:algobowl.templates.admin.get_all"],
        "edit": ["kajiki:algobowl.templates.admin.edit"],
        "new": ["kajiki:algobowl.templates.admin.new"],
    }
    TableFiller = AdminTableFiller


class AdminConfig(AdminConfig):
    project_name = "AlgoBOWL"
    layout = AdminLayout
    allow_only = tg.predicates.has_permission("admin")


try:
    # Enable DebugBar if available, install tgext.debugbar to turn it on
    from tgext.debugbar import enable_debugbar

    enable_debugbar(base_config)
except ImportError:
    pass
