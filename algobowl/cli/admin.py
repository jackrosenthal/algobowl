import json
import sys
from typing import Iterable

import click
import requests

import algobowl.cli.formatter as fmt
from algobowl.lib import constants


def create_group(
    cli,
    competition_id: int,
    name: str = "",
    usernames: Iterable[str] = (),
    incognito: bool = False,
    benchmark: bool = False,
):
    data = {
        "competition_id": str(competition_id),
        "users": ",".join(usernames),
    }
    if name:
        data["name"] = name
    if incognito:
        data["incognito"] = "true"
    if benchmark:
        data["benchmark"] = "true"
    r = cli.session.post(cli.config.get_url("/setup/create_group.json"), data=data)
    r.raise_for_status()
    return r.json()


@click.group(
    help="Administration",
    epilog="Note: --sudo is implicit for this command group.",
)
@click.pass_obj
def admin(cli):
    # Give implicit --sudo for admin commands.
    cli.session.headers[constants.SUDO_HEADER] = "True"


@admin.command(help="Setup a new competition")
@click.option(
    "--name",
    type=str,
    help="Name of the competition",
    required=True,
)
@click.option(
    "--problem",
    type=str,
    help="Name of the problem",
    required=True,
)
@click.option(
    "--input-upload-due",
    type=str,
    help="Due date of input upload in ISO 8601 format (please include timezone!)",
    required=True,
)
@click.option(
    "--output-upload-hours",
    type=int,
    default=48,
    help="Number of hours for output upload.",
)
@click.option(
    "--verification-hours",
    type=int,
    default=24,
    help="Number of hours for verification.",
)
@click.option(
    "--resolution-hours",
    type=int,
    default=24,
    help="Number of hours for resolution.",
)
@click.option(
    "--ov-hours",
    type=int,
    default=72,
    help="Number of hours for open verification and evaluation.",
)
@click.pass_obj
def setup_competition(
    cli,
    name,
    problem,
    input_upload_due,
    output_upload_hours,
    verification_hours,
    resolution_hours,
    ov_hours,
):
    data = {
        "name": name,
        "problem": problem,
        "input_upload_ends": input_upload_due,
        "output_upload_hours": output_upload_hours,
        "verification_hours": verification_hours,
        "resolution_hours": resolution_hours,
        "ov_hours": ov_hours,
    }
    r = cli.session.post(cli.config.get_url("/setup/setup_competition.json"), data=data)
    r.raise_for_status()
    cli.formatter.dump_table([r.json()])


@admin.command(name="create-group", help="Create a new group")
@click.option(
    "--incognito/--no-incognito", "-i", help="Enable if the group should be incognito"
)
@click.option(
    "--benchmark/--no-benchmark",
    "-b",
    help="Enable if the group should be a benchmark group",
)
@click.option("--name", "-n", type=str, help="Group Name")
@click.option(
    "--competition", "-c", type=int, help="Competition ID for this group", required=True
)
@click.option("--user", "-u", type=str, help="Add user", multiple=True)
@click.pass_obj
def create_group_(cli, name, competition, user, incognito, benchmark):
    cli.formatter.dump_table(
        [
            create_group(
                cli,
                competition,
                name=name,
                usernames=user,
                incognito=incognito,
                benchmark=benchmark,
            )
        ]
    )


@admin.command(name="create-groups", help="Create groups from JSON file")
@click.option(
    "--competition", "-c", type=int, help="Competition ID for this group", required=True
)
@click.argument("json_file", type=click.Path(exists=True))
@click.pass_obj
def create_groups(cli, competition, json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        groups = json.load(f)
    failed_groups = []
    with click.progressbar(groups, label="Create groups") as bar:
        for group in bar:
            try:
                create_group(cli, competition, usernames=group)
            except (
                requests.exceptions.HTTPError,
                requests.exceptions.JSONDecodeError,
            ) as e:
                failed_groups.append((group, e))
    click.echo(
        f"Successfully created {len(groups) - len(failed_groups)} groups.", err=True
    )
    if failed_groups:
        fmt.err(f"Failed to create {len(failed_groups)} groups:")
        for group, exn in failed_groups:
            fmt.err(f"{json.dumps(group)}: {exn}")
        fmt.err("See the server logs for more information.")
        sys.exit(1)
