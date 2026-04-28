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
import random
import typing
from collections.abc import Sequence

from typing_extensions import Self


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

    @classmethod
    def generate(cls, rng: random.Random) -> Self:
        """Generate an input."""
        raise NotImplementedError

    def trivial_solve(self) -> "BaseOutput":
        """Solve this input in the most trivial way possible.

        This should solve the input in a valid but computationally cheap manner.
        Perhaps you want to aim to solve the problem with the worst answer
        possible.  Problems are not required to implement this, but it does
        provide some fuzz testing of outputs and the verifier when combined with
        the generate() method.
        """
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
    except FileFormatError as e:
        # Try to be accommodating of extra blank lines at end of file.
        while lines and not lines[-1].rstrip():
            lines.pop()
            try:
                check_bound(-1, bounds, len(lines))
                return
            except FileFormatError:
                continue
        raise FileFormatError("File has invalid number of lines") from e


def parse_int(lineno, value, bound=None):
    try:
        value = int(value)
    except ValueError as e:
        raise FileFormatError(
            f"Line #{lineno + 1}: Unable to interpret {value!r} as integer"
        ) from e
    check_bound(lineno, bound, value)
    return value


def parse_line_ints(lines, lineno, bounds=None, count=None):
    line = lines[lineno]
    line_split = line.split()
    try:
        check_bound(lineno, count, len(line_split))
    except FileFormatError as e:
        raise FileFormatError(
            f"Line #{lineno + 1}: Number of values ({len(line_split)}) "
            f"is out of expected bounds"
        ) from e
    if isinstance(bounds, range) or not (
        isinstance(bounds, Sequence) and len(bounds) == count
    ):
        bounds = [bounds] * len(line_split)
    return [
        parse_int(lineno, value, bound=bound)
        for bound, value in zip(bounds, line_split)
    ]


def parse_line_int(lines, lineno, bounds=None):
    return parse_line_ints(lines, lineno, bounds=bounds, count=1)[0]
