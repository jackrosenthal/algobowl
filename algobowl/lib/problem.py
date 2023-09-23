"""
Problem Format Helpers
======================

This module contains two things:

1. The BaseInput and BaseOutput classes, which define the base classes
   for input classes and output classes respectively.

2. Any helper functions to help implement problems.
"""

import dataclasses
import enum
import pathlib
import types
import typing

from algobowl.lib import problem_tester


class FileFormatError(Exception):
    """Raised from .read() for either an input or an output.

    This exception will always notify the user of the formatting error
    immediately.  The exception message will be displayed to the user.
    """


class VerificationError(Exception):
    """Raised from .verify() (or .compute_actual_score()) of an output.

    This exception will not notify the user, and will count as an
    output rejection from the instructor.  The instructor will be able
    to see the exception message, but not students.
    """


class ProblemTestError(Exception):
    """Tests did not pass successfully."""


class RankSort(enum.Enum):
    minimization = 0
    maximization = 1


@dataclasses.dataclass
class BaseInput:
    @classmethod
    def read(cls, f):
        """Read an input file."""
        raise NotImplementedError

    def write(self, f):
        """Write an input file."""
        raise NotImplementedError


@dataclasses.dataclass
class BaseOutput:
    input: BaseInput
    score: int
    rank_sort: typing.ClassVar[RankSort] = RankSort.minimization

    @classmethod
    def read(cls, input, f):
        """Read an output file."""
        raise NotImplementedError

    def compute_actual_score(self):
        """Compute the correct score that should correspond to this output.

        Returns:
            The integer score value.

        Raises:
            A VerificationError, if the output is not valid.
        """
        raise NotImplementedError

    def verify(self):
        """Verify an output is valid.

        Raises:
            A VerificationError, if the output is not valid.
        """
        actual_score = self.compute_actual_score()
        if self.score != actual_score:
            raise VerificationError(
                f"Reported score ({self.score}) does not match actual ({actual_score})"
            )

    @staticmethod
    def repr_score(score):
        """Get the score as a string."""
        return str(score)

    def write(self, f):
        """Write an output."""
        raise NotImplementedError


def check_bound(lineno, bound, value):
    if bound is None:
        return
    if isinstance(bound, int):
        cond = value == bound
    elif callable(bound):
        cond = bound(value)
    else:
        cond = value in bound
    if cond:
        return
    raise FileFormatError(f"Line #{lineno + 1}: Value {value} out of expected bounds")


def assert_linecount(lines, bounds):
    try:
        check_bound(-1, bounds, len(lines))
    except FileFormatError:
        # Try to be accommodating of extra blank lines at end of file.
        while lines and not lines[-1].rstrip():
            lines.pop()
            try:
                check_bound(-1, bounds, len(lines))
                return
            except FileFormatError:
                continue
        raise FileFormatError("File has invalid number of lines")


def parse_int(lineno, value, bound=None):
    try:
        value = int(value)
    except ValueError:
        raise FileFormatError(
            f"Line #{lineno + 1}: Unable to interpret {value!r} as integer"
        )
    check_bound(lineno, bound, value)
    return value


def parse_line_ints(lines, lineno, bounds=None, count=None):
    line = lines[lineno]
    line_split = line.split()
    try:
        check_bound(lineno, count, len(line_split))
    except FileFormatError:
        raise FileFormatError(
            f"Line #{lineno + 1}: Number of values ({len(line_split)}) "
            f"is out of expected bounds"
        )
    return [parse_int(lineno, value, bounds) for value in line_split]


def parse_line_int(lines, lineno, bounds=None):
    return parse_line_ints(lines, lineno, bounds=bounds, count=1)[0]


_module_cache = {}
_statement_cache = {}


def _cache_getent(cache, path, loader=lambda pth: pth.read_bytes()):
    path = path.resolve()
    mtime = path.stat().st_mtime
    if path in cache:
        c_mtime, c_val = cache[path]
        if c_mtime == mtime:
            return c_val
    val = loader(path)
    cache[path] = (mtime, val)
    return val


class Problem:
    """High-level wrapper around the problem format."""

    def __init__(self, path):
        self.path = path

    def get_module(self):
        def loader(path):
            contents = path.read_text()
            module = types.ModuleType("problem")
            code = compile(contents, str(path), "exec")
            exec(code, module.__dict__)
            return module

        return _cache_getent(_module_cache, self.path / "problem.py", loader=loader)

    def get_statement_pdf(self):
        return _cache_getent(_statement_cache, self.path / "statement.pdf")

    def parse_input(self, input_file):
        module = self.get_module()
        return module.Input.read(input_file)

    def parse_output(self, input, output_file):
        module = self.get_module()
        if not isinstance(input, module.Input):
            input = module.Input.read(input)
        output = module.Output.read(input, output_file)
        return output

    def verify_output(self, input, output_file):
        output = self.parse_output(input, output_file)
        output.verify()

    def run_tests(self, pytest_extra_args=()):
        """Run tests on this problem."""
        retcode = problem_tester.run_problem_tests(self.path, pytest_extra_args)
        if retcode != 0:
            raise ProblemTestError(f"Tests failed with error code {retcode}")


class DefaultProblem(Problem):
    """Used when the problem is unspecified."""

    def __init__(self):
        pass

    def get_module(self):
        module = types.ModuleType("problem")
        module.Input = BaseInput
        module.Output = BaseOutput
        return module


def load_problem(competition):
    # Deferred import so this module does not depend on TurboGears for
    # most functionality.
    import tg

    if not competition.problem:
        return DefaultProblem()

    for path in tg.config.get("problems.search_paths", "").split():
        if not path:
            continue
        path = pathlib.Path(path)
        if (path / competition.problem).is_dir():
            return Problem(path / competition.problem)
    raise ValueError(f"No problem named {competition.problem}")
