import collections.abc
import dataclasses
import enum
import io
import random

import algobowl.lib.problem
from algops import _connect
from algops.proto.algobowl.problemsupport.v1 import problem_support_pb2


_RANK_SORT_TO_PROTO = {
    algobowl.lib.problem.RankSort.minimization: problem_support_pb2.RANK_SORT_MINIMIZATION,
    algobowl.lib.problem.RankSort.maximization: problem_support_pb2.RANK_SORT_MAXIMIZATION,
}

_SOLVER_NAMES = {
    problem_support_pb2.SOLVER_TYPE_TRIVIAL: "trivial_solve",
}


class StatementFormat(enum.Enum):
    MARKDOWN = problem_support_pb2.STATEMENT_FORMAT_MARKDOWN
    PDF = problem_support_pb2.STATEMENT_FORMAT_PDF


@dataclasses.dataclass(frozen=True)
class Statement:
    format: StatementFormat
    url: str

    @classmethod
    def markdown(cls, url):
        return cls(format=StatementFormat.MARKDOWN, url=url)

    @classmethod
    def pdf(cls, url):
        return cls(format=StatementFormat.PDF, url=url)


class ProblemSupportApplication:
    def __init__(
        self,
        *,
        input_type,
        output_type,
        score_decimal_places=0,
        statements=(),
    ):
        self._input_type = input_type
        self._output_type = output_type
        self._score_decimal_places = score_decimal_places
        self._statements = tuple(statements)
        self._handlers = {
            "/algobowl.problemsupport.v1.ProblemSupportService/GenerateInput": (
                problem_support_pb2.GenerateInputRequest,
                self._handle_generate_input,
            ),
            "/algobowl.problemsupport.v1.ProblemSupportService/GetProblemInfo": (
                problem_support_pb2.GetProblemInfoRequest,
                self._handle_get_problem_info,
            ),
            "/algobowl.problemsupport.v1.ProblemSupportService/Solve": (
                problem_support_pb2.SolveRequest,
                self._handle_solve,
            ),
            "/algobowl.problemsupport.v1.ProblemSupportService/VerifyInput": (
                problem_support_pb2.VerifyInputRequest,
                self._handle_verify_input,
            ),
            "/algobowl.problemsupport.v1.ProblemSupportService/VerifyOutput": (
                problem_support_pb2.VerifyOutputRequest,
                self._handle_verify_output,
            ),
        }

    async def __call__(self, scope, receive, send):
        response = await _connect.dispatch(scope, receive, self._handlers)
        await _connect.send_response(send, response)

    def _handle_generate_input(self, request):
        if not self._supports_generate_input():
            raise _connect.ConnectError("unimplemented", "generate_input is not implemented")
        seed = request.seed if request.HasField("seed") else None
        generated = self._input_type.generate(random.Random(seed))
        return problem_support_pb2.GenerateInputResponse(content=_write_to_bytes(generated))

    def _handle_get_problem_info(self, _request):
        return problem_support_pb2.GetProblemInfoResponse(
            rank_sort=_RANK_SORT_TO_PROTO[self._output_type.rank_sort],
            score_decimal_places=self._score_decimal_places,
            statements=[self._statement_to_proto(statement) for statement in self._statements],
            supported_solvers=self._supported_solvers(),
            supports_generate_input=self._supports_generate_input(),
        )

    def _handle_solve(self, request):
        try:
            parsed_input = self._input_type.read(io.BytesIO(request.input_content))
        except algobowl.lib.problem.FileFormatError as exc:
            raise _connect.ConnectError("invalid_argument", str(exc)) from exc

        solver_name = _SOLVER_NAMES.get(request.solver_type)
        solver = getattr(parsed_input, solver_name, None) if solver_name is not None else None
        if not callable(solver):
            raise _connect.ConnectError("unimplemented", "solver is not implemented")

        output = solver()
        return problem_support_pb2.SolveResponse(output_content=_write_to_bytes(output))

    def _handle_verify_input(self, request):
        try:
            parsed = self._input_type.read(io.BytesIO(request.content))
        except algobowl.lib.problem.FileFormatError as exc:
            return problem_support_pb2.VerifyInputResponse(format_error=str(exc))
        return problem_support_pb2.VerifyInputResponse(normalized_content=_write_to_bytes(parsed))

    def _handle_verify_output(self, request):
        try:
            parsed_input = self._input_type.read(io.BytesIO(request.input_content))
            parsed_output = self._output_type.read(
                parsed_input, io.BytesIO(request.output_content)
            )
        except algobowl.lib.problem.FileFormatError as exc:
            return problem_support_pb2.VerifyOutputResponse(format_error=str(exc))

        verified = problem_support_pb2.VerifiedOutput(
            normalized_content=_write_to_bytes(parsed_output),
            reported_score=parsed_output.score,
        )

        try:
            self._verify_output_score(parsed_output, verified)
        except algobowl.lib.problem.VerificationError as exc:
            verified.rejected.CopyFrom(
                problem_support_pb2.RejectedOutput(rejection_reason=str(exc))
            )

        return problem_support_pb2.VerifyOutputResponse(output=verified)

    def _verify_output_score(self, parsed_output, verified):
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

    def _statement_to_proto(self, statement):
        if isinstance(statement, problem_support_pb2.StatementInfo):
            return statement
        if not isinstance(statement, Statement):
            raise TypeError("statement must be a Statement or StatementInfo")
        return problem_support_pb2.StatementInfo(
            format=statement.format.value,
            url=statement.url,
        )

    def _supported_solvers(self):
        solvers = []
        if (
            self._input_type.trivial_solve
            is not algobowl.lib.problem.BaseInput.trivial_solve
        ):
            solvers.append(
                problem_support_pb2.SolverInfo(
                    solver_type=problem_support_pb2.SOLVER_TYPE_TRIVIAL
                )
            )
        return solvers

    def _supports_generate_input(self):
        return (
            self._input_type.generate.__func__
            is not algobowl.lib.problem.BaseInput.generate.__func__
        )


def _write_to_bytes(value):
    buffer = io.BytesIO()
    text = io.TextIOWrapper(buffer, encoding="utf-8", write_through=True)
    value.write(text)
    text.flush()
    return buffer.getvalue()
