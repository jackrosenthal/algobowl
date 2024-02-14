#!/usr/bin/env python3

"""Write the VERSION file and push to the release branch."""

from __future__ import annotations

import dataclasses
import datetime
import logging
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION_FILE = HERE / "VERSION"


def run(argv, **kwargs) -> subprocess.CompletedProcess:
    kwargs.setdefault("cwd", HERE)
    kwargs.setdefault("check", True)
    kwargs.setdefault("encoding", "utf-8")
    logging.info("Run command: %s", " ".join(shlex.quote(x) for x in argv))
    return subprocess.run(argv, **kwargs)


@dataclasses.dataclass(frozen=True)
class Version:
    year: int
    month: int
    day: int
    rel: int = 0
    suffix: str = ""

    @classmethod
    def read(cls) -> Version:
        components = VERSION_FILE.read_text(encoding="ascii").split(".")
        year = int(components[0])
        month = int(components[1])
        day = int(components[2])
        rel = 0
        suffix = ""
        try:
            rel = int(components[3])
        except ValueError:
            suffix = components[3].strip()
        else:
            if len(components) > 4:
                suffix = components[4].strip()
        return cls(year=year, month=month, day=day, rel=rel, suffix=suffix)

    def write(self, commit: bool = True) -> None:
        VERSION_FILE.write_text(f"{self}\n", encoding="ascii")
        logging.info("Wrote version: %s", self)
        if commit:
            run(["git", "add", VERSION_FILE.name])
            run(["git", "commit", "-m", f"Update VERSION to {self}"])

    @classmethod
    def today(cls) -> Version:
        today = datetime.date.today()
        return cls(year=today.year, month=today.month, day=today.day)

    @property
    def is_today(self):
        today = datetime.date.today()
        return (
            self.year == today.year
            and self.month == today.month
            and self.day == today.day
        )

    def __str__(self):
        result = f"{self.year}.{self.month:>02}.{self.day:>02}.{self.rel}"
        if self.suffix:
            result += f".{self.suffix}"
        return result


def main():
    upstream = run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        stdout=subprocess.PIPE,
    ).stdout.strip()
    if upstream != "origin/main":
        logging.error("Upstream must be origin/main")
        sys.exit(1)
    if run(
        ["git", "diff", "--name-only", "--cached"],
        stdout=subprocess.PIPE,
    ).stdout:
        logging.error("Uncommitted changes exist")
        sys.exit(1)
    current_version = Version.read()
    if current_version.is_today:
        release_version = dataclasses.replace(
            current_version, rel=current_version.rel + 1, suffix=""
        )
    else:
        release_version = Version.today()
    dev_version = dataclasses.replace(release_version, suffix="dev0")
    release_version.write()
    run(["git", "tag", str(release_version)])
    run(["git", "push", "--tags", "origin", "HEAD:refs/heads/release"])
    dev_version.write()
    run(["git", "push"])


if __name__ == "__main__":
    main()
