import base64
import getpass
import os
import platform
import sys
import urllib.parse

import click
import requests
import tabulate

import algobowl.lib.constants


def _style_cmd(text):
    return click.style(text, fg="cyan", bold=True)


def get_session(config):
    session = requests.Session()
    auth_token = config.get_server_config("access_token")
    if auth_token and len(auth_token) == 88:
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
    session.headers.update(
        {"X-AlgoBOWL-CLI-Compatible": str(algobowl.lib.constants.cli_compatible)},
    )
    return session


def get_tokens(cli):
    r = cli.session.get(cli.config.get_url("/pref/cli.json"))
    check_response(r)
    return r.json()["auth_tokens"]


def check_response(response):
    if response.status_code == requests.codes.unauthorized:
        click.echo("This command requires authentication.")
        click.echo(f"Run {_style_cmd('algobowl auth login')} to continue.")
        sys.exit(1)
    response.raise_for_status()


def generate_client_name():
    return f"{platform.system()} {getpass.getuser()}@{platform.node()}"


def generate_client_id():
    return base64.urlsafe_b64encode(os.urandom(66)).decode("ascii")


@click.group(help="Authentication")
def auth():
    pass


@auth.command(help="Connect this CLI to your account")
@click.pass_obj
def login(cli):
    client_name = generate_client_name()
    client_id = generate_client_id()
    params = urllib.parse.urlencode(
        {
            "client_name": client_name,
            "client_id": client_id,
        }
    )
    url = cli.config.get_url(f"/pref/cli?{params}")
    cli.config.set_server_config("access_token", client_id)
    click.echo("Open the following URL in your browser:")
    click.echo(f"    {url}")
    click.echo(f"Then, run {_style_cmd('algobowl auth whoami')} to verify.")


@auth.command(help="Show information about the current user")
@click.pass_obj
def whoami(cli):
    r = cli.session.get(cli.config.get_url("/pref/whoami.json"))
    check_response(r)
    cli.formatter.dump_table([r.json()])


@auth.command(help="Show registered clients")
@click.pass_obj
def list_clients(cli):
    cli.formatter.dump_table(get_tokens(cli))


@auth.command(help="Revoke a client token")
@click.option(
    "--token-id", type=int, help="Revoke a specific token (instead of this client's)"
)
@click.pass_obj
def logout(cli, token_id):
    if not token_id:
        tokens = get_tokens(cli)
        for token in tokens:
            if token["this_client"]:
                token_id = token["id"]
                break

    r = cli.session.get(
        cli.config.get_url("/pref/revoke_auth_token"),
        allow_redirects=False,
        params={"token_id": token_id},
    )
    check_response(r)
