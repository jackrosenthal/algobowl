# algobowl-python-problem-server

ASGI problem server support for AlgoBOWL problem packages.

This package implements the `ProblemSupportService` protobuf API over unary
Connect-compatible HTTP. Problem packages provide their `Input` and `Output`
types from `algobowl-python-problem-support`; this package handles request
routing, protobuf serialization, input normalization, output verification, input
generation, and trivial solving.

## Usage

Create an ASGI application from the problem's input and output types:

```python
import algops.app
import problem

app = algops.app.ProblemSupportApplication(
    input_type=problem.Input,
    output_type=problem.Output,
    score_decimal_places=0,
    statements=[
        algops.app.Statement.pdf("https://example.com/statement.pdf"),
    ],
)
```

For Cloudflare Workers Python, bridge the ASGI app with the runtime-provided
`asgi` module:

```python
import asgi
import problem_server
import workers


class Default(workers.WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(problem_server.app, request, self.env)
```

## Supported Problem Hooks

The input type may implement:

- `Input.generate(rng)` to support `GenerateInput`
- `Input.trivial_solve()` to support `Solve` with `SOLVER_TYPE_TRIVIAL`

The output type may implement either:

- `Output.compute_actual_score()` to report `actual_score` and compare it with
  the submitted score
- `Output.verify()` for problems that can verify validity but do not compute an
  independent score

`FileFormatError` becomes a format error response. `VerificationError` becomes a
rejected output response. Other exceptions are treated as server bugs.

## Protocol

The server accepts unary Connect protobuf requests:

- `POST /algobowl.problemsupport.v1.ProblemSupportService/GetProblemInfo`
- `POST /algobowl.problemsupport.v1.ProblemSupportService/VerifyInput`
- `POST /algobowl.problemsupport.v1.ProblemSupportService/VerifyOutput`
- `POST /algobowl.problemsupport.v1.ProblemSupportService/GenerateInput`
- `POST /algobowl.problemsupport.v1.ProblemSupportService/Solve`

Requests and successful responses use `Content-Type: application/proto` with raw
protobuf message bodies. Errors use Connect-style JSON bodies:

```json
{"code": "invalid_argument", "message": "..."}
```

## Protobuf Generation

The generated protobuf files are committed under `src/algops/proto/`.

From the repository root:

```sh
buf format -w
buf lint
buf generate
```

`buf.gen.yaml` uses Buf remote plugins and does not require a local `protoc`.
