import sys
import pathlib

import click

import algobowl.cli.auth as auth
import algobowl.cli.formatter as fmt


def get_active_groups(cli):
    r = cli.session.get(cli.config.get_url("/group.json"))
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


@group.command(name="list", help="List all active groups you're a member of")
@click.pass_obj
def list_(cli):
    groups = get_active_groups(cli)
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
        fmt.err(result["message"])
        sys.exit(1)


@input.command(help="Download your group's input")
@click.argument("output_file", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def download(cli, output_file):
    group_id = get_group_id(cli)
    r = cli.session.get(cli.config.get_url(f"/files/input_group{group_id}.txt"))
    auth.check_response(r)
    output_file.write(r.text)
