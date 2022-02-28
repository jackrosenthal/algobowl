"""Automated tester for the problem format."""

import io
import pathlib
import sys

import pytest

import algobowl.lib.problem as problemlib


@pytest.fixture
def problem(problem_dir):
    return problemlib.Problem(problem_dir)


def stringio_from_path(path, convert_to_dos=False):
    contents = path.read_text()
    assert "\r\n" not in contents
    if convert_to_dos:
        if contents.endswith("\n"):
            contents = contents[:-1]
        contents = contents.replace("\n", "\r\n")
    return io.StringIO(contents)


def test_good_input(problem, good_input_path, convert_to_dos):
    input = problem.parse_input(
        stringio_from_path(good_input_path, convert_to_dos=convert_to_dos)
    )
    output_buf = io.StringIO()
    input.write(output_buf)

    reformatted = output_buf.getvalue()
    assert reformatted.endswith("\n")

    # The reformatted data should also parse OK.
    problem.parse_input(io.StringIO(reformatted))


def test_bad_input(problem, bad_input_path, convert_to_dos):
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_input(
            stringio_from_path(bad_input_path, convert_to_dos=convert_to_dos)
        )


def test_empty_input(problem):
    # The empty input should never be valid.
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_input(io.StringIO(""))


def test_good_output(problem, good_output_path, convert_to_dos):
    input_path, output_path = good_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    output = problem.parse_output(
        input, stringio_from_path(output_path, convert_to_dos=convert_to_dos)
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


def test_bad_output(problem, bad_output_path, convert_to_dos):
    input_path, output_path = bad_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    with pytest.raises(problemlib.FileFormatError):
        problem.parse_output(
            input, stringio_from_path(output_path, convert_to_dos=convert_to_dos)
        )


def test_rejected_output(problem, rejected_output_path, convert_to_dos):
    input_path, output_path = rejected_output_path
    input = problem.parse_input(stringio_from_path(input_path))
    output = problem.parse_output(
        input, stringio_from_path(output_path, convert_to_dos=convert_to_dos)
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
            _add_param("convert_to_dos", [True, False])

    return pytest.main([*pytest_extra_args, __file__], plugins=[ProblemDataPlugin()])


def main(argv=sys.argv):
    sys.exit(run_problem_tests(argv[1], pytest_extra_args=argv[2:]))


if __name__ == "__main__":
    main()
