import concurrent.futures
import random
import sys
from pathlib import Path

import click

from algobowl.cli import formatter
from algobowl.lib import problem_client, problem_tester


def _read_text(path: Path) -> str:
    """Reads an ASCII text file.

    Args:
        path: File path to read.

    Returns:
        The file contents.
    """
    with open(path, encoding="ascii") as file_obj:
        return file_obj.read()


def _parse_input(cli, path: Path):
    """Parses an input file through the configured problem client.

    Args:
        cli: CLI context.
        path: Input file path.

    Returns:
        Normalized input.
    """
    with open(path, encoding="ascii") as f:
        try:
            return cli.problem.normalize_input(f.read())
        except problem_client.FileFormatError as e:
            formatter.err(f"Input has formatting errors: {e}")
            sys.exit(1)


def _parse_output(cli, iput, oput_path: Path):
    """Parses an output file through the configured problem client.

    Args:
        cli: CLI context.
        iput: Normalized input or input file path.
        oput_path: Output file path.

    Returns:
        Verified output.
    """
    if isinstance(iput, Path):
        iput = _parse_input(cli, iput)
    try:
        return cli.problem.verify_output(iput.content, _read_text(oput_path))
    except problem_client.FileFormatError as e:
        formatter.err(f"Output has formatting errors: {e}")
        sys.exit(1)


@click.group(help="Work with algops problems")
@click.argument("problem", type=str)
@click.pass_obj
def problem(cli, problem):
    cli.problem = problem_client.ProblemClient(problem)


@problem.command(help="Run tests on a problem")
@click.argument("test_data_dir", type=Path)
@click.argument("pytest_args", nargs=-1)
@click.pass_obj
def test(cli, test_data_dir, pytest_args):
    retcode = problem_tester.run_problem_tests(
        cli.problem.url,
        test_data_dir,
        pytest_args,
    )
    sys.exit(retcode)


@problem.command(help="Parse an input file and print the normalized version")
@click.argument("input_file", type=Path)
@click.pass_obj
def parse_input(cli, input_file):
    iput = _parse_input(cli, input_file)
    sys.stdout.write(iput.text())


@problem.command(help="Parse an output file and print the normalized version")
@click.argument("input_file", type=Path)
@click.argument("output_file", type=Path)
@click.pass_obj
def parse_output(cli, input_file, output_file):
    oput = _parse_output(cli, input_file, output_file)
    sys.stdout.write(oput.text())


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
            oput.require_accepted()
        except problem_client.VerificationError as e:
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


@problem.command(help="Generate an input")
@click.option("--seed", type=int, help="Seed to use.  Default: use SystemRandom.")
@click.pass_obj
def generate_input(cli, seed):
    rng = random.Random(seed) if seed else random.SystemRandom()
    iput = cli.problem.generate_input(rng)
    sys.stdout.write(iput.text())


@problem.command(help="Trivially solve an input")
@click.argument("input_file", type=Path)
@click.pass_obj
def trivial_solve(cli, input_file):
    iput = _parse_input(cli, input_file)
    output = cli.problem.trivial_solve(iput.content)
    sys.stdout.write(output.text())
