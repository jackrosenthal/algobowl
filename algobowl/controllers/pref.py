import datetime

import sqlalchemy
import tg

import algobowl.lib.base as base
import algobowl.model as model


class PrefController(base.BaseController):
    allow_only = tg.predicates.not_anonymous()

    @tg.expose("algobowl.templates.cli_setup")
    @tg.expose("json")
    def cli(self, client_name=None, client_id=None):
        user = tg.request.identity["user"]

        if client_name and client_id:
            if len(client_id) != 88:
                tg.abort(400, "client_id must be 88 characters long")
            if " " in client_id:
                tg.abort(400, "client_id cannot contain spaces")
            token = model.AuthToken(
                client_name=client_name,
                client_id=client_id,
                date_added=datetime.datetime.now(),
                user=user,
            )
            try:
                model.DBSession.add(token)
                model.DBSession.flush()
            except sqlalchemy.exc.IntegrityError:
                tg.flash("Cannot add client (already added?)", "danger")
                model.DBSession.rollback()
            else:
                tg.flash(f"Client {client_name} successfully added!", "success")
            tg.redirect(tg.url("/pref/cli"))

        identity = tg.request.environ.get("repoze.who.identity", {})
        this_client_id = identity.get("token")
        auth_tokens_json = [
            {
                "id": token.id,
                "client_name": token.client_name,
                "date_added": token.date_added.isoformat(),
                "this_client": this_client_id == token.client_id,
            }
            for token in user.auth_tokens
        ]

        return dict(auth_tokens=auth_tokens_json)

    @tg.expose()
    def revoke_auth_token(self, token_id):
        try:
            token_id = int(token_id)
        except ValueError:
            tg.abort(400, "token_id must be an integer")

        user = tg.request.identity["user"]
        query = model.DBSession.query(model.AuthToken).filter(
            model.AuthToken.id == token_id
        )
        token = query.one_or_none()

        if not user.admin and token.user_id != user.id:
            tg.abort(403, "You don't have permission to revoke this token")

        client_name = token.client_name
        query.delete()
        model.DBSession.flush()
        tg.flash(f"Client {client_name} revoked!", "success")
        tg.redirect(tg.url("/pref/cli"))

    @tg.expose("json")
    def whoami(self):
        user = tg.request.identity["user"]
        return {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
        }
