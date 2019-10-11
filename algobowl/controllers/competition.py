import zipfile
import datetime
from io import BytesIO
from statistics import mean, StatisticsError
from collections import namedtuple, defaultdict
from recordclass import recordclass
from tg import expose, abort, request, response, flash, redirect, require
from tg.predicates import has_permission
from sqlalchemy.sql.expression import case
from algobowl.lib.base import BaseController
from algobowl.lib.logoutput import logoutput
from algobowl.model import (DBSession, Competition, Input, Output, Group,
                            VerificationStatus, Protest, Evaluation)

__all__ = ['CompetitionsController', 'CompetitionController']


ScoreTuple = namedtuple('ScoreTuple',
                        ['score', 'verification', 'rank', 'output'])

GradingTuple = recordclass('GradingTuple',
                           ['rankings', 'verification', 'input',
                            'contributions', 'evaluations'])

GradingContributionTuple = recordclass(
    'GradingContributionTuple',
    ['participation', 'verification', 'input_difficulty', 'ranking'],
    defaults=[0, 0, 0, 0])

GradingInputTuple = recordclass(
    'GradingInputTuple',
    ['scores_l', 'scores_s'])

GradingVerificationTuple = recordclass(
    'GradingVerificationTuple',
    ['correct', 'false_positives', 'false_negatives'],
    defaults=[0, 0, 0])

CompInfoTuple = recordclass(
    'CompInfoTuple',
    ['inputs', 'best_score', 'worst_score', 'best_input_difference'])


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

    @property
    def adj_score(self):
        """
        Score used for grading: each rejection is assumed
        to count as one mean score of the group.
        """
        if not self.reject_count:
            return self.score

        try:
            return (self.sum_of_ranks
                    + self.penalties
                    + self.reject_count * mean(
                        s.rank
                        for s in self.input_ranks.values()
                        if s.rank is not None))
        except StatisticsError:
            return self.reject_count ** 2

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
        show_scores = admin or (comp.open_verification_begins
                                and now >= comp.open_verification_begins)

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

    @expose('algobowl.templates.competition.grade')
    @require(has_permission('admin'))
    def grade(self):
        rankings = self.index(ground_truth=True)

        groups = {
            k: GradingTuple(
                v,
                GradingVerificationTuple(),
                GradingInputTuple([], set()),
                GradingContributionTuple(),
                defaultdict(dict))
            for k, v in rankings['groups'].items()}

        compinfo = CompInfoTuple(len(rankings['inputs']), float("inf"), 0, 0)

        for group, gt in groups.items():
            # compute verification correctness
            q = (DBSession.query(Output)
                          .filter(Output.original == True)
                          .join(Output.input)
                          .filter(Input.group_id == group.id))
            for oput in q:
                if oput.verification == oput.ground_truth:
                    gt.verification.correct += 1
                elif oput.verification == VerificationStatus.accepted:
                    gt.verification.false_positives += 1
                else:
                    gt.verification.false_negatives += 1

            # compute input unique ranks
            for iput, st in gt.rankings.input_ranks.items():
                if st.rank is None:
                    groups[iput.group].input.scores_s.add('R{}'.format(id(st)))
                else:
                    groups[iput.group].input.scores_s.add(st.score)
                groups[iput.group].input.scores_l.append(st.score)

            adj_score = gt.rankings.adj_score
            if adj_score < compinfo.best_score:
                compinfo.best_score = adj_score
            if adj_score > compinfo.worst_score:
                compinfo.worst_score = adj_score

        compinfo.best_input_difference = max(
            len(g.input.scores_s) for g in groups.values())

        for group, gt in groups.items():
            gt.contributions.ranking = (
                max(16 - (gt.rankings.adj_score / compinfo.best_score), 0))
            gt.contributions.verification = (
                gt.verification.correct / sum(gt.verification) * 5
            ) if any(gt.verification) else 0
            gt.contributions.participation = (
                (compinfo.inputs - gt.rankings.reject_count)
                / compinfo.inputs
                * 70)
            gt.contributions.input_difficulty = (
                7 + len(gt.input.scores_s) / compinfo.best_input_difference * 3
            ) if gt.input.scores_l else 0

        for group, gt in groups.items():
            for from_member in group.users:
                q = (DBSession
                     .query(Evaluation, Evaluation.score)
                     .filter(Evaluation.group_id == group.id)
                     .filter(Evaluation.from_student_id == from_member.id)
                     .all())
                evals = {e.to_student: s for e, s in q}
                for to_member in group.users:
                    if to_member not in evals.keys():
                        evals[to_member] = 1.0
                for to_member, score in evals.items():
                    gt.evaluations[to_member][from_member] = (
                        score / sum(evals.values()))

        return {'groups': groups, 'competition': self.competition}

    @logoutput
    @require(has_permission('admin'))
    def reverify(self):
        verif_mod = self.competition.output_verifier.module

        changes = 0
        for group in self.competition.groups:
            if group.input:
                for output in group.input.outputs:
                    old_status = output.ground_truth
                    try:
                        verif_mod.verify(group.input.data.file,
                                         output.data.file)
                    except verif_mod.VerificationError as e:
                        output.ground_truth = VerificationStatus.rejected
                        print("{} rejected because: {}".format(output, e))
                    except Exception as e:
                        output.ground_truth = VerificationStatus.waiting
                        print("Verifier module failed on {}: {}".format(
                            output, e))
                    else:
                        output.ground_truth = VerifcationStatus.accepted
                    if old_status != output.ground_truth:
                        print("{} changed ground truth from {} to {}".format(
                            output, old_status, output.ground_truth))
                        changes += 1
        DBSession.flush()
        print("{} ground truths changed".format(changes))

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
                          .order_by(Competition.input_upload_ends))
        active, historical = [], []
        for c in comps:
            (active if c.end >= now else historical).append(c)
        return {'active': active, 'historical': historical}
