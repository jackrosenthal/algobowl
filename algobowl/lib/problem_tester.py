"""Automated tester for the problem format."""

import enum
import io
import pathlib
import sys

import pytest

import algobowl.lib.problem as problemlib


class ASCIIFormat(enum.Enum):
    UNIX = 0
    DOS = 1
    DOS_WITH_FINAL_TERMINATOR = 2


@pytest.fixture
def problem(problem_dir):
    return problemlib.Problem(problem_dir)


def stringio_from_path(path, ascii_format=False):
    contents = path.read_text(encoding="ascii")
    assert "\r\n" not in contents
    if ascii_format != ASCIIFormat.UNIX:
        if contents.endswith("\n"):
            contents = contents[:-1]
        contents = contents.replace("\n", "\r\n")
        if ascii_format == ASCIIFormat.DOS_WITH_FINAL_TERMINATOR:
            contents += "\r\n"
    return io.StringIO(contents)


def test_good_input(problem, good_input_path, ascii_format):
    input = problem.parse_input(
        stringio_from_path(good_input_path, ascii_format=ascii_format)
    )
    output_buf = io.StringIO()
    input.write(output_buf)

    reformatted = output_buf.getvalue()
    assert reformatted.endswith("\n")

    # The reformatted data should also parse OK.
    problem.parse_input(io.StringIO(reformatted))


def test_bad_input(problem, bad_input_path, ascii_format):
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_input(
            stringio_from_path(bad_input_path, ascii_format=ascii_format)
        )


def test_empty_input(problem):
    # The empty input should never be valid.
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_input(io.StringIO(""))


def test_good_output(problem, good_output_path, ascii_format):
    input_path, output_path = good_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    output = problem.parse_output(
        input, stringio_from_path(output_path, ascii_format=ascii_format)
    )
    output.verify()

    # Reformatting the output should still result in a good output.
    output_buf = io.StringIO()
    output.write(output_buf)
    reformatted = output_buf.getvalue()
    assert reformatted.endswith("\n")
    reformatted_output = problem.parse_output(input, io.StringIO(reformatted))
    reformatted_output.verify()
    assert output.score == reformatted_output.score


def test_bad_output(problem, bad_output_path, ascii_format):
    input_path, output_path = bad_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_output(
            input, stringio_from_path(output_path, ascii_format=ascii_format)
        )


def test_rejected_output(problem, rejected_output_path, ascii_format):
    input_path, output_path = rejected_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    output = problem.parse_output(
        input, stringio_from_path(output_path, ascii_format=ascii_format)
    )
    with pytest.raises(problemlib.VerificationError):
        output.verify()

    # Reformatting an output should still result in a rejected output.
    output_buf = io.StringIO()
    output.write(output_buf)
    reformatted = output_buf.getvalue()
    assert reformatted.endswith("\n")
    reformatted_output = problem.parse_output(input, io.StringIO(reformatted))
    with pytest.raises(problemlib.VerificationError):
        output.verify()
    assert output.score == reformatted_output.score


def load_inputs_from_dir(path):
    return list(path.glob("*.in"))


def load_outputs_from_dir(path):
    result = []
    for input_path in load_inputs_from_dir(path):
        assert input_path.is_symlink()
        output_path = input_path.parent / f"{input_path.stem}.out"
        result.append((input_path, output_path))
    return result


def run_problem_tests(problem_dir, pytest_extra_args=()):
    problem_dir = pathlib.Path(problem_dir).resolve()
    test_data_dir = problem_dir / "test_data"

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
            _add_param("problem_dir", [problem_dir])
            _add_param("ascii_format", list(ASCIIFormat))

    return pytest.main([*pytest_extra_args, __file__], plugins=[ProblemDataPlugin()])


def main(argv=sys.argv):
    sys.exit(run_problem_tests(argv[1], pytest_extra_args=argv[2:]))


if __name__ == "__main__":
    main()
