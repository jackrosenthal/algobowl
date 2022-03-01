import click

import algobowl.cli.auth as auth


def get_active_groups(cli):
    r = cli.session.get(cli.config.get_url("/group.json"))
    auth.check_response(r)
    data = r.json()
    return data["groups"]


@click.group(help="Your Group")
def group():
    pass


@group.command(help="List all active groups you're a member of")
@click.pass_obj
def list(cli):
    groups = get_active_groups(cli)
    cli.formatter.dump_table(
        groups,
        filter_keys=["id", "name", "competition_id", "incognito"],
    )
