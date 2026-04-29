from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RankSort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANK_SORT_UNSPECIFIED: _ClassVar[RankSort]
    RANK_SORT_MINIMIZATION: _ClassVar[RankSort]
    RANK_SORT_MAXIMIZATION: _ClassVar[RankSort]

class StatementFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATEMENT_FORMAT_UNSPECIFIED: _ClassVar[StatementFormat]
    STATEMENT_FORMAT_PDF: _ClassVar[StatementFormat]
    STATEMENT_FORMAT_MARKDOWN: _ClassVar[StatementFormat]

class SolverType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOLVER_TYPE_UNSPECIFIED: _ClassVar[SolverType]
    SOLVER_TYPE_TRIVIAL: _ClassVar[SolverType]
    SOLVER_TYPE_BENCH1: _ClassVar[SolverType]
    SOLVER_TYPE_BENCH2: _ClassVar[SolverType]

RANK_SORT_UNSPECIFIED: RankSort
RANK_SORT_MINIMIZATION: RankSort
RANK_SORT_MAXIMIZATION: RankSort
STATEMENT_FORMAT_UNSPECIFIED: StatementFormat
STATEMENT_FORMAT_PDF: StatementFormat
STATEMENT_FORMAT_MARKDOWN: StatementFormat
SOLVER_TYPE_UNSPECIFIED: SolverType
SOLVER_TYPE_TRIVIAL: SolverType
SOLVER_TYPE_BENCH1: SolverType
SOLVER_TYPE_BENCH2: SolverType

class StatementInfo(_message.Message):
    __slots__ = ("format", "url")
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    format: StatementFormat
    url: str
    def __init__(
        self,
        format: _Optional[_Union[StatementFormat, str]] = ...,
        url: _Optional[str] = ...,
    ) -> None: ...

class SolverInfo(_message.Message):
    __slots__ = ("solver_type",)
    SOLVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    solver_type: SolverType
    def __init__(
        self, solver_type: _Optional[_Union[SolverType, str]] = ...
    ) -> None: ...

class GetProblemInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProblemInfoResponse(_message.Message):
    __slots__ = (
        "rank_sort",
        "score_decimal_places",
        "statements",
        "supported_solvers",
        "supports_generate_input",
    )
    RANK_SORT_FIELD_NUMBER: _ClassVar[int]
    SCORE_DECIMAL_PLACES_FIELD_NUMBER: _ClassVar[int]
    STATEMENTS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_SOLVERS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_GENERATE_INPUT_FIELD_NUMBER: _ClassVar[int]
    rank_sort: RankSort
    score_decimal_places: int
    statements: _containers.RepeatedCompositeFieldContainer[StatementInfo]
    supported_solvers: _containers.RepeatedCompositeFieldContainer[SolverInfo]
    supports_generate_input: bool
    def __init__(
        self,
        rank_sort: _Optional[_Union[RankSort, str]] = ...,
        score_decimal_places: _Optional[int] = ...,
        statements: _Optional[_Iterable[_Union[StatementInfo, _Mapping]]] = ...,
        supported_solvers: _Optional[_Iterable[_Union[SolverInfo, _Mapping]]] = ...,
        supports_generate_input: _Optional[bool] = ...,
    ) -> None: ...

class VerifyInputRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    def __init__(self, content: _Optional[bytes] = ...) -> None: ...

class VerifyInputResponse(_message.Message):
    __slots__ = ("normalized_content", "format_error")
    NORMALIZED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_ERROR_FIELD_NUMBER: _ClassVar[int]
    normalized_content: bytes
    format_error: str
    def __init__(
        self,
        normalized_content: _Optional[bytes] = ...,
        format_error: _Optional[str] = ...,
    ) -> None: ...

class AcceptedOutput(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RejectedOutput(_message.Message):
    __slots__ = ("rejection_reason",)
    REJECTION_REASON_FIELD_NUMBER: _ClassVar[int]
    rejection_reason: str
    def __init__(self, rejection_reason: _Optional[str] = ...) -> None: ...

class VerifiedOutput(_message.Message):
    __slots__ = (
        "normalized_content",
        "reported_score",
        "actual_score",
        "accepted",
        "rejected",
    )
    NORMALIZED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    REPORTED_SCORE_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_SCORE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    normalized_content: bytes
    reported_score: int
    actual_score: int
    accepted: AcceptedOutput
    rejected: RejectedOutput
    def __init__(
        self,
        normalized_content: _Optional[bytes] = ...,
        reported_score: _Optional[int] = ...,
        actual_score: _Optional[int] = ...,
        accepted: _Optional[_Union[AcceptedOutput, _Mapping]] = ...,
        rejected: _Optional[_Union[RejectedOutput, _Mapping]] = ...,
    ) -> None: ...

class VerifyOutputRequest(_message.Message):
    __slots__ = ("input_content", "output_content")
    INPUT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    input_content: bytes
    output_content: bytes
    def __init__(
        self,
        input_content: _Optional[bytes] = ...,
        output_content: _Optional[bytes] = ...,
    ) -> None: ...

class VerifyOutputResponse(_message.Message):
    __slots__ = ("output", "format_error")
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_ERROR_FIELD_NUMBER: _ClassVar[int]
    output: VerifiedOutput
    format_error: str
    def __init__(
        self,
        output: _Optional[_Union[VerifiedOutput, _Mapping]] = ...,
        format_error: _Optional[str] = ...,
    ) -> None: ...

class GenerateInputRequest(_message.Message):
    __slots__ = ("seed",)
    SEED_FIELD_NUMBER: _ClassVar[int]
    seed: int
    def __init__(self, seed: _Optional[int] = ...) -> None: ...

class GenerateInputResponse(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    def __init__(self, content: _Optional[bytes] = ...) -> None: ...

class SolveRequest(_message.Message):
    __slots__ = ("input_content", "solver_type")
    INPUT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SOLVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    input_content: bytes
    solver_type: SolverType
    def __init__(
        self,
        input_content: _Optional[bytes] = ...,
        solver_type: _Optional[_Union[SolverType, str]] = ...,
    ) -> None: ...

class SolveResponse(_message.Message):
    __slots__ = ("output_content",)
    OUTPUT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    output_content: bytes
    def __init__(self, output_content: _Optional[bytes] = ...) -> None: ...
