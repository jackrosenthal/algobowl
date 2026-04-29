# algobowl-python-problem-server

ASGI problem server support for AlgoBOWL problem packages.

This package implements the `ProblemSupportService` protobuf API over unary
Connect-compatible HTTP. Problem packages provide their `Input` and `Output`
types by subclassing helpers in `algops.problemlib`; this package handles
request routing, protobuf serialization, input normalization, output
verification, input generation, and trivial solving.

## Usage

Create an ASGI application from the problem's input and output types, and
bridge it with the Cloudflare Workers runtime-provided `asgi` module:

```python
import asgi
import algops.app
import workers
import problem

app = algops.app.ProblemSupportApplication(
    input_type=problem.Input,
    output_type=problem.Output,
    rank_sort=algops.app.RANK_SORT_MINIMIZATION,
    score_decimal_places=0,
    statements=[
        algops.app.Statement.pdf("/statement.pdf"),
        algops.app.Statement.markdown("/statement.md"),
    ],
)


class Default(workers.WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
```

Root-relative statement URLs (e.g. `"/statement.pdf"`) are resolved against
the request origin at runtime, so the same worker code works in both local
development and production without any configuration changes. Serve the
statement files as static assets via `[assets]` in `wrangler.jsonc`.

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
