"""Minimal ASGI transport for unary Connect protobuf RPCs."""

import json

from google.protobuf import message


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
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def make_response(body, content_type="application/proto", status=200):
    return {
        "body": body,
        "headers": [(b"content-type", content_type.encode("ascii"))],
        "status": status,
    }


def make_error(code, message):
    body = json.dumps({"code": code, "message": message}).encode("utf-8")
    status = _ERROR_STATUS.get(code, 500)
    return make_response(body, content_type="application/json", status=status)


async def dispatch(scope, receive, handlers):
    if scope["type"] != "http":
        return make_error("unimplemented", "only http is supported")
    if scope["method"].upper() != "POST":
        return make_error("unimplemented", "only POST is supported")

    route = handlers.get(scope["path"])
    if route is None:
        return make_error("not_found", "rpc method not found")

    content_type = _content_type(scope)
    if content_type != _PROTO_CONTENT_TYPE:
        return make_error("invalid_argument", "unsupported content type")

    request_type, handler = route
    try:
        payload = await read_body(receive)
        message = request_type()
        message.ParseFromString(payload)
        response = handler(message)
        return make_response(response.SerializeToString())
    except ConnectError as exc:
        return make_error(exc.code, exc.message)
    except message.DecodeError as exc:
        return make_error("invalid_argument", str(exc))


async def read_body(receive):
    chunks = []
    while True:
        message = await receive()
        if message["type"] != "http.request":
            raise ConnectError("invalid_argument", "unexpected asgi message")
        body = message.get("body", b"")
        if body:
            chunks.append(body)
        if not message.get("more_body", False):
            return b"".join(chunks)


async def send_response(send, response):
    await send(
        {
            "headers": response["headers"],
            "status": response["status"],
            "type": "http.response.start",
        }
    )
    await send(
        {
            "body": response["body"],
            "more_body": False,
            "type": "http.response.body",
        }
    )


def _content_type(scope):
    for name, value in scope.get("headers", ()):
        if name.decode("latin-1").lower() == "content-type":
            return value.decode("latin-1").split(";", 1)[0].strip().lower()
    return ""
