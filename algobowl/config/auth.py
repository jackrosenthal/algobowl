from pathlib import Path
from urllib.parse import quote

import google_auth_oauthlib.flow as gflow
import googleapiclient.discovery as gdiscovery
import sqlalchemy as sa
import tg
from repoze.who.interfaces import IAuthenticator, IChallenger, IIdentifier
from tg.configuration.auth import TGAuthMetadata
from tg.exceptions import HTTPFound, HTTPUnauthorized
from webob import Request
from zope.interface import implementer

from algobowl.lib import constants
from algobowl.model import AuthToken, DBSession, User


class BaseAuth:
    def _get_cookie_plugin(self, environ):
        return environ["repoze.who.plugins"]["cookie"]

    def remember(self, environ, identity):
        return self._get_cookie_plugin(environ).remember(environ, identity)

    def forget(self, environ, identity):
        return self._get_cookie_plugin(environ).forget(environ, identity)


@implementer(IIdentifier, IAuthenticator)
class TokenAuth:
    def identify(self, environ):
        request = Request(environ)
        auth_header = environ.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None
        method, _, token = auth_header.partition(" ")
        if method != "Bearer":
            return None
        environ["tg.skip_auth_challenge"] = True
        sudo = request.headers.get(constants.SUDO_HEADER) == "True"
        return {"token": token, "identifier": "token", "sudo": sudo}

    def remember(self, environ, identity):
        return []

    def forget(self, environ, identity):
        return []

    def authenticate(self, environ, identity):
        if identity.get("identifier") != "token":
            return None
        client_id = identity["token"]

        token = (
            DBSession.query(AuthToken)
            .filter(AuthToken.client_id == client_id)
            .one_or_none()
        )
        if not token:
            return None

        return token.user.username


@implementer(IIdentifier, IChallenger, IAuthenticator)
class GoogleAuth(BaseAuth):
    def _is_configured(self):
        client_secrets_file = tg.config.get("glogin.client_secrets_file", "")
        return bool(client_secrets_file) and Path(client_secrets_file).is_file()

    def _make_flow(self):
        """Create a fresh Flow instance for a single OAuth dance."""
        client_secrets_file = tg.config["glogin.client_secrets_file"]
        return gflow.Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )

    def identify(self, environ):
        if not self._is_configured():
            return None

        request = Request(environ)
        try:
            code = request.GET["code"]
        except KeyError:
            return None

        code_verifier = request.cookies.get("glogin_code_verifier")
        return {"code": code, "identifier": "glogin", "code_verifier": code_verifier}

    def authenticate(self, environ, identity):
        if not self._is_configured():
            return None

        try:
            code = identity["code"]
        except KeyError:
            return None

        if identity["identifier"] != "glogin":
            return None

        request = Request(environ)
        flow = self._make_flow()
        flow.redirect_uri = f"{request.application_url}/post_login"
        code_verifier = identity.get("code_verifier")
        if code_verifier:
            flow.code_verifier = code_verifier
        flow.fetch_token(code=code)
        with gdiscovery.build("oauth2", "v2", credentials=flow.credentials) as service:
            userinfo = service.userinfo().get().execute()

        if not userinfo.get("verified_email"):
            return None

        email = userinfo["email"]
        user = (
            DBSession.query(User)
            .filter(sa.func.lower(User.email) == email.lower())
            .one_or_none()
        )
        if not user:
            # Let post_login explain that this Google account isn't registered.
            environ["algobowl.glogin_unknown_email"] = email
            return None

        return user.username

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Provide ``IChallenger`` interface.
        """
        request = Request(environ)

        # Never attempt to redirect the CLI to Google.
        if constants.CLI_COMPATIBLE_HEADER in request.headers:
            return HTTPUnauthorized("Please run 'algobowl auth login' first.")

        flow = self._make_flow()
        flow.redirect_uri = f"{request.application_url}/post_login"
        # Always show the account chooser, as students commonly have both a
        # personal and a school Google account signed in.
        auth_url, _state = flow.authorization_url(prompt="select_account")
        cookie_attrs = "; HttpOnly; Path=/; SameSite=Lax"
        if request.application_url.startswith("https"):
            cookie_attrs += "; Secure"
        came_from = quote(request.path_qs, safe="")
        headers = [
            ("Location", auth_url),
            ("Set-Cookie", f"glogin_code_verifier={flow.code_verifier}{cookie_attrs}"),
            ("Set-Cookie", f"glogin_came_from={came_from}{cookie_attrs}"),
            *forget_headers,
            *((h, v) for h, v in app_headers if h.lower() == "set-cookie"),
        ]
        return HTTPFound(headers=headers)


class AuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth, *args, **kwargs):
        self.sa_auth = sa_auth
        super().__init__(*args, **kwargs)

    def get_user(self, identity, userid):
        return DBSession.query(User).filter_by(username=userid).first()

    def get_groups(self, identity, userid):
        return ["admin"] if identity["user"].admin else []

    def get_permissions(self, identity, userid):
        if "sudo" in identity and not identity["sudo"]:
            return []
        return ["admin"] if identity["user"].admin else []
