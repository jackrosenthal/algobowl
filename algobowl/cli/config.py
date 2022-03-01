import dataclasses
import os
import pathlib

import click
import toml


def get_default_config_path():
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if not xdg_config_home:
        xdg_config_home = pathlib.Path.home() / ".config"
    return pathlib.Path(xdg_config_home) / "algobowl" / "cli.toml"


def _ensure_protocol(server):
    if server.startswith("http://") or server.startswith("https://"):
        return server
    if server.endswith(":8080"):
        return f"http://{server}"
    return f"https://{server}"


@dataclasses.dataclass
class CLIConfig:
    path: pathlib.Path
    server: str = ""
    config: dict = dataclasses.field(default_factory=dict)
    orig_config: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if not self.path.is_file():
            return
        with open(self.path) as f:
            self.config = toml.load(f)

    def write(self):
        if self.config != self.orig_config:
            self.path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.path, "w") as f:
                toml.dump(self.config, f)

    def get_server(self):
        if self.server:
            return _ensure_protocol(self.server)
        default = self.config.get("defaults", {}).get("server")
        if default:
            return _ensure_protocol(default)
        return "https://mines.algobowl.org"

    def get_url(self, path):
        return f"{self.get_server()}{path}"

    def set_default_server(self, server):
        defaults = self.config.get("defaults", {})
        defaults["server"] = server
        self.config["defaults"] = defaults

    def get_server_config(self, key, default=None):
        server = self.get_server()
        server_config = self.config.get(server, {})
        return server_config.get(key, default)

    def set_server_config(self, key, value):
        server = self.get_server()
        self.config.setdefault(server, {})
        self.config[server][key] = value


@click.group(help="Get and set CLI configuration")
def config():
    pass


@config.command()
@click.pass_obj
def show(cli):
    cli.formatter.dump_config(cli.config.config)


@config.command()
@click.argument("server_url")
@click.pass_obj
def set_default_server(cli, server_url):
    cli.config.set_default_server(server_url)
