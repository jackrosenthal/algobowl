import dataclasses
import os
import sys
from pathlib import Path

import click
import toml

import algobowl.lib.problem as problemlib
from algobowl.cli import formatter


def get_default_config_path():
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if not xdg_config_home:
        xdg_config_home = Path.home() / ".config"
    return Path(xdg_config_home) / "algobowl" / "cli.toml"


def _ensure_protocol(server):
    if server.startswith("http://") or server.startswith("https://"):
        return server
    if server.endswith(":8080"):
        return f"http://{server}"
    return f"https://{server}"


@dataclasses.dataclass
class CLIConfig:
    path: Path
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

    def load_problem(self, name):
        def _propose_paths():
            path = Path(name)
            yield path
            if path.name == "problem.py":
                yield path.parent
            defaults = self.config.get("defaults", {})
            for search_path in defaults.get("problem_search_paths", []):
                yield Path(search_path) / name

        for path in _propose_paths():
            if path.is_dir() and (path / "problem.py").is_file():
                return problemlib.Problem(path)

        raise FileNotFoundError(f"Unable to find problem {name!r}")


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


@config.command()
@click.argument("path", type=Path)
@click.pass_obj
def add_problem_search_path(cli, path):
    if not path.is_dir():
        formatter.err(f"Path must be a directory: {path}")
        sys.exit(1)
    defaults = cli.config.config.setdefault("defaults", {})
    paths = defaults.setdefault("problem_search_paths", [])
    paths.append(str(path.resolve()))
