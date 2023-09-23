import dataclasses

import tg

from algobowl import model
from algobowl.lib import base


@dataclasses.dataclass
class UserApiController(base.BaseController):
    user: model.User

    @tg.expose("json")
    def info(self):
        return {
            "username": self.user.username,
            "email": self.user.email,
            "id": self.user.id,
            "full_name": self.user.full_name,
            "admin": self.user.admin,
            "groups": [group.id for group in self.user.groups],
        }


class UserLookupApiController(base.BaseController):
    allow_only = tg.predicates.not_anonymous()

    @tg.expose()
    def _lookup(self, lookup, *args):
        def _lookup_by_uid():
            try:
                user_id = int(lookup)
            except ValueError:
                return None
            return (
                model.DBSession.query(model.User)
                .filter(model.User.id == user_id)
                .one_or_none()
            )

        def _lookup_by_username():
            return model.User.from_username(lookup)

        def _lookup_by_email():
            if "@" not in lookup:
                return None
            return (
                model.DBSession.query(model.User)
                .filter(model.User.email == lookup)
                .one_or_none()
            )

        for f in (_lookup_by_uid, _lookup_by_username, _lookup_by_email):
            user = f()
            if user:
                break
        else:
            tg.abort(404, "No such user found")

        return UserApiController(user), args
