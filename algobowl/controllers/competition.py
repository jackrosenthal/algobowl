import zipfile
import datetime
from io import BytesIO
from collections import namedtuple, defaultdict
from tg import expose, abort, request, response, flash, redirect
from sqlalchemy.sql.expression import case
from algobowl.lib.base import BaseController
from algobowl.model import (DBSession, Competition, Input, Output, Group,
                            VerificationStatus, Protest)

__all__ = ['CompetitionsController', 'CompetitionController']


ScoreTuple = namedtuple('ScoreTuple',
                        ['score', 'verification', 'rank', 'output'])


class GroupEntry:
    def __init__(self):
        self.reject_count = 0
        self.sum_of_ranks = 0
        self.penalties = 0
        self.place = 1
        self.input_ranks = {}

    @property
    def score(self):
        return self.sum_of_ranks + self.penalties

    def __lt__(self, other):
        if self.reject_count < other.reject_count:
            return True
        if self.reject_count > other.reject_count:
            return False
        return self.score < other.score

    def __eq__(self, other):
        return (self.reject_count == other.reject_count
                and self.score == other.score)

    def to_dict(self):
        return {'reject_count': self.reject_count,
                'sum_of_ranks': self.sum_of_ranks,
                'penalties': self.penalties,
                'score': self.score,
                'place': self.place,
                'input_ranks':
                    {k.id: (v[0], str(v[1]), v[2])
                     for k, v in self.input_ranks.items()}}


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition

    @expose('algobowl.templates.competition.rankings')
    @expose('json')
    def index(self, ground_truth=False):
        user = request.identity and request.identity['user']
        now = datetime.datetime.now()
        admin = user and user.admin
        comp = self.competition
        show_scores = admin or now >= comp.open_verification_begins

        if not admin and now < comp.output_upload_begins:
            flash("Rankings are not available yet", "info")
            redirect("/competition")

        if ground_truth and not admin:
            abort(403, "You do not have permission for this option")

        if ground_truth:
            verification_column = Output.ground_truth
        else:
            verification_column = case(
                [(Output.use_ground_truth, Output.ground_truth)],
                else_=Output.verification)

        open_verification = user and comp.open_verification_open

        groups = defaultdict(GroupEntry)
        ir_query = (
            DBSession.query(Input, Group, Output, verification_column)
                     .join(Input.outputs)
                     .join(Output.group)
                     .filter(Group.competition_id == comp.id)
                     .filter(Output.active == True)
                     .order_by(Input.group_id,
                               verification_column
                               == VerificationStatus.rejected,
                               Output.score))

        inputs = []
        last_iput = None
        for iput, ogroup, output, verif in ir_query:
            if iput is not last_iput:
                inputs.append(iput)
                potential_rank = 1
                last_rank = 0
                last_score = None
            shown_score = output.score
            shown_output = output
            if not show_scores:
                shown_score = None
                shown_output = None
            if verif is VerificationStatus.rejected:
                rank = None
                shown_score = None
            elif output.score == last_score:
                rank = last_rank
            else:
                rank = potential_rank
            groups[ogroup].input_ranks[iput] = ScoreTuple(
                shown_score, verif, rank, shown_output)
            if verif is VerificationStatus.rejected:
                groups[ogroup].reject_count += 1
            else:
                groups[ogroup].sum_of_ranks += rank

            # add accepted resubmissions to penalty
            if verif is VerificationStatus.accepted and not output.original:
                groups[ogroup].penalties += 1

            potential_rank += 1
            last_iput = iput
            last_rank = rank
            last_score = output.score

        # no submission? this adds to reject count
        for group in groups.values():
            for iput in inputs:
                if iput not in group.input_ranks.keys():
                    group.reject_count += 1

        # add open verification protest rejections to penalty
        rprotests = (DBSession.query(Protest)
                              .filter(Protest.accepted == False)
                              .join(Protest.submitter)
                              .filter(Group.competition_id == comp.id))
        for protest in rprotests:
            # technically, a group which failed to submit anything
            # COULD protest... but this case is unlikely ;)
            if protest.submitter in groups.keys():
                groups[protest.submitter].penalties += 1

        # compute places for groups
        for this_ent in groups.values():
            for other_ent in groups.values():
                if other_ent < this_ent:
                    this_ent.place += 1

        if request.response_type == 'application/json':
            return {'status': 'success',
                    'groups': {k.id: v.to_dict() for k, v in groups.items()}}
        else:
            return {'groups': groups,
                    'competition': comp,
                    'inputs': inputs,
                    'ground_truth': ground_truth,
                    'open_verification': open_verification}

    @expose('algobowl.templates.competition.ov')
    def ov(self, output_id):
        output = DBSession.query(Output).get(int(output_id))
        if output.group.competition_id != self.competition.id:
            abort(404)
        if not output.active:
            abort(404, "This output is no longer active.")
        user = request.identity and request.identity['user']
        if user:
            group = (DBSession.query(Group)
                              .filter(Group.competition_id
                                      == self.competition.id)
                              .filter(Group.users.any(id=user.id))
                              .first())
        else:
            group = None
        message = request.POST.get('message')
        if group and message:
            if output.use_ground_truth:
                abort(403, "The instructor has already reviewed this output.")

            output.use_ground_truth = True
            protest = Protest(
                message=message,
                accepted=output.verification != output.ground_truth,
                submitter=group,
                output=output)

            DBSession.add(output)
            DBSession.add(protest)

            flash('Your protest has been submitted.', 'success')

        return {'output': output, 'group': group,
                'competition': self.competition}

    @expose()
    def all_inputs(self):
        user = request.identity and request.identity['user']
        now = datetime.datetime.now()
        comp = self.competition
        if not (user and user.admin) and now < comp.output_upload_begins:
            abort(403, "Input downloading is not available until the output"
                       " upload stage begins.")
        f = BytesIO()
        archive = zipfile.ZipFile(f, mode='w')
        inputs = (DBSession.query(Input)
                           .join(Input.group)
                           .filter(Group.competition_id == comp.id))
        for iput in inputs:
            archive.writestr(
                'inputs/{}'.format(iput.data.filename),
                iput.data.file.read())
        archive.close()
        f.seek(0)
        response.content_type = 'application/zip'
        return f.read()


class CompetitionsController(BaseController):
    @expose()
    def _lookup(self, comp_id, *args):
        try:
            comp_id = int(comp_id)
        except ValueError:
            abort(404, "Invalid input for competition id")
        competition = DBSession.query(Competition).get(comp_id)
        if not competition:
            abort(404, "No such competition")

        return CompetitionController(competition), args

    @expose('algobowl.templates.competition.list')
    def index(self):
        now = datetime.datetime.now()
        comps = (DBSession.query(Competition)
                          .filter(Competition.input_upload_begins <= now)
                          .order_by(Competition.input_upload_ends))
        active, historical = [], []
        for c in comps:
            (active if c.active else historical).append(c)
        return {'active': active, 'historical': historical}
