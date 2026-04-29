"""Connect protobuf unary RPC handling."""

from __future__ import annotations

import json

import starlette.requests
import starlette.responses
from google.protobuf import message as proto_message

_ERROR_STATUS = {
    "canceled": 408,
    "internal": 500,
    "invalid_argument": 400,
    "not_found": 404,
    "unimplemented": 501,
    "unknown": 500,
}

_PROTO_CONTENT_TYPE = "application/proto"


class ConnectError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _error_response(code: str, msg: str) -> starlette.responses.Response:
    body = json.dumps({"code": code, "message": msg}).encode("utf-8")
    status = _ERROR_STATUS.get(code, 500)
    return starlette.responses.Response(
        content=body,
        status_code=status,
        media_type="application/json",
    )


async def handle_rpc(
    request: starlette.requests.Request,
    request_type,
    handler,
) -> starlette.responses.Response:
    """Dispatch a Connect unary protobuf RPC from a Starlette request."""
    content_type = (
        request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    )
    if content_type != _PROTO_CONTENT_TYPE:
        return _error_response("invalid_argument", "unsupported content type")
    try:
        payload = await request.body()
        proto_request = request_type()
        proto_request.ParseFromString(payload)
        response_proto = handler(proto_request, scope=request.scope)
        return starlette.responses.Response(
            content=response_proto.SerializeToString(),
            media_type=_PROTO_CONTENT_TYPE,
        )
    except ConnectError as exc:
        return _error_response(exc.code, exc.message)
    except proto_message.DecodeError as exc:
        return _error_response("invalid_argument", str(exc))
