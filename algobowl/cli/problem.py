import concurrent.futures
import io
import sys
from pathlib import Path

import click

import algobowl.lib.problem as problemlib
from algobowl.cli import formatter


def _parse_input(cli, path: Path):
    with open(path, "r", encoding="ascii") as f:
        try:
            return cli.problem.parse_input(f)
        except problemlib.FileFormatError as e:
            formatter.err(f"Input has formatting errors: {e}")
            sys.exit(1)


def _parse_output(cli, iput, oput_path: Path):
    if isinstance(iput, Path):
        iput = _parse_input(cli, iput)
    with open(oput_path, "r", encoding="ascii") as f:
        try:
            return cli.problem.parse_output(iput, f)
        except problemlib.FileFormatError as e:
            formatter.err(f"Output has formatting errors: {e}")
            sys.exit(1)


@click.group(help="Work with local problems")
@click.argument("problem", type=str)
@click.pass_obj
def problem(cli, problem):
    cli.problem = cli.config.load_problem(problem)


@problem.command(help="Run tests on a problem")
@click.argument("pytest_args", nargs=-1)
@click.pass_obj
def test(cli, pytest_args):
    pytest_args = [
        "--cov",
        "problem",
        "--cov-report",
        "term-missing:skip-covered",
        *pytest_args,
    ]
    try:
        cli.problem.run_tests(pytest_args)
    except problemlib.ProblemTestError:
        sys.exit(1)


@problem.command(help="Parse an input file and print the normalized version")
@click.argument("input_file", type=Path)
@click.pass_obj
def parse_input(cli, input_file):
    iput = _parse_input(cli, input_file)
    iput.write(sys.stdout)


@problem.command(help="Parse an output file and print the normalized version")
@click.argument("input_file", type=Path)
@click.argument("output_file", type=Path)
@click.pass_obj
def parse_output(cli, input_file, output_file):
    oput = _parse_output(cli, input_file, output_file)
    oput.write(sys.stdout)


@problem.command(help="Verify an output")
@click.argument("input_file", type=Path)
@click.argument("output_files", type=Path, nargs=-1, required=True)
@click.pass_obj
def verify(cli, input_file, output_files):
    rv = 0
    iput = _parse_input(cli, input_file)

    def _verify_output(output_file):
        rv = 0
        oput = _parse_output(cli, iput, output_file)
        message = click.style("OK!", fg="green", bold=True)
        try:
            oput.verify()
        except problemlib.VerificationError as e:
            rv = 1
            message = click.style(f"BAD: {e}", fg="red", bold=True)
        message = f"{output_file}: {message}"
        return rv, message

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for output_file in output_files:
            futures.append(executor.submit(_verify_output, output_file))

    for future in futures:
        future_rv, message = future.result()
        rv = rv or future_rv
        click.echo(message)

    sys.exit(rv)
