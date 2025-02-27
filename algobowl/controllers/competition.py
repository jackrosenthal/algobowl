from __future__ import annotations

import dataclasses
import datetime
from collections import defaultdict
from io import StringIO

from sqlalchemy.sql.expression import case
from tg import abort, expose, flash, redirect, request, require, response
from tg.predicates import has_permission

import algobowl.lib.problem as problemlib
from algobowl.lib.base import BaseController
from algobowl.lib.logoutput import logoutput
from algobowl.model import (
    Competition,
    DBSession,
    Evaluation,
    Group,
    Input,
    Output,
    Protest,
    VerificationStatus,
)

__all__ = ["CompetitionController", "CompetitionsController"]


@dataclasses.dataclass
class ScoreTuple:
    score: str | None
    verification: VerificationStatus
    rank: int | None
    output: Output | None
    vdiffer: bool


@dataclasses.dataclass
class GradingTuple:
    rankings: GroupEntry
    fleet: int
    verification: GradingVerificationTuple
    input_ones: int
    contributions: GradingContributionTuple
    evaluations: defaultdict[dict]


@dataclasses.dataclass
class GradingContributionTuple:
    participation: float | int = 0
    verification: float | int = 0
    input_submitted: int = 0
    input_difficulty: int = 0
    ranking: int | float = 0

    def __iter__(self):
        yield from dataclasses.asdict(self).values()


@dataclasses.dataclass
class GradingVerificationTuple:
    correct: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    def __iter__(self):
        yield from dataclasses.asdict(self).values()


@dataclasses.dataclass
class CompetitionYearTuple:
    year: int
    competitions: list[Competition]


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
        to count as the number of groups.
        """
        if not self.reject_count:
            return self.score

        num_inputs = len(self.input_ranks)
        if not num_inputs:
            num_inputs = 9999

        return self.sum_of_ranks + self.penalties + self.reject_count * num_inputs

    def __lt__(self, other):
        if self.reject_count < other.reject_count:
            return True
        if self.reject_count > other.reject_count:
            return False
        return self.score < other.score

    def __eq__(self, other):
        return self.reject_count == other.reject_count and self.score == other.score


def compute_rankings_grade(gt: GradingTuple, fleet_num: int, fleet: int) -> int | float:
    place_in_fleet = 0
    last_adj_score = fleet[0].rankings.adj_score
    for i, other_gt in enumerate(fleet):
        if other_gt.rankings.adj_score != last_adj_score:
            place_in_fleet = i
            last_adj_score = other_gt.rankings.adj_score
        if other_gt is gt:
            break
    if len(fleet) == 1:
        return 5 + fleet_num * 5
    return (place_in_fleet / (len(fleet) - 1)) * 5 + fleet_num * 5


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition
        super().__init__()

    @expose("algobowl.templates.competition.rankings")
    @expose("json")
    def index(self, ground_truth=False, incognito=False):
        user = request.identity and request.identity["user"]
        now = datetime.datetime.now()
        comp = self.competition
        problem = problemlib.load_problem(comp)
        show_scores = request.environ["is_admin"] or comp.open_verification_open
        if user:
            my_groups = (
                DBSession.query(Group).filter(Group.competition_id == comp.id).all()
            )
            # non-sql filter, bleh
            my_groups = [g for g in my_groups if user in g.users]
        else:
            my_groups = []

        show_input_downloads = request.environ["is_admin"] or not comp.archived
        show_incognito_option = request.environ["is_admin"] or any(
            g.incognito for g in my_groups
        )

        if show_incognito_option:
            incognito_teams = (
                DBSession.query(Group)
                .filter(Group.competition_id == comp.id)
                .filter(Group.incognito == True)
                .all()
            )
        else:
            incognito = False
            incognito_teams = []

        if not request.environ["is_admin"] and now < comp.output_upload_begins:
            abort(403, "Rankings for this competition are not available yet")

        if ground_truth and not request.environ["is_admin"]:
            abort(403, "You do not have permission for this option")

        if ground_truth:
            verification_column = Output.ground_truth
        else:
            verification_column = case(
                [(Output.use_ground_truth, Output.ground_truth)],
                else_=Output.verification,
            )

        open_verification = user and comp.open_verification_open

        problem_module = problem.get_module()
        score_sort = {
            problemlib.RankSort.minimization: Output.score.asc(),
            problemlib.RankSort.maximization: Output.score.desc(),
        }[problem_module.Output.rank_sort]

        groups = defaultdict(GroupEntry)
        ir_query = (
            DBSession.query(Input, Group, Output, verification_column)
            .join(Input.outputs)
            .join(Output.group)
            .filter(Group.competition_id == comp.id)
            .filter(Output.active == True)
            .order_by(
                Input.group_id,
                verification_column == VerificationStatus.rejected,
                score_sort,
            )
        )

        inputs = []
        last_iput = None
        accurate_count = 0
        total_count = 0
        for iput, ogroup, output, verif in ir_query:
            if not incognito and ogroup.incognito:
                continue
            if iput is not last_iput:
                inputs.append(iput)
                potential_rank = 1
                last_rank = 0
                last_score = None
            shown_score = None
            shown_output = None
            if show_scores:
                shown_score = problem_module.Output.repr_score(output.score)
                shown_output = output
            if verif is VerificationStatus.rejected:
                rank = None
                shown_score = None
            elif output.score == last_score:
                rank = last_rank
            else:
                rank = potential_rank

            vdiffer = False
            if ground_truth:
                if (
                    output.use_ground_truth
                    or output.verification == output.ground_truth
                ):
                    accurate_count += 1
                else:
                    vdiffer = True

            groups[ogroup].input_ranks[iput] = ScoreTuple(
                shown_score, verif, rank, shown_output, vdiffer
            )
            if verif is VerificationStatus.rejected:
                groups[ogroup].reject_count += 1
            else:
                groups[ogroup].sum_of_ranks += rank

            # add accepted resubmissions to penalty
            if verif is VerificationStatus.accepted and not output.original:
                groups[ogroup].penalties += 1

            total_count += 1
            potential_rank += 1
            last_iput = iput
            last_rank = rank
            last_score = output.score

        # no submission? this adds to reject count
        for group in groups.values():
            for iput in inputs:
                if iput not in group.input_ranks:
                    group.reject_count += 1

        # add open verification protest rejections to penalty
        rprotests = (
            DBSession.query(Protest)
            .filter(Protest.accepted == False)
            .join(Protest.submitter)
            .filter(Group.competition_id == comp.id)
        )
        for protest in rprotests:
            # technically, a group which failed to submit anything
            # COULD protest... but this case is unlikely ;)
            if protest.submitter in groups:
                groups[protest.submitter].penalties += 1

        # compute places for groups
        for this_ent in groups.values():
            for other_ent in groups.values():
                if other_ent < this_ent:
                    this_ent.place += 1

        if request.response_type == "application/json":
            return {
                "status": "success",
                "groups": [
                    {
                        "group_name": group.name,
                        "reject_count": rankings.reject_count,
                        "sum_of_ranks": rankings.sum_of_ranks,
                        "penalties": rankings.penalties,
                        "score": rankings.score,
                        "place": rankings.place,
                        "input_ranks": [
                            {
                                "group_id": k.group.id,
                                "score": v.score,
                                "verification": str(v.verification),
                                "rank": v.rank,
                            }
                            for k, v in rankings.input_ranks.items()
                        ],
                    }
                    for group, rankings in groups.items()
                ],
            }
        return {
            "groups": groups,
            "my_groups": my_groups,
            "competition": comp,
            "inputs": inputs,
            "admin": request.environ["is_admin"],
            "incognito": incognito,
            "show_incognito_option": show_incognito_option,
            "incognito_teams": incognito_teams,
            "show_input_downloads": show_input_downloads,
            "ground_truth": ground_truth,
            "verification_accuracy": (
                0 if not total_count else (accurate_count / total_count)
            ),
            "open_verification": open_verification,
        }

    @expose("algobowl.templates.competition.grade")
    @require(has_permission("admin"))
    def grade(self):
        rankings = self.index(ground_truth=True, incognito=False)

        def new_gt(rankings_entry):
            return GradingTuple(
                rankings=rankings_entry,
                fleet=0,
                verification=GradingVerificationTuple(),
                input_ones=0,
                contributions=GradingContributionTuple(),
                evaluations=defaultdict(dict),
            )

        groups = {k: new_gt(v) for k, v in rankings["groups"].items()}

        num_inputs = len(rankings["inputs"])
        benchmark_groups = []

        # in the case a group submitted an input but has no outputs
        # uploaded yet, they won't be in groups as they are off the
        # rankings table. in this case, we need to make a
        # GradingTuples for them now.
        for group in self.competition.groups:
            if group.incognito:
                groups.pop(group, None)
                continue
            if group.benchmark:
                benchmark_groups.append(groups[group])
                groups.pop(group, None)
                continue
            if group not in groups:
                rankings_entry = GroupEntry()
                # If they submitted nothing, then everything is a "reject"
                rankings_entry.reject_count = num_inputs
                groups[group] = new_gt(rankings_entry)

        benchmark_groups.sort(key=lambda gt: -gt.rankings.adj_score)
        fleets = [[] for _ in range(len(benchmark_groups) + 1)]

        for group, gt in groups.items():
            # compute verification correctness
            q = (
                DBSession.query(Output)
                .filter(Output.original == True)
                .join(Output.input)
                .filter(Input.group_id == group.id)
            )
            for oput in q:
                if oput.verification == oput.ground_truth:
                    gt.verification.correct += 1
                elif oput.verification == VerificationStatus.accepted:
                    gt.verification.false_positives += 1
                else:
                    gt.verification.false_negatives += 1

            # Compute input difficulty
            for iput, st in gt.rankings.input_ranks.items():
                if iput.group.incognito or iput.group.benchmark:
                    continue
                if st.rank == 1:
                    groups[iput.group].input_ones += 1

            gt.fleet = 0
            for bench_gt in benchmark_groups:
                if gt.rankings.adj_score <= bench_gt.rankings.adj_score:
                    gt.fleet += 1
            fleets[gt.fleet].append(gt)

        for fleet in fleets:
            fleet.sort(key=lambda gt: -gt.rankings.adj_score)

        for group, gt in groups.items():
            gt.contributions.ranking = compute_rankings_grade(
                gt, gt.fleet, fleets[gt.fleet]
            )
            gt.contributions.verification = (
                (gt.verification.correct / sum(gt.verification) * 20)
                if any(gt.verification)
                else 0
            )
            if num_inputs:
                gt.contributions.participation = (
                    (num_inputs - gt.rankings.reject_count) / num_inputs * 50
                )
            else:
                gt.contributions.participation = 0
            if group.input and not group.input.is_default:
                gt.contributions.input_submitted = 5
                gt.contributions.input_difficulty = max(
                    10 - (gt.input_ones - 1),
                    0,
                )
            else:
                gt.contributions.input_submitted = 0
                gt.contributions.input_difficulty = 0

        for group, gt in groups.items():
            for from_member in group.users:
                q = (
                    DBSession.query(Evaluation, Evaluation.score)
                    .filter(Evaluation.group_id == group.id)
                    .filter(Evaluation.from_student_id == from_member.id)
                    .all()
                )
                evals = {e.to_student: s for e, s in q}
                for to_member in group.users:
                    if to_member not in evals:
                        evals[to_member] = 1.0
                for to_member, score in evals.items():
                    gt.evaluations[to_member][from_member] = score / sum(evals.values())

        return {"groups": groups, "competition": self.competition}

    @logoutput
    @require(has_permission("admin"))
    def reverify(self):
        problem = problemlib.load_problem(self.competition)

        changes = 0
        for group in self.competition.groups:
            if group.input:
                for output in group.input.outputs:
                    old_status = output.ground_truth
                    input_file = StringIO(group.input.data.file.read().decode("utf-8"))
                    output_file = StringIO(output.data.file.read().decode("utf-8"))
                    try:
                        problem.verify_output(input_file, output_file)
                    except problemlib.VerificationError as e:
                        output.ground_truth = VerificationStatus.rejected
                        print(f"{output} rejected because: {e}")
                    except Exception as e:
                        output.ground_truth = VerificationStatus.waiting
                        print(f"Verifier module failed on {output}: {e}")
                    else:
                        output.ground_truth = VerificationStatus.accepted
                    if old_status != output.ground_truth:
                        print(
                            f"{output} changed: {old_status} -> {output.ground_truth}"
                        )
                        changes += 1
        DBSession.flush()
        print(f"{changes} ground truths changed")

    @expose("algobowl.templates.competition.ov")
    def ov(self, output_id):
        if not (request.environ["is_admin"] or self.competition.open_verification_open):
            abort(403, "Open verification is not currently open.")
        output = DBSession.query(Output).get(int(output_id))
        if not output:
            abort(404, "Output does not exist.")
        if output.group.competition_id != self.competition.id:
            abort(404, "This output is not associated with this competition.")
        if not output.active:
            abort(404, "This output is no longer active.")
        user = request.identity and request.identity["user"]
        if user:
            group = (
                DBSession.query(Group)
                .filter(Group.competition_id == self.competition.id)
                .filter(Group.users.any(id=user.id))
                .first()
            )
        else:
            group = None

        problem = problemlib.load_problem(self.competition)
        problem_module = problem.get_module()
        message = request.POST.get("message")
        if group and message:
            if output.use_ground_truth:
                abort(403, "The instructor has already reviewed this output.")

            output.use_ground_truth = True
            protest = Protest(
                message=message,
                accepted=output.verification != output.ground_truth,
                submitter=group,
                output=output,
            )

            DBSession.add(output)
            DBSession.add(protest)

            flash("Your protest has been submitted.", "success")

        return {
            "output": output,
            "score": problem_module.Output.repr_score(output.score),
            "group": group,
            "competition": self.competition,
        }

    @expose()
    def problem_statement(self):
        if not request.environ["is_admin"] and self.competition.archived:
            abort(
                403,
                "The problem statement is no longer available as the "
                "competition has been archived.",
            )
        problem = problemlib.load_problem(self.competition)
        response.content_type = "application/pdf"
        return problem.get_statement_pdf()


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

    @expose("algobowl.templates.competition.archive")
    def archive(self):
        now = datetime.datetime.now()
        comps = []
        for comp in (
            DBSession.query(Competition)
            .filter(Competition.open_verification_ends <= now)
            .order_by(Competition.input_upload_ends.desc())
        ):
            if not comps or comps[-1].year != comp.input_upload_ends.year:
                comps.append(CompetitionYearTuple(comp.input_upload_ends.year, [comp]))
            else:
                comps[-1].competitions.append(comp)

        return {"competitions": comps}

    @expose("algobowl.templates.competition.list")
    def index(self):
        now = datetime.datetime.now()
        comps = (
            DBSession.query(Competition)
            .filter(Competition.output_upload_begins <= now)
            .filter(Competition.open_verification_ends > now)
            .order_by(Competition.input_upload_ends)
            .all()
        )
        if len(comps) == 1:
            redirect(f"/competition/{comps[0].id}")
        return {"competitions": comps}
