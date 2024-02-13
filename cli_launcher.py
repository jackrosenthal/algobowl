#!/usr/bin/env python3

"""Launcher for AlgoBOWL CLI.

This is a small little launcher script for the AlgoBOWL CLI.  It launches the
CLI creating a Python virtual environment and installing it from GitHub.  The
launcher will update the CLI on startup every 24 hours.  By design, this has no
dependencies other than Python 3.8+ and is a single file.  You should be able to
"chmod +x" this script and put it in your PATH, or put it in your team's Git
repo for everyone on your team to use.

This launcher can be downloaded from:
https://raw.githubusercontent.com/jackrosenthal/algobowl/main/cli_launcher.py

All command line arguments are passed as-is to the real AlgoBOWL CLI.  It can
minimally be configured via environment variables:

- ALGOBOWL_VENV: Path to the virtual environment to use (by default, create one
  in the XDG cache directory).
- ALGOBOWL_FORCE_UPDATE: Set to 1 to force the launcher to re-build the virtual
  environment.
- ALGOBOWL_NO_UPDATE: Set to 1 to force the launcher to not update the virtual
  environment.
"""

import datetime
import os
import subprocess
import sys
import venv
from pathlib import Path

assert sys.version_info >= (3, 8), "AlgoBOWL CLI requires Python 3.8+"


def quiet_run(argv) -> None:
    """Run a command, staying quiet unless there's an error."""
    try:
        subprocess.run(
            argv,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed ({argv})!", file=sys.stderr)
        sys.stderr.write(e.stdout)
        raise


def get_cache_dir() -> Path:
    """Get the XDG-specified cache directory."""
    xdg_cache_home = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache_home:
        return Path(xdg_cache_home)
    return Path.home() / ".cache"


def get_venv_dir() -> Path:
    """Get the path to the virtual environment to use."""
    venv_dir = os.environ.get("ALGOBOWL_VENV")
    if venv_dir:
        return Path(venv_dir)

    return (
        get_cache_dir()
        / "algobowl"
        / f"venv-{sys.version_info.major}.{sys.version_info.minor}"
    )


def venv_cmd(executable: str) -> Path:
    """Get the path to a command in the virtual environment."""
    scripts_file = get_venv_dir() / "Scripts" / f"{executable}.exe"
    if scripts_file.exists():
        return scripts_file
    return get_venv_dir() / "bin" / executable


def build_venv() -> None:
    """Build the virtual environment."""
    venv.EnvBuilder(
        system_site_packages=False,
        clear=bool(os.environ.get("ALGOBOWL_FORCE_UPDATE")),
        symlinks=sys.platform != "win32",
        with_pip=True,
    ).create(get_venv_dir())
    quiet_run([venv_cmd("python"), "-m", "pip", "install", "--upgrade", "pip"])
    quiet_run([venv_cmd("python"), "-m", "pip", "install", "--upgrade", "algobowl"])


def update_venv() -> None:
    """Build the virtual environment if necessary."""
    if os.environ.get("ALGOBOWL_NO_UPDATE"):
        return
    update_file = get_venv_dir() / "UPDATE"
    force_update = os.environ.get("ALGOBOWL_FORCE_UPDATE")
    now = datetime.datetime.now()
    if not force_update and update_file.exists():
        last_update = datetime.datetime.fromisoformat(
            update_file.read_text(encoding="ascii")
        )
        required_update = last_update + datetime.timedelta(hours=24)
        if required_update > now:
            return
    build_venv()
    update_file.write_text(now.isoformat(), encoding="ascii")


def main():
    """The main function."""
    update_venv()
    sys.exit(subprocess.run([venv_cmd("algobowl")] + sys.argv[1:]).returncode)


if __name__ == "__main__":
    main()
