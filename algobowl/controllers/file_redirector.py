import datetime
import re
from typing import Union

import tg

import algobowl.model as model


def input_redirector(group_id: str) -> model.Input:
    group_id = int(group_id)
    group = model.DBSession.query(model.Group).get(group_id)
    if not group:
        tg.abort(404, "No such group.")
    competition = group.competition

    user = tg.request.identity and tg.request.identity.get("user")
    is_admin = tg.request.environ["is_admin"]
    is_group_member = user in group.users
    file_is_public = datetime.datetime.now() >= competition.output_upload_begins

    if not file_is_public and not is_admin and group.input and group.input.is_default:
        tg.abort(403, "Default inputs are not downloadable until output upload begins.")

    if file_is_public or is_group_member or is_admin:
        if not group.input:
            tg.abort(404, "An input file has not been uploaded yet.")
        return group.input

    tg.abort(403, "You do not have access to this file at this time.")


def output_redirector(from_group_id: str, to_group_id: str) -> model.Output:
    from_group_id = int(from_group_id)
    to_group_id = int(to_group_id)
    output = (
        model.DBSession.query(model.Output)
        .join(model.Output.input)
        .filter(model.Input.group_id == to_group_id)
        .filter(model.Output.group_id == from_group_id)
        .filter(model.Output.active == True)
        .one()
    )
    if not output:
        tg.abort(404, "Output does not exist.")

    competition = output.group.competition
    user = tg.request.identity and tg.request.identity.get("user")
    is_admin = tg.request.environ["is_admin"]
    is_uploader = user in output.group.users
    is_verifier = user in output.input.group.users
    visible_to_verifier = datetime.datetime.now() >= competition.verification_begins
    file_is_public = competition.open_verification_open

    if (
        file_is_public
        or is_uploader
        or is_admin
        or (is_verifier and visible_to_verifier)
    ):
        return output

    tg.abort(403, "You do not have access to this file at this time.")


file_pattern_handlers = [
    (re.compile(r"input_group(\d+)"), input_redirector),
    (re.compile(r"output_from_(\d+)_to_(\d+)"), output_redirector),
]


def get_file(filename: str) -> Union[model.Input, model.Output]:
    for pattern, func in file_pattern_handlers:
        m = pattern.fullmatch(filename)
        if m:
            return func(*m.groups())

    tg.abort(404, "No handler found for filename.")
