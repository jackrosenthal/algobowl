from io import StringIO, BytesIO
from tg import expose, redirect, url, request, abort, flash
from tg.predicates import not_anonymous
from depot.io.utils import FileIntent

from algobowl.lib.helpers import ftime
from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Group, Input

__all__ = ['GroupsController', 'GroupController']


def file_normalize(contents: bytes) -> str:
    contents = contents.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    if not contents.endswith(b'\n'):
        contents += b'\n'
    return contents.decode('utf-8')


class GroupController(BaseController):
    allow_only = not_anonymous()

    def __init__(self, group):
        self.group = group
        self.base_url = '/group/{}'.format(group.id)

    @expose('algobowl.templates.group.index')
    def index(self):
        return {'competition': self.group.competition,
                'group': self.group}

    @expose()
    def input_upload(self, input_upload=None, team_name=None):
        if not self.group.competition.input_upload_open:
            abort(403, "Sorry, input upload stage is closed.")

        if input_upload is not None:
            if not hasattr(input_upload, "file"):
                abort(400, "input_upload provided, but not a file")
            try:
                contents = file_normalize(input_upload.file.read())
            except UnicodeDecodeError:
                flash('Your input contains invalid characters. '
                      'Please correct and try uploading again.',
                      'danger')
                redirect(self.base_url)

            if len(contents) > 1E6:
                abort(400, "Your input exceeds the maxiumum size.")
            verif_mod = self.group.competition.input_verifier.module

            try:
                verif_mod.verify(StringIO(contents))
            except verif_mod.VerificationError as e:
                flash('Your input has been rejected for the following reason: '
                      '{}. Please correct and try uploading again.'.format(e),
                      'danger')
                redirect(self.base_url)

            f = FileIntent(
                BytesIO(contents.encode('utf-8')),
                'input_group{}.txt'.format(self.group.id),
                'application/octet-stream')
            if self.group.input is None:
                iput = Input(data=f, group=self.group)
                DBSession.add(iput)
            else:
                self.group.input.data = f
            DBSession.flush()

        if team_name is not None:
            if len(team_name) >= 100:
                flash('Your team name has been rejected, as it is too long.',
                      'danger')
                redirect(self.base_url)

            if not team_name:
                flash('You must set a team name.',
                      'danger')
                redirect(self.base_url)

            self.group.name = team_name

        flash('Thank you. Please return here for output upload on {}'
              .format(ftime(self.group.competition.output_upload_begins)),
              'success')
        redirect(self.base_url)


class GroupsController(BaseController):
    allow_only = not_anonymous()

    @expose()
    def _lookup(self, group_id, *args):
        try:
            group_id = int(group_id)
        except ValueError:
            abort(404, "Not a valid group identifier.")
        user = request.identity['user']
        group = DBSession.query(Group).get(group_id)
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
