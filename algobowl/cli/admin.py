import click

import algobowl.cli.auth as auth


def lookup_uid(cli, lookup):
    try:
        user_id = int(lookup)
    except ValueError:
        pass
    else:
        return user_id

    r = cli.session.get(cli.config.get_url(f"/api/user/{lookup}/info.json"))
    auth.check_response(r)
    data = r.json()
    return data["id"]


@click.group(help="Administration")
@click.pass_obj
def admin(cli):
    pass


@admin.command(name="create-group", help="Create a new group")
@click.option(
    "--incognito/--no-incognito", "-i", help="Enable if the group should be incognito"
)
@click.option("--name", "-n", type=str, help="Group Name")
@click.option(
    "--competition", "-c", type=int, help="Competition ID for this group", required=True
)
@click.option("--user", "-u", type=str, help="Add user", multiple=True)
@click.pass_obj
def create_group(cli, incognito, name, competition, user):
    user_ids = []
    for u in user:
        user_ids.append(str(lookup_uid(cli, u)))

    data = {"competition": str(competition), "users": user_ids}
    if incognito:
        data["incognito"] = "true"
    if name:
        data["name"] = name

    r = cli.session.post(cli.config.get_url("/admin/groups"), data=data)
    auth.check_response(r)
