import os
from urllib.parse import urlencode

import google_auth_oauthlib.flow as gflow
import googleapiclient.discovery as gdiscovery
import requests
import tg
import transaction
from repoze.who.interfaces import IAuthenticator, IChallenger, IIdentifier
from tg.configuration.auth import TGAuthMetadata
from tg.exceptions import HTTPFound
from webob import Request
from zope.interface import implementer

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
        auth_header = environ.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None
        method, _, token = auth_header.partition(" ")
        if method != "Bearer":
            return None
        environ["tg.skip_auth_challenge"] = True
        return {"token": token, "identifier": "token"}

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
class MPAPIAuthenticator(BaseAuth):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s = requests.Session()

    def identify(self, environ):
        request = Request(environ)
        try:
            ticket = request.GET["tkt"]
        except KeyError:
            return None

        return {"login": ticket, "identifier": "mpapi"}

    def forget(self, environ, identity):
        headers = super().forget(environ, identity)
        headers.append(("Location", self.mpapi_slo))
        return headers

    def authenticate(self, environ, identity):
        try:
            ticket = identity["login"]
        except KeyError:
            return None

        if identity["identifier"] != "mpapi":
            return None

        r = requests.post(self.mpapi_fetch, data={"tkt": ticket})
        r.raise_for_status()
        data = r.json()
        if data["result"] != "success":
            raise ValueError("MPAPI Failure")
        username = data["uid"]
        attributes = data["attributes"]
        uid = attributes["uidNumber"]
        full_name = "{} {}".format(attributes["first"], attributes["sn"])
        email = attributes["mail"]

        user = DBSession.query(User).filter(User.id == uid).one_or_none()
        if user:
            # Update attributes in case of username/full name change
            user.username = username
            user.full_name = full_name
            user.email = email
        else:
            user = User(id=uid, username=username, full_name=full_name, email=email)
            DBSession.add(user)

        DBSession.flush()
        transaction.commit()
        return username

    def new_user_by_username(self, username):
        url = f"{self.mpapi_url}/uid/{username}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if data["result"] != "success":
            raise ValueError("MPAPI Failure.  User {username} may not exist?")
        attributes = data["attributes"]
        uid = attributes["uidNumber"]
        full_name = f"{attributes['first']} {attributes['sn']}"
        email = attributes["mail"]
        user = User(id=uid, username=username, full_name=full_name, email=email)
        DBSession.add(user)
        return user

    @property
    def mpapi_url(self) -> str:
        return tg.config["auth.mpapi.url"].rstrip("/")

    @property
    def mpapi_sso(self) -> str:
        return self.mpapi_url + "/sso"

    @property
    def mpapi_fetch(self) -> str:
        return self.mpapi_url + "/fetch"

    @property
    def mpapi_slo(self) -> str:
        return self.mpapi_url + "/slo"

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Provide ``IChallenger`` interface.
        """
        challenger = environ.get("repoze.who.challenge")
        if challenger and challenger != "mpapi":
            return None
        request = Request(environ)
        return_url = tg.url(
            request.application_url + "/post_login", {"came_from": request.path_qs}
        )
        headers = [
            (
                "Location",
                "{}?{}".format(self.mpapi_sso, urlencode({"return": return_url})),
            ),
            *forget_headers,
            *((h, v) for h, v in app_headers if h.lower() == "set-cookie"),
        ]
        return HTTPFound(headers=headers)


@implementer(IIdentifier, IChallenger, IAuthenticator)
class GoogleAuth(BaseAuth):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flow = None

    @property
    def flow(self):
        if not self._flow:
            client_secrets_file = tg.config["glogin.client_secrets_file"]
            if not os.path.isfile(client_secrets_file):
                return None
            self._flow = gflow.Flow.from_client_secrets_file(
                client_secrets_file,
                scopes=[
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                ],
            )
        return self._flow

    def identify(self, environ):
        if not self.flow:
            return None

        request = Request(environ)
        self.flow.redirect_uri = f"{request.application_url}/post_login"
        try:
            code = request.GET["code"]
        except KeyError:
            return None

        return {"code": code, "identifier": "glogin"}

    def authenticate(self, environ, identity):
        if not self.flow:
            return None

        try:
            code = identity["code"]
        except KeyError:
            return None

        if identity["identifier"] != "glogin":
            return None

        self.flow.fetch_token(code=code)
        with gdiscovery.build(
            "oauth2", "v2", credentials=self.flow.credentials
        ) as service:
            userinfo = service.userinfo().get().execute()

        email = userinfo["email"]
        user = DBSession.query(User).filter(User.email == email).one_or_none()
        if not user:
            # TODO: Handle unregistered users?
            return None

        return user.username

    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Provide ``IChallenger`` interface.
        """
        if not self.flow:
            return None

        challenger = environ.get("repoze.who.challenge")
        if challenger != "glogin":
            return None
        request = Request(environ)
        self.flow.redirect_uri = f"{request.application_url}/post_login"
        auth_url, state = self.flow.authorization_url()
        headers = [
            ("Location", auth_url),
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
        return ["admin"] if identity["user"].admin else []
