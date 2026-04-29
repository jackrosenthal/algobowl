"""ASGI application for algops problem support services."""

from __future__ import annotations

import dataclasses
import enum
import io
import random
from collections.abc import Awaitable, Callable, Iterable
from typing import Any, Self

import starlette.applications
import starlette.requests
import starlette.responses
import starlette.routing

from algops import _connect, problemlib
from algops.proto.algobowl.problemsupport.v1 import problem_support_pb2

RANK_SORT_MINIMIZATION = problem_support_pb2.RANK_SORT_MINIMIZATION
RANK_SORT_MAXIMIZATION = problem_support_pb2.RANK_SORT_MAXIMIZATION

_SOLVER_NAMES = {
    problem_support_pb2.SOLVER_TYPE_TRIVIAL: "trivial_solve",
}

_SERVICE_DESCRIPTOR = problem_support_pb2.DESCRIPTOR.services_by_name[
    "ProblemSupportService"
]


class StatementFormat(enum.Enum):
    """Problem statement file formats."""

    MARKDOWN = problem_support_pb2.STATEMENT_FORMAT_MARKDOWN
    PDF = problem_support_pb2.STATEMENT_FORMAT_PDF


@dataclasses.dataclass(frozen=True)
class Statement:
    """Statement metadata exposed by a problem service.

    Attributes:
        format: Statement file format.
        url: URL where the statement can be downloaded.
    """

    format: StatementFormat
    url: str

    @classmethod
    def markdown(cls, url: str) -> Self:
        """Statement in Markdown format at the given URL.

        A root-relative URL (starting with ``/``) is resolved against the
        request origin at the time ``GetProblemInfo`` is called.
        """
        return cls(format=StatementFormat.MARKDOWN, url=url)

    @classmethod
    def pdf(cls, url: str) -> Self:
        """Statement PDF at the given URL.

        A root-relative URL (starting with ``/``) is resolved against the
        request origin at the time ``GetProblemInfo`` is called.
        """
        return cls(format=StatementFormat.PDF, url=url)


def _base_url_from_scope(scope: dict[str, Any]) -> str:
    """Derive the base URL (scheme + host) from an ASGI HTTP scope."""
    scheme = scope.get("scheme", "https")
    for name, value in scope.get("headers", ()):
        if name.lower() == b"host":
            return f"{scheme}://{value.decode('latin-1')}"
    server = scope.get("server")
    if server:
        host, port = server
        default_port = 443 if scheme == "https" else 80
        if port != default_port:
            return f"{scheme}://{host}:{port}"
        return f"{scheme}://{host}"
    return f"{scheme}://localhost"


def _resolve_url(url: str, scope: dict[str, Any] | None) -> str:
    """Resolve a root-relative URL to absolute using the ASGI scope, if needed."""
    if url.startswith("/") and scope is not None:
        return _base_url_from_scope(scope) + url
    return url


def _make_rpc_endpoint(
    request_type: type[Any],
    handler: Callable[..., Any],
) -> Callable[[starlette.requests.Request], Awaitable[starlette.responses.Response]]:
    """Builds a Starlette endpoint for one unary RPC method.

    Args:
        request_type: Protobuf request message type.
        handler: RPC handler function.

    Returns:
        Starlette endpoint coroutine function.
    """

    async def endpoint(
        request: starlette.requests.Request,
    ) -> starlette.responses.Response:
        """Handles one unary RPC request."""
        return await _connect.handle_rpc(request, request_type, handler)

    return endpoint


class ProblemSupportApplication:
    """ASGI application exposing the problem support RPC API."""

    def __init__(
        self,
        *,
        input_type: type[problemlib.BaseInput],
        output_type: type[problemlib.BaseOutput],
        rank_sort: int,
        score_decimal_places: int = 0,
        statements: Iterable[Statement | problem_support_pb2.StatementInfo] = (),
    ) -> None:
        """Create an ASGI problem support application.

        Args:
            input_type: The problem's Input class.
            output_type: The problem's Output class.
            rank_sort: Optimization direction; use minimization if lower scores
                are better, maximization if higher scores are better.
            score_decimal_places: Number of decimal places in the score.
            statements: Statements to include in GetProblemInfo responses.
                Root-relative URLs (e.g. ``/statement.pdf``) are resolved
                against each request's origin.
        """
        self._input_type = input_type
        self._output_type = output_type
        self._rank_sort = rank_sort
        self._score_decimal_places = score_decimal_places
        self._statements = tuple(statements)

        handlers = {
            "GenerateInput": self._handle_generate_input,
            "GetProblemInfo": self._handle_get_problem_info,
            "Solve": self._handle_solve,
            "VerifyInput": self._handle_verify_input,
            "VerifyOutput": self._handle_verify_output,
        }
        routes = [
            starlette.routing.Route(
                f"/{method.containing_service.full_name}/{method.name}",
                endpoint=_make_rpc_endpoint(
                    getattr(problem_support_pb2, method.input_type.name),
                    handlers[method.name],
                ),
                methods=["POST"],
            )
            for method in _SERVICE_DESCRIPTOR.methods
        ]
        self._app = starlette.applications.Starlette(routes=routes)

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        """Dispatches an ASGI request to the underlying Starlette app.

        Args:
            scope: ASGI connection scope.
            receive: ASGI receive callable.
            send: ASGI send callable.
        """
        await self._app(scope, receive, send)

    def _handle_generate_input(
        self,
        request: problem_support_pb2.GenerateInputRequest,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.GenerateInputResponse:
        """Handles a GenerateInput RPC.

        Args:
            request: GenerateInput request.
            scope: ASGI scope for the request.

        Returns:
            GenerateInput response.

        Raises:
            _connect.ConnectError: Input generation is not implemented.
        """
        del scope
        if not self._supports_generate_input():
            raise _connect.ConnectError(
                "unimplemented", "generate_input is not implemented"
            )
        seed = request.seed if request.HasField("seed") else None
        generated = self._input_type.generate(random.Random(seed))
        return problem_support_pb2.GenerateInputResponse(
            content=_write_to_bytes(generated)
        )

    def _handle_get_problem_info(
        self,
        _request: problem_support_pb2.GetProblemInfoRequest,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.GetProblemInfoResponse:
        """Handles a GetProblemInfo RPC.

        Args:
            _request: GetProblemInfo request.
            scope: ASGI scope for resolving root-relative statement URLs.

        Returns:
            Problem metadata response.
        """
        return problem_support_pb2.GetProblemInfoResponse(
            rank_sort=self._rank_sort,
            score_decimal_places=self._score_decimal_places,
            statements=[
                self._statement_to_proto(statement, scope=scope)
                for statement in self._statements
            ],
            supported_solvers=self._supported_solvers(),
            supports_generate_input=self._supports_generate_input(),
        )

    def _handle_solve(
        self,
        request: problem_support_pb2.SolveRequest,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.SolveResponse:
        """Handles a Solve RPC.

        Args:
            request: Solve request.
            scope: ASGI scope for the request.

        Returns:
            Solve response.

        Raises:
            _connect.ConnectError: The input is invalid or solver is unsupported.
        """
        del scope
        try:
            parsed_input = self._input_type.read(io.BytesIO(request.input_content))
        except problemlib.FileFormatError as exc:
            raise _connect.ConnectError("invalid_argument", str(exc)) from exc

        solver_name = _SOLVER_NAMES.get(request.solver_type)
        solver = (
            getattr(parsed_input, solver_name, None)
            if solver_name is not None
            else None
        )
        if not callable(solver):
            raise _connect.ConnectError("unimplemented", "solver is not implemented")

        output = solver()
        return problem_support_pb2.SolveResponse(output_content=_write_to_bytes(output))

    def _handle_verify_input(
        self,
        request: problem_support_pb2.VerifyInputRequest,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.VerifyInputResponse:
        """Handles a VerifyInput RPC.

        Args:
            request: VerifyInput request.
            scope: ASGI scope for the request.

        Returns:
            VerifyInput response.
        """
        del scope
        try:
            parsed = self._input_type.read(io.BytesIO(request.content))
        except problemlib.FileFormatError as exc:
            return problem_support_pb2.VerifyInputResponse(format_error=str(exc))
        return problem_support_pb2.VerifyInputResponse(
            normalized_content=_write_to_bytes(parsed)
        )

    def _handle_verify_output(
        self,
        request: problem_support_pb2.VerifyOutputRequest,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.VerifyOutputResponse:
        """Handles a VerifyOutput RPC.

        Args:
            request: VerifyOutput request.
            scope: ASGI scope for the request.

        Returns:
            VerifyOutput response.
        """
        del scope
        try:
            parsed_input = self._input_type.read(io.BytesIO(request.input_content))
            parsed_output = self._output_type.read(
                parsed_input, io.BytesIO(request.output_content)
            )
        except problemlib.FileFormatError as exc:
            return problem_support_pb2.VerifyOutputResponse(format_error=str(exc))

        verified = problem_support_pb2.VerifiedOutput(
            normalized_content=_write_to_bytes(parsed_output),
            reported_score=parsed_output.score,
        )

        try:
            self._verify_output_score(parsed_output, verified)
        except problemlib.VerificationError as exc:
            verified.rejected.CopyFrom(
                problem_support_pb2.RejectedOutput(rejection_reason=str(exc))
            )

        return problem_support_pb2.VerifyOutputResponse(output=verified)

    def _verify_output_score(
        self,
        parsed_output: problemlib.BaseOutput,
        verified: problem_support_pb2.VerifiedOutput,
    ) -> None:
        """Populates verification fields on a verified output.

        Args:
            parsed_output: Parsed output to verify.
            verified: Protobuf response object to mutate.
        """
        try:
            actual_score = parsed_output.compute_actual_score()
        except NotImplementedError:
            parsed_output.verify()
            verified.accepted.CopyFrom(problem_support_pb2.AcceptedOutput())
            return

        verified.actual_score = actual_score
        if actual_score == parsed_output.score:
            verified.accepted.CopyFrom(problem_support_pb2.AcceptedOutput())
        else:
            verified.rejected.CopyFrom(
                problem_support_pb2.RejectedOutput(
                    rejection_reason=(
                        f"Reported score ({parsed_output.score}) does not match actual "
                        f"({actual_score})"
                    )
                )
            )

    def _statement_to_proto(
        self,
        statement: Statement | problem_support_pb2.StatementInfo,
        *,
        scope: dict[str, Any] | None = None,
    ) -> problem_support_pb2.StatementInfo:
        """Converts local statement metadata to protobuf metadata.

        Args:
            statement: Statement metadata.
            scope: ASGI scope for resolving root-relative URLs.

        Returns:
            Statement metadata protobuf.

        Raises:
            TypeError: The statement has an unsupported type.
        """
        if isinstance(statement, problem_support_pb2.StatementInfo):
            return statement
        if not isinstance(statement, Statement):
            raise TypeError("statement must be a Statement or StatementInfo")
        return problem_support_pb2.StatementInfo(
            format=statement.format.value,
            url=_resolve_url(statement.url, scope),
        )

    def _supported_solvers(self) -> list[problem_support_pb2.SolverInfo]:
        """Returns solvers supported by the input type.

        Returns:
            Solver metadata protobufs.
        """
        solvers = []
        if self._input_type.trivial_solve is not problemlib.BaseInput.trivial_solve:
            solvers.append(
                problem_support_pb2.SolverInfo(
                    solver_type=problem_support_pb2.SOLVER_TYPE_TRIVIAL
                )
            )
        return solvers

    def _supports_generate_input(self) -> bool:
        """Returns whether the input type implements generation.

        Returns:
            True if GenerateInput is supported.
        """
        return (
            self._input_type.generate.__func__
            is not problemlib.BaseInput.generate.__func__
        )


def _write_to_bytes(value: problemlib.BaseInput | problemlib.BaseOutput) -> bytes:
    """Writes a problem value to UTF-8 bytes.

    Args:
        value: Input or output object to write.

    Returns:
        Serialized value bytes.
    """
    buffer = io.BytesIO()
    text = io.TextIOWrapper(buffer, encoding="utf-8", write_through=True)
    value.write(text)
    text.flush()
    return buffer.getvalue()
