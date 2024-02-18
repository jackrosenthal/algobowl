import datetime
import io
import random

import tg
from depot.io.utils import FileIntent

import algobowl.lib.base as base
import algobowl.lib.problem as problemlib
import algobowl.model as model


def get_user(username):
    user = (
        model.DBSession.query(model.User)
        .filter(model.User.username == username)
        .one_or_none()
    )
    if user:
        return user

    mpapi = tg.request.environ["repoze.who.plugins"]["mpapi"]
    return mpapi.new_user_by_username(username)


def generate_default_input(
    problem: problemlib.Problem,
    group: model.Group,
) -> model.Input:
    reformatted_contents = io.StringIO()
    iput = problem.generate_input(random.SystemRandom())
    iput.write(reformatted_contents)

    input_file = FileIntent(
        io.BytesIO(reformatted_contents.getvalue().encode("utf-8")),
        f"input_group{group.id}.txt",
        "application/octet-stream",
    )
    result = model.Input(data=input_file, group=group, is_default=True)
    model.DBSession.add(result)
    return result


class SetupController(base.BaseController):
    allow_only = tg.predicates.has_permission("admin")

    @tg.expose("json")
    def create_group(
        self,
        competition_id=None,
        name=None,
        users="",
        incognito=False,
        benchmark=False,
    ):
        competition = (
            model.DBSession.query(model.Competition)
            .filter(model.Competition.id == int(competition_id))
            .one()
        )
        problem = problemlib.load_problem(competition)
        users = [get_user(username) for username in users.split(",")]
        group = model.Group(
            users=users,
            competition=competition,
            name=name or None,
            incognito=bool(incognito),
            benchmark=bool(benchmark),
        )
        model.DBSession.add(group)
        group.input = generate_default_input(problem=problem, group=group)
        model.DBSession.flush()
        return {"group_id": group.id}

    @tg.expose("json")
    def setup_competition(
        self,
        name=None,
        problem=None,
        input_upload_ends=None,
        output_upload_hours=48,
        verification_hours=24,
        resolution_hours=24,
        ov_hours=72,
    ):
        input_upload_ends_dt = datetime.datetime.fromisoformat(input_upload_ends)
        output_upload_delta = datetime.timedelta(hours=int(output_upload_hours))
        verification_delta = datetime.timedelta(hours=int(verification_hours))
        resolution_delta = datetime.timedelta(hours=int(resolution_hours))
        ov_delta = datetime.timedelta(hours=int(ov_hours))

        output_upload_ends = input_upload_ends_dt + output_upload_delta
        verification_ends = output_upload_ends + verification_delta
        resolution_ends = verification_ends + resolution_delta
        ov_ends = resolution_ends + ov_delta

        competition = model.Competition(
            name=name,
            problem=problem,
            allow_custom_team_names=True,
            input_upload_begins=input_upload_ends_dt - datetime.timedelta(weeks=2),
            input_upload_ends=input_upload_ends_dt,
            output_upload_begins=input_upload_ends_dt,
            output_upload_ends=output_upload_ends,
            verification_begins=output_upload_ends,
            verification_ends=verification_ends,
            resolution_begins=verification_ends,
            resolution_ends=resolution_ends,
            open_verification_begins=resolution_ends,
            open_verification_ends=ov_ends,
            evaluation_begins=resolution_ends,
            evaluation_ends=ov_ends,
        )
        model.DBSession.add(competition)
        model.DBSession.flush()

        return {"competition_id": competition.id}
