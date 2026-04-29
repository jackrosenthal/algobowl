"""Automated tester for the problem format."""

import enum
import pathlib
import random
import sys

import pytest

from algobowl.lib import problem_client


class ASCIIFormat(enum.Enum):
    UNIX = 0
    DOS = 1
    DOS_WITH_FINAL_TERMINATOR = 2


@pytest.fixture
def problem(problem_url):
    return problem_client.ProblemClient(problem_url)


@pytest.fixture(params=[1337, 0xDEADBEEF, 0xDEADD00D, 55378008])
def rng(request):
    return random.Random(request.param)


def content_from_path(path, ascii_format=False):
    """Reads an ASCII test data file with an alternate newline format.

    Args:
        path: File path to read.
        ascii_format: Newline format to emulate.

    Returns:
        The file contents with the requested newline format.
    """
    contents = path.read_text(encoding="ascii")
    assert "\r\n" not in contents
    if ascii_format != ASCIIFormat.UNIX:
        contents = contents.removesuffix("\n")
        contents = contents.replace("\n", "\r\n")
        if ascii_format == ASCIIFormat.DOS_WITH_FINAL_TERMINATOR:
            contents += "\r\n"
    return contents


def test_good_input(problem, good_input_path, ascii_format):
    input_ = problem.normalize_input(
        content_from_path(good_input_path, ascii_format=ascii_format)
    )

    reformatted = input_.text()
    assert reformatted.endswith("\n")

    # The reformatted data should also parse OK.
    problem.normalize_input(reformatted)


def test_bad_input(problem, bad_input_path, ascii_format):
    with pytest.raises(problem_client.FileFormatError):
        problem.normalize_input(
            content_from_path(bad_input_path, ascii_format=ascii_format)
        )


def test_empty_input(problem):
    # The empty input should never be valid.
    with pytest.raises(problem_client.FileFormatError):
        problem.normalize_input("")


def test_good_output(problem, good_output_path, ascii_format):
    input_path, output_path = good_output_path
    input_ = problem.normalize_input(content_from_path(input_path))
    output = problem.verify_output(
        input_.content,
        content_from_path(output_path, ascii_format=ascii_format),
    )
    output.require_accepted()

    # Reformatting the output should still result in a good output.
    reformatted = output.text()
    assert reformatted.endswith("\n")
    reformatted_output = problem.verify_output(input_.content, reformatted)
    reformatted_output.require_accepted()
    assert output.score == reformatted_output.score


def test_bad_output(problem, bad_output_path, ascii_format):
    input_path, output_path = bad_output_path
    input_ = problem.normalize_input(content_from_path(input_path))
    with pytest.raises(problem_client.FileFormatError):
        problem.verify_output(
            input_.content,
            content_from_path(output_path, ascii_format=ascii_format),
        )


def test_rejected_output(problem, rejected_output_path, ascii_format):
    input_path, output_path = rejected_output_path
    input_ = problem.normalize_input(content_from_path(input_path))
    output = problem.verify_output(
        input_.content,
        content_from_path(output_path, ascii_format=ascii_format),
    )
    with pytest.raises(problem_client.VerificationError):
        output.require_accepted()

    # Reformatting an output should still result in a rejected output.
    reformatted = output.text()
    assert reformatted.endswith("\n")
    reformatted_output = problem.verify_output(input_.content, reformatted)
    with pytest.raises(problem_client.VerificationError):
        reformatted_output.require_accepted()
    assert output.score == reformatted_output.score


def test_generate_input(problem, rng):
    try:
        input = problem.generate_input(rng)
    except NotImplementedError:
        pytest.skip("Input.generate() is not required (yet!)")

    # We should be able to parse the generated input.
    problem.normalize_input(input.content)

    # Solve the generated input.
    try:
        output = problem.trivial_solve(input.content)
    except NotImplementedError:
        pytest.skip("Input.trivial_solve() not implemented")

    # The solved output should be valid.
    output.require_accepted()

    # We should be able to parse the written output.
    reparsed_output = problem.verify_output(input.content, output.content)
    reparsed_output.require_accepted()


def load_inputs_from_dir(path):
    """Loads input test data paths from a directory.

    Args:
        path: Directory containing input files.

    Returns:
        A list of input file paths.
    """
    return list(path.glob("*.in"))


def load_outputs_from_dir(path):
    """Loads paired input and output test data paths from a directory.

    Args:
        path: Directory containing output symlinks and output files.

    Returns:
        A list of input path and output path pairs.
    """
    result = []
    for input_path in load_inputs_from_dir(path):
        assert input_path.is_symlink()
        output_path = input_path.parent / f"{input_path.stem}.out"
        result.append((input_path, output_path))
    return result


def run_problem_tests(problem_url, test_data_dir, pytest_extra_args=()):
    """Runs the algops problem tester.

    Args:
        problem_url: Base URL for the algops problem support service.
        test_data_dir: Directory containing problem test data.
        pytest_extra_args: Extra arguments to pass to pytest.

    Returns:
        The pytest return code.
    """
    test_data_dir = pathlib.Path(test_data_dir).resolve()

    good_inputs = load_inputs_from_dir(test_data_dir / "inputs" / "good")
    bad_inputs = load_inputs_from_dir(test_data_dir / "inputs" / "bad")

    good_outputs = load_outputs_from_dir(test_data_dir / "outputs" / "good")
    bad_outputs = load_outputs_from_dir(test_data_dir / "outputs" / "bad")
    rejected_outputs = load_outputs_from_dir(test_data_dir / "outputs" / "rejected")

    class ProblemDataPlugin:
        def pytest_generate_tests(self, metafunc):
            def _add_param(name, value):
                if name in metafunc.fixturenames:
                    metafunc.parametrize(name, value)

            _add_param("good_input_path", good_inputs)
            _add_param("bad_input_path", bad_inputs)
            _add_param("good_output_path", good_outputs)
            _add_param("bad_output_path", bad_outputs)
            _add_param("rejected_output_path", rejected_outputs)
            _add_param("problem_url", [problem_url])
            _add_param("ascii_format", list(ASCIIFormat))

    return pytest.main([*pytest_extra_args, __file__], plugins=[ProblemDataPlugin()])


def main(argv=sys.argv):
    """Runs the problem tester command-line entry point.

    Args:
        argv: Command-line arguments.
    """
    sys.exit(run_problem_tests(argv[1], argv[2], pytest_extra_args=argv[3:]))


if __name__ == "__main__":
    main()
