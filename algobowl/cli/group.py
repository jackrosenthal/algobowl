import pathlib
import re
import sys

import click

import algobowl.cli.auth as auth
import algobowl.cli.formatter as fmt


def get_active_groups(cli, params=None):
    r = cli.session.get(cli.config.get_url("/group.json"), params=params)
    auth.check_response(r)
    data = r.json()
    return data["groups"]


def get_group_id(cli):
    if cli.selected_group > 0:
        return cli.selected_group
    active_groups = get_active_groups(cli)
    if len(active_groups) == 1:
        return active_groups[0]["id"]
    if not active_groups:
        fmt.err("You aren't a member of any groups.")
    else:
        fmt.err("You're a member of multiple groups.")
        fmt.err("Pass --group-id to manually select a group.")
        fmt.err(
            f"Hint: Run {fmt.cmd('algobowl group list')} to show your active groups."
        )
    sys.exit(1)


@click.group(help="Your Group")
@click.option("--group-id", type=int, help="Select group")
@click.pass_obj
def group(cli, group_id):
    if group_id:
        cli.selected_group = group_id


@group.command(name="list", help="List groups")
@click.option("--inactive/--no-inactive", help="Include inactive groups")
@click.option(
    "--non-member/--no-non-member",
    help="(Admin only) Include groups you're not a member of",
)
@click.option("--competition", type=int, help="Only show groups for this competition")
@click.pass_obj
def list_(cli, inactive, non_member, competition):
    params = {}
    if inactive:
        params["list_inactive"] = True
    if non_member:
        params["list_non_member"] = True
    if competition:
        params["competition_id"] = competition
    groups = get_active_groups(cli, params=params)
    cli.formatter.dump_table(
        groups,
        filter_keys=["id", "name", "competition_id", "incognito"],
    )


@group.command(help="Set your team name")
@click.argument("team_name")
@click.pass_obj
def set_team_name(cli, team_name):
    group_id = get_group_id(cli)
    r = cli.session.post(
        cli.config.get_url(f"/group/{group_id}/input_upload"),
        data={
            "team_name": team_name,
        },
    )
    auth.check_response(r)


@group.group(help="Upload and see your group's input")
def input():
    pass


@input.command(help="Upload your group's input")
@click.argument("file_path", type=pathlib.Path)
@click.pass_obj
def upload(cli, file_path):
    group_id = get_group_id(cli)
    with open(file_path, "rb") as f:
        r = cli.session.post(
            cli.config.get_url(f"/group/{group_id}/input_upload_api"),
            files={"input_upload": f},
        )
    auth.check_response(r)
    result = r.json()
    if result["status"] != "success":
        fmt.err(result["msg"])
        sys.exit(1)


@input.command(help="Download your group's input")
@click.argument("output_file", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def download(cli, output_file):
    group_id = get_group_id(cli)
    r = cli.session.get(cli.config.get_url(f"/files/input_group{group_id}.txt"))
    auth.check_response(r)
    output_file.write(r.text)


@group.group(help="Upload and view outputs")
@click.option(
    "--to-group-id",
    type=int,
    help=(
        "Manually specify the group to submit to (by default, infer from the file name)"
    ),
)
@click.pass_obj
def output(cli, to_group_id):
    cli.to_group_id = to_group_id


def infer_group_from_path(file_path):
    matches = re.findall(r"\d+", file_path.name)
    if not matches:
        fmt.err(
            "Unable to infer the group id from file name.  "
            "Pass --to-group-id to specify manually."
        )
        sys.exit(1)
    return int(matches[-1])


@output.command(help="Upload output")
@click.argument("file_path", type=pathlib.Path)
@click.pass_obj
def upload(cli, file_path):
    from_group_id = get_group_id(cli)
    to_group_id = cli.to_group_id
    if not to_group_id:
        to_group_id = infer_group_from_path(file_path)
    with open(file_path, "rb") as f:
        r = cli.session.post(
            cli.config.get_url(f"/group/{from_group_id}/submit_output"),
            data={"to_group": to_group_id},
            files={"output_file": f},
        )
    auth.check_response(r)
    result = r.json()
    if result["status"] != "success":
        fmt.err(result["msg"])
        sys.exit(1)


@output.command(help="Download output")
@click.argument("file_path", type=pathlib.Path)
@click.pass_obj
def download(cli, file_path):
    from_group_id = get_group_id(cli)
    to_group_id = cli.to_group_id
    if not to_group_id:
        to_group_id = infer_group_from_path(file_path)
    r = cli.session.get(
        cli.config.get_url(f"/files/output_from_{from_group_id}_to_{to_group_id}.txt"),
    )
    auth.check_response(r)
    file_path.write_text(r.text)


@output.command(name="list", help="List outputs this group (will) provide")
@click.pass_obj
def output_list(cli):
    group_id = get_group_id(cli)
    r = cli.session.get(
        cli.config.get_url(f"/group/{group_id}/output_upload_list_api.json"),
    )
    auth.check_response(r)
    cli.formatter.dump_table(r.json()["outputs"])


@group.group(help="Preform verifications")
@click.pass_obj
def verification(cli):
    pass


@verification.command(name="list", help="Show verifications")
@click.pass_obj
def verification_list(cli):
    group_id = get_group_id(cli)
    r = cli.session.get(
        cli.config.get_url(f"/group/{group_id}/verification_data_v2.json"),
    )
    auth.check_response(r)
    cli.formatter.dump_table(r.json()["verifications"])
