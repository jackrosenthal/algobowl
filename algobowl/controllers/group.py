from tg import expose, redirect, url, request, abort
from tg.predicates import not_anonymous

from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Group

__all__ = ['GroupsController', 'GroupController']


class GroupController(BaseController):
    allow_only = not_anonymous()

    def __init__(self, group):
        self.group = group

    @expose('algobowl.templates.group.index')
    def index(self):
        return {'competition': self.group.competition,
                'group': self.group}


class GroupsController(BaseController):
    allow_only = not_anonymous()

    @expose()
    def _lookup(self, group_id, *args):
        try:
            group_id = int(group_id)
        except ValueError:
            abort(404, "Not a valid group identifier.")
        user = request.identity['user']
        group = DBSession.query(Group).filter(Group.id == group_id).first()
        if not group:
            abort(404, "No such group.")
        if user not in group.users:
            abort(403, "You are not a part of this group.")
        return GroupController(group), args

    @expose('algobowl.templates.group.select')
    @expose('json')
    def index(self):
        user = request.identity['user']
        groups = user.groups

        if len(groups) == 1 and request.response_type != 'application/json':
            redirect(url('/group/{}'.format(groups[0].id)))

        return {'groups': groups}
