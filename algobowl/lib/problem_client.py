"""Client helpers for algops problem support services."""

import dataclasses
import enum
import functools
import random
import urllib.parse

import connectrpc.errors
import requests

from algobowl.problemsupport.v1 import problem_support_connect, problem_support_pb2


class FileFormatError(Exception):
    """Raised when an input or output file has formatting errors."""


class VerificationError(Exception):
    """Raised when an output is well-formed but rejected."""


class RankSort(enum.Enum):
    """Problem ranking sort direction."""

    MINIMIZATION = "minimization"
    MAXIMIZATION = "maximization"


_RANK_SORT_FROM_PROTO = {
    problem_support_pb2.RANK_SORT_MINIMIZATION: RankSort.MINIMIZATION,
    problem_support_pb2.RANK_SORT_MAXIMIZATION: RankSort.MAXIMIZATION,
}


class ProblemClientError(Exception):
    """Raised when an algops problem service returns an unexpected response."""


@dataclasses.dataclass(frozen=True)
class NormalizedInput:
    """An input accepted and normalized by an algops problem service.

    Attributes:
        content: Normalized input bytes.
    """

    content: bytes

    def text(self) -> str:
        """Returns normalized input content as UTF-8 text.

        Returns:
            The normalized input text.
        """
        return _bytes_to_text(self.content)


@dataclasses.dataclass(frozen=True)
class VerifiedOutput:
    """An output checked and normalized by an algops problem service.

    Attributes:
        content: Normalized output bytes.
        score: Reported output score.
        rejection_reason: Reason the output was rejected, or None if accepted.
    """

    content: bytes
    score: int
    rejection_reason: str | None

    def text(self) -> str:
        """Returns normalized output content as UTF-8 text.

        Returns:
            The normalized output text.
        """
        return _bytes_to_text(self.content)

    def require_accepted(self) -> None:
        """Raises VerificationError if the output was rejected.

        Raises:
            VerificationError: The service rejected the output.
        """
        if self.rejection_reason is not None:
            raise VerificationError(self.rejection_reason)


def _content_to_bytes(content: str | bytes) -> bytes:
    """Converts text or bytes content to bytes.

    Args:
        content: Text or bytes content.

    Returns:
        Content encoded as UTF-8 bytes.
    """
    if isinstance(content, str):
        return content.encode("utf-8")
    return content


def _bytes_to_text(content: bytes) -> str:
    """Converts UTF-8 bytes to text.

    Args:
        content: UTF-8 encoded content.

    Returns:
        Decoded text.
    """
    return content.decode("utf-8")


def _verified_output_from_proto(
    output: problem_support_pb2.VerifiedOutput,
) -> VerifiedOutput:
    """Converts a VerifiedOutput protobuf into a local value object.

    Args:
        output: VerifiedOutput protobuf from the algops service.

    Returns:
        Local verified output value object.

    Raises:
        ProblemClientError: The service omitted the verification result.
    """
    verification = output.WhichOneof("verification")
    if verification == "accepted":
        return VerifiedOutput(
            content=output.normalized_content,
            score=output.reported_score,
            rejection_reason=None,
        )
    if verification == "rejected":
        return VerifiedOutput(
            content=output.normalized_content,
            score=output.reported_score,
            rejection_reason=output.rejected.rejection_reason,
        )
    raise ProblemClientError("VerifiedOutput did not include verification")


class ProblemClient:
    """Client for an algops problem support service.

    Attributes:
        url: Base URL of the problem support service.
    """

    def __init__(self, url: str) -> None:
        """Initializes a problem client.

        Args:
            url: Base URL of the problem support service.
        """
        self.url = url.rstrip("/")

    def _client(
        self,
    ) -> problem_support_connect.ProblemSupportServiceClientSync:
        """Creates a generated Connect client.

        Returns:
            A synchronous generated Connect client.
        """
        return problem_support_connect.ProblemSupportServiceClientSync(
            self.url,
            accept_compression=(),
            send_compression=None,
        )

    @functools.cached_property
    def info(self) -> problem_support_pb2.GetProblemInfoResponse:
        """Gets problem metadata.

        Returns:
            The problem metadata response.
        """
        request = problem_support_pb2.GetProblemInfoRequest()
        with self._client() as client:
            return client.get_problem_info(request)

    def rank_sort(self) -> RankSort:
        """Gets the rank sort direction for this problem.

        Returns:
            The rank sort direction.
        """
        return _RANK_SORT_FROM_PROTO[self.info.rank_sort]

    def format_score(self, score: int) -> str:
        """Formats a score for display.

        Args:
            score: Integer score value.

        Returns:
            Score formatted using the problem metadata.
        """
        decimal_places = self.info.score_decimal_places
        if decimal_places == 0:
            return str(score)
        scale = 10**decimal_places
        return f"{score / scale:.{decimal_places}f}"

    def statement_pdf(self) -> bytes:
        """Downloads the problem statement PDF.

        Returns:
            PDF statement bytes.

        Raises:
            ProblemClientError: The problem does not advertise a PDF statement.
        """
        for statement in self.info.statements:
            if statement.format == problem_support_pb2.STATEMENT_FORMAT_PDF:
                statement_url = urllib.parse.urljoin(
                    f"{self.url}/",
                    statement.url,
                )
                response = requests.get(statement_url)
                response.raise_for_status()
                return response.content
        raise ProblemClientError("Problem does not provide a PDF statement")

    def normalize_input(self, content: str | bytes) -> NormalizedInput:
        """Validates and normalizes input content.

        Args:
            content: Input content as text or bytes.

        Returns:
            Normalized input.

        Raises:
            FileFormatError: The input has formatting errors.
        """
        request = problem_support_pb2.VerifyInputRequest(
            content=_content_to_bytes(content),
        )
        with self._client() as client:
            response = client.verify_input(request)

        if response.WhichOneof("result") == "format_error":
            raise FileFormatError(response.format_error)
        return NormalizedInput(response.normalized_content)

    def verify_output(
        self,
        input_content: str | bytes,
        output_content: str | bytes,
    ) -> VerifiedOutput:
        """Validates, normalizes, and verifies output content.

        Args:
            input_content: Input content as text or bytes.
            output_content: Output content as text or bytes.

        Returns:
            Verified output value object.

        Raises:
            FileFormatError: The input or output has formatting errors.
            ProblemClientError: The response omits the output.
        """
        request = problem_support_pb2.VerifyOutputRequest(
            input_content=_content_to_bytes(input_content),
            output_content=_content_to_bytes(output_content),
        )
        with self._client() as client:
            response = client.verify_output(request)

        if response.WhichOneof("result") == "format_error":
            raise FileFormatError(response.format_error)
        if response.WhichOneof("result") != "output":
            raise ProblemClientError("VerifyOutput response did not include output")
        return _verified_output_from_proto(response.output)

    def generate_input(self, rng: random.Random) -> NormalizedInput:
        """Generates input content.

        Args:
            rng: Random source used to seed the remote generator.

        Returns:
            Normalized generated input.

        Raises:
            NotImplementedError: The problem does not support input generation.
        """
        request = problem_support_pb2.GenerateInputRequest(
            seed=rng.getrandbits(63),
        )
        try:
            with self._client() as client:
                response = client.generate_input(request)
        except connectrpc.errors.ConnectError as exc:
            raise NotImplementedError(str(exc)) from exc
        return NormalizedInput(response.content)

    def trivial_solve(self, input_content: str | bytes) -> VerifiedOutput:
        """Solves an input with the problem's trivial solver.

        Args:
            input_content: Input content as text or bytes.

        Returns:
            Verified output from the trivial solver.

        Raises:
            NotImplementedError: The problem does not support the trivial solver.
        """
        normalized_input = _content_to_bytes(input_content)
        request = problem_support_pb2.SolveRequest(
            input_content=normalized_input,
            solver_type=problem_support_pb2.SOLVER_TYPE_TRIVIAL,
        )
        try:
            with self._client() as client:
                response = client.solve(request)
        except connectrpc.errors.ConnectError as exc:
            raise NotImplementedError(str(exc)) from exc
        return self.verify_output(normalized_input, response.output_content)
