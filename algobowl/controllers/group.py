import datetime
import zipfile
import re
from io import StringIO, BytesIO
from tg import expose, redirect, url, request, response, abort, flash, require
from tg.predicates import not_anonymous, has_permission
from depot.io.utils import FileIntent

import algobowl.lib.problem as problemlib
from algobowl.lib.helpers import ftime
from algobowl.lib.base import BaseController
from algobowl.model import (DBSession, Group, Input, Output, Evaluation,
                            VerificationStatus)

__all__ = ['GroupsController', 'GroupController']

newline_p = re.compile(br'\s*\n')
spacesep_p = re.compile(br'[ \t\v\f]+')


class GroupController(BaseController):
    allow_only = not_anonymous()

    def __init__(self, group):
        self.group = group
        self.base_url = '/group/{}'.format(group.id)

    @expose('algobowl.templates.group.index')
    def index(self):
        stage = None
        if self.group.competition.input_upload_open:
            stage = 'input_upload'
        if self.group.competition.output_upload_open:
            stage = 'output_upload'
        if self.group.competition.verification_open:
            stage = 'verification'
        if self.group.competition.resolution_open:
            stage = 'resolution'
        if self.group.competition.evaluation_open:
            stage = 'evaluation'

        return self.stagepage(stage)

    @expose('algobowl.templates.group.index')
    def stage(self, stage):
        user = request.identity['user']
        if not user.admin:
            abort(403, "Manual stage selection is for admin users only.")
        return self.stagepage(stage)

    def stagepage(self, stage):
        user = request.identity['user']
        submitted_outputs = {o.input.id: o for o in self.group.outputs}
        d = {'competition': self.group.competition,
             'group': self.group,
             'submitted_outputs': submitted_outputs,
             'stage': stage}
        if stage == 'evaluation':
            evals = dict(DBSession
                         .query(Evaluation.to_student_id, Evaluation.score)
                         .filter(Evaluation.group_id == self.group.id)
                         .filter(Evaluation.from_student_id == user.id))
            for member in self.group.users:
                if member.id not in evals.keys():
                    evals[member.id] = 1.0
            d['evals'] = evals
        return d

    @expose()
    def input_upload(self, input_upload=None, team_name=None):
        user = request.identity['user']
        if not user.admin and not self.group.competition.input_upload_open:
            abort(403, "Sorry, input upload stage is closed.")

        if hasattr(input_upload, "file"):
            try:
                contents = input_upload.file.read().decode("utf-8")
            except UnicodeDecodeError:
                flash('Your input contains invalid characters. '
                      'Please correct and try uploading again.',
                      'danger')
                redirect(self.base_url)

            problem = problemlib.load_problem(self.group.competition)
            try:
                input = problem.parse_input(StringIO(contents))
            except problemlib.FileFormatError as e:
                flash(
                    f"Your input is not valid: {e}. Please correct and upload again.",
                    "danger",
                )
                redirect(self.base_url)

            reformatted_contents = StringIO()
            input.write(reformatted_contents)

            f = FileIntent(
                BytesIO(reformatted_contents.getvalue().encode('utf-8')),
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
        user = request.identity['user']
        to_group = DBSession.query(Group).get(to_group)
        if not to_group:
            abort(404, "No such group")
        if to_group.competition_id != self.group.competition_id:
            abort(400, "Cannot submit to a group in another competition")
        if not hasattr(output_file, "file"):
            abort(400, "Must include file in submission")
        comp = self.group.competition
        existing = (DBSession.query(Output)
                             .filter(Output.group_id == self.group.id)
                             .filter(Output.input_id == to_group.input.id)
                             .filter(Output.active == True)
                             .one_or_none())
        if not (user.admin
                or comp.output_upload_open
                or (comp.resolution_open
                    and existing is not None
                    and not existing.use_ground_truth)):
            abort(403, "Forbidden to upload this output at this time")

        try:
            contents = output_file.file.read().decode("utf-8")
        except UnicodeDecodeError:
            return {'status': 'error',
                    'msg': 'Output contains invalid characters.'}

        problem = problemlib.load_problem(comp)

        try:
            output = problem.parse_output(to_group.input.data.file,
                                          StringIO(contents))
        except problemlib.FileFormatError as e:
            return {
                "status": "error",
                "msg": f"Output has formatting errors: {e}",
            }

        new_contents = StringIO()
        output.write(new_contents)

        f = FileIntent(
            BytesIO(new_contents.getvalue().encode("utf-8")),
            'output_from_{}_to_{}.txt'.format(self.group.id, to_group.id),
            'application/octet-stream')
        try:
            output.verify()
        except problemlib.VerificationError:
            ground_truth = VerificationStatus.rejected
        except Exception:
            ground_truth = VerificationStatus.waiting
        else:
            ground_truth = VerificationStatus.accepted

        use_ground_truth = (
            not comp.verification_begins
            or datetime.datetime.now() >= comp.verification_begins
        )

        if existing:
            if comp.resolution_open:
                existing.active = False
            else:
                DBSession.delete(existing)

        db_output = Output(
            data=f,
            group=self.group,
            input=to_group.input,
            score=output.score,
            original=comp.output_upload_open,
            ground_truth=ground_truth,
            use_ground_truth=use_ground_truth,
        )
        DBSession.add(db_output)
        DBSession.flush()

        return {'status': 'success', 'url': db_output.data.url}

    @expose('json')
    def submit_verification(self, output_id, status):
        user = request.identity['user']
        try:
            output_id = int(output_id)
        except ValueError:
            return {'status': 'error',
                    'msg': 'There was an error. Please try clearing your '
                           'browser cache and repeating this action.'}
        output = DBSession.query(Output).get(output_id)
        if not output or output.input.group_id != self.group.id:
            abort(404)
        try:
            status = VerificationStatus[status]
        except KeyError:
            abort(404)
        if not user.admin and not self.group.competition.verification_open:
            return {'status': 'error', 'msg': 'Verification closed'}
        assert output.original is True
        assert output.active is True
        assert output.use_ground_truth is False
        output.verification = status
        return self.verification_data()

    @expose('json')
    def verification_data(self):
        data = {k: str(v)
                for k, v in (DBSession
                             .query(Output.id, Output.verification)
                             .join(Output.input)
                             .filter(Input.group_id == self.group.id))}
        return {'status': 'success', 'data': data}

    @expose()
    def verification_outputs(self):
        user = request.identity['user']
        if not user.admin and not self.group.competition.verification_open:
            abort(403, "This file is only available during verification.")
        f = BytesIO()
        archive = zipfile.ZipFile(f, mode='w')
        outputs = (DBSession.query(Output)
                            .join(Output.input)
                            .filter(Input.group_id == self.group.id))
        for output in outputs:
            archive.writestr(
                'verification_outputs/{}'.format(output.data.filename),
                output.data.file.read())
        archive.close()
        f.seek(0)
        response.content_type = 'application/zip'
        return f.read()

    @expose()
    @require(has_permission("admin"))
    def automatic_verification(self):
        outputs = (DBSession
                   .query(Output)
                   .join(Output.input)
                   .filter(Input.group_id == self.group.id))
        for output in outputs:
            output.verification = output.ground_truth
        DBSession.flush()

    @expose('json')
    def resolution_protest(self, output_id):
        if not self.group.competition.resolution_open:
            return {'status': 'error',
                    'msg': 'Resolution stage is not open.'}
        output = DBSession.query(Output).get(output_id)
        if not output or output.group_id != self.group.id:
            abort(404)
        if not output.active:
            return {'status': 'error',
                    'msg': 'Output has been replaced; cannot protest.'}
        if output.use_ground_truth:
            return {'status': 'error',
                    'msg': 'Output has already been protested.'}
        assert output.original
        output.use_ground_truth = True
        return {'status': 'success'}

    @expose()
    def submit_evaluations(self):
        me = request.identity['user']
        students_allowed = set(user.id for user in self.group.users)
        for user_id, score in request.POST.items():
            user_id = int(user_id)
            if user_id not in students_allowed:
                abort(403, "You cannot submit an evaluation to this user")
            score = float(score)
            if score < 0:
                abort(403, "Negative contributions are not allowed")
            e = (DBSession.query(Evaluation)
                          .filter(Evaluation.from_student_id == me.id)
                          .filter(Evaluation.to_student_id == user_id)
                          .filter(Evaluation.group_id == self.group.id)
                          .one_or_none())
            if not e:
                e = Evaluation(
                    from_student_id=me.id,
                    to_student_id=user_id,
                    group=self.group,
                    score=score)
            else:
                e.score = score
            DBSession.add(e)
        flash('Your evaluations have been saved. Thank you.', 'success')
        redirect('/group/{}'.format(self.group.id))


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
        if user not in group.users and not user.admin:
            abort(403, "You are not a part of this group.")
        return GroupController(group), args

    @expose('algobowl.templates.group.select')
    @expose('json')
    def index(self):
        user = request.identity['user']
        groups = [g for g in user.groups if g.competition.active]

        if len(groups) == 1 and request.response_type != 'application/json':
            redirect(url('/group/{}'.format(groups[0].id)))

        return {'groups': groups}
