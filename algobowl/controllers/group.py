import datetime
import tg
from io import StringIO, BytesIO
from tg import expose, redirect, url, request, abort, flash
from tg.predicates import not_anonymous
from depot.io.utils import FileIntent

from algobowl.lib.helpers import ftime
from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Group, Input, Output, VerificationStatus

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
        submitted_outputs = {o.input.id: o for o in self.group.outputs}
        return {'competition': self.group.competition,
                'group': self.group,
                'submitted_outputs': submitted_outputs}

    @expose()
    def input_upload(self, input_upload=None, team_name=None):
        if not self.group.competition.input_upload_open:
            abort(403, "Sorry, input upload stage is closed.")

        if hasattr(input_upload, "file"):
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

    @expose('json')
    def submit_output(self, to_group, output_file=None):
        to_group = DBSession.query(Group).get(to_group)
        if not to_group:
            abort(404, "No such group")
        if to_group.competition_id != self.group.competition_id:
            abort(403, "Cannot submit to a group in another competition")
        if not hasattr(output_file, "file"):
            abort(400, "Must include file in submission")
        comp = self.group.competition
        existing = (DBSession.query(Output)
                             .filter(Output.group_id == self.group.id)
                             .filter(Output.input_id == to_group.input.id)
                             .filter(Output.active is True)
                             .one_or_none())
        if not (comp.output_upload_open
                or (comp.resolution_open
                    and existing is not None
                    and not existing.use_ground_truth)):
            abort(403, "Forbidden to upload this output at this time")

        try:
            contents = file_normalize(output_file.file.read())
        except UnicodeDecodeError:
            return {'status': 'error',
                    'msg': 'Output contains invalid characters.'}

        if len(contents) > 1E6:
            return {'status': 'error',
                    'msg': 'Output exceeds maximum size.'}

        try:
            score, _, _ = contents.partition('\n')
            score = int(score)
        except ValueError:
            return {'status': 'error',
                    'msg': 'First line must only contain an integer.'}

        f = FileIntent(
            BytesIO(contents.encode('utf-8')),
            'output_from_{}_to_{}.txt'.format(self.group.id, to_group.id),
            'application/octet-stream')
        if existing:
            if comp.resolution_open:
                existing.active = False
            else:
                DBSession.delete(existing)
        output = Output(data=f, group=self.group, input=to_group.input,
                        score=score, original=comp.output_upload_open)

        verif_mod = self.group.competition.output_verifier.module
        try:
            verif_mod.verify(StringIO(contents))
        except verif_mod.VerificationError:
            output.ground_truth = VerificationStatus.rejected
        except Exception:
            output.ground_truth = VerificationStatus.waiting
        else:
            output.ground_truth = VerificationStatus.accepted

        if comp.resolution_open:
            output.use_ground_truth = True

        DBSession.add(output)
        DBSession.flush()

        return {'status': 'success', 'url': output.data.url}


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
