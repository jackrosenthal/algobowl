import dataclasses
import pathlib

import click
import requests

import algobowl.cli.config as cfg
import algobowl.cli.formatter as fmt
from algobowl.cli import admin, auth, group, problem


@dataclasses.dataclass
class CommandContext:
    config: cfg.CLIConfig = None
    session: requests.Session = None
    formatter: fmt.JsonFormatter = dataclasses.field(default_factory=fmt.TableFormatter)
    selected_group: int = -1


@click.group(help="The AlgoBOWL CLI")
@click.option("--config", type=pathlib.Path, help="Config file to use")
@click.option("--server", help="Server to use")
@click.option("--json", is_flag=True, help="Use JSON output instead of tables")
@click.option(
    "--sudo/--no-sudo",
    type=bool,
    default=False,
    help=(
        "Grant admin permissions on the server.  Doesn't do anything unless "
        "your account is actually an admin."
    ),
)
@click.pass_context
def main(ctx, server, config, json, sudo):
    ctx.ensure_object(CommandContext)

    if not config:
        config = cfg.get_default_config_path()

    ctx.obj.config = cfg.CLIConfig(path=config, server=server)
    ctx.obj.session = auth.get_session(ctx.obj.config, sudo=sudo)
    if json:
        ctx.obj.formatter = fmt.JsonFormatter()
    ctx.call_on_close(ctx.obj.config.write)


main.add_command(auth.auth)
main.add_command(cfg.config)
main.add_command(group.group)
main.add_command(admin.admin)
main.add_command(problem.problem)


if __name__ == "__main__":
    main()
