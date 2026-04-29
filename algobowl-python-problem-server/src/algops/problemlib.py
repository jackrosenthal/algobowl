"""Problem authoring helpers for algops problem servers."""

from __future__ import annotations

import dataclasses
import random
from collections.abc import Callable, Sequence
from typing import Any, Self

Bound = int | range | Sequence[int] | Callable[[int], bool] | None


class FileFormatError(Exception):
    """Raised when an input or output file has formatting errors."""


class VerificationError(Exception):
    """Raised when an output is well-formed but should be rejected."""


class ProblemTestError(Exception):
    """Raised when problem tests do not pass successfully."""


@dataclasses.dataclass
class BaseInput:
    """Base class for problem input files."""

    @classmethod
    def read(cls, f: Any) -> Self:
        """Reads an input file.

        Args:
            f: File-like object to read from.

        Returns:
            Parsed input.
        """
        raise NotImplementedError

    def write(self, f: Any) -> None:
        """Writes an input file.

        Args:
            f: File-like object to write to.
        """
        raise NotImplementedError

    @classmethod
    def generate(cls, rng: random.Random) -> Self:
        """Generates an input.

        Args:
            rng: Random source to use for generation.

        Returns:
            Generated input.
        """
        raise NotImplementedError

    def trivial_solve(self) -> BaseOutput:
        """Solves this input in the most trivial way possible.

        Returns:
            Output produced by the trivial solver.
        """
        raise NotImplementedError


@dataclasses.dataclass
class BaseOutput:
    """Base class for problem output files."""

    input: BaseInput
    score: int

    @classmethod
    def read(cls, input_: BaseInput, f: Any) -> Self:
        """Reads an output file.

        Args:
            input_: Parsed input corresponding to the output.
            f: File-like object to read from.

        Returns:
            Parsed output.
        """
        raise NotImplementedError

    def compute_actual_score(self) -> int:
        """Computes the correct score for this output.

        Returns:
            The actual score.

        Raises:
            VerificationError: The output is invalid.
        """
        raise NotImplementedError

    def verify(self) -> None:
        """Verifies that this output is valid.

        Raises:
            VerificationError: The output is invalid.
        """
        actual_score = self.compute_actual_score()
        if self.score != actual_score:
            raise VerificationError(
                f"Reported score ({self.score}) does not match actual ({actual_score})"
            )

    def repr_score(self, score: int) -> str:
        """Formats a score as text.

        Args:
            score: Score to format.

        Returns:
            Formatted score.
        """
        return str(score)

    def write(self, f: Any) -> None:
        """Writes an output file.

        Args:
            f: File-like object to write to.
        """
        raise NotImplementedError


def check_bound(lineno: int, bound: Bound, value: int) -> None:
    """Checks whether an integer value is inside a bound.

    Args:
        lineno: Zero-based line number for error reporting.
        bound: Expected value, range, sequence, predicate, or None.
        value: Value to check.

    Raises:
        FileFormatError: The value is outside the expected bound.
    """
    if bound is None:
        return
    if isinstance(bound, int):
        condition = value == bound
    elif callable(bound):
        condition = bound(value)
    else:
        condition = value in bound
    if condition:
        return
    raise FileFormatError(f"Line #{lineno + 1}: Value {value} out of expected bounds")


def assert_linecount(lines: list[Any], bounds: Bound) -> None:
    """Checks the number of lines in a file.

    Args:
        lines: Lines read from the file.
        bounds: Expected line count bound.

    Raises:
        FileFormatError: The file has an invalid line count.
    """
    try:
        check_bound(-1, bounds, len(lines))
    except FileFormatError as exc:
        while lines and not lines[-1].rstrip():
            lines.pop()
            try:
                check_bound(-1, bounds, len(lines))
                return
            except FileFormatError:
                continue
        raise FileFormatError("File has invalid number of lines") from exc


def parse_int(lineno: int, value: Any, bound: Bound = None) -> int:
    """Parses an integer and checks its bounds.

    Args:
        lineno: Zero-based line number for error reporting.
        value: Value to parse.
        bound: Expected value bound.

    Returns:
        Parsed integer.

    Raises:
        FileFormatError: The value cannot be parsed or is out of bounds.
    """
    try:
        parsed = int(value)
    except ValueError as exc:
        raise FileFormatError(
            f"Line #{lineno + 1}: Unable to interpret {value!r} as integer"
        ) from exc
    check_bound(lineno, bound, parsed)
    return parsed


def parse_line_ints(
    lines: Sequence[Any],
    lineno: int,
    bounds: Bound | Sequence[Bound] = None,
    count: Bound = None,
) -> list[int]:
    """Parses whitespace-separated integers from a line.

    Args:
        lines: File lines.
        lineno: Zero-based line number to parse.
        bounds: Bound or per-value bounds for parsed integers.
        count: Expected number of values on the line.

    Returns:
        Parsed integers.

    Raises:
        FileFormatError: The line has the wrong count or invalid values.
    """
    line = lines[lineno]
    line_split = line.split()
    try:
        check_bound(lineno, count, len(line_split))
    except FileFormatError as exc:
        raise FileFormatError(
            f"Line #{lineno + 1}: Number of values ({len(line_split)}) "
            "is out of expected bounds"
        ) from exc
    if isinstance(bounds, range) or not (
        isinstance(bounds, Sequence) and len(bounds) == count
    ):
        bounds = [bounds] * len(line_split)
    return [
        parse_int(lineno, value, bound=bound)
        for bound, value in zip(bounds, line_split, strict=False)
    ]


def parse_line_int(
    lines: Sequence[Any],
    lineno: int,
    bounds: Bound = None,
) -> int:
    """Parses one integer from a line.

    Args:
        lines: File lines.
        lineno: Zero-based line number to parse.
        bounds: Bound for the parsed integer.

    Returns:
        Parsed integer.
    """
    return parse_line_ints(lines, lineno, bounds=bounds, count=1)[0]
