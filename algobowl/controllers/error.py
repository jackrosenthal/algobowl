from tg import expose, request

from algobowl.lib.base import BaseController

__all__ = ["ErrorController"]


class ErrorController(BaseController):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """

    @expose("algobowl.templates.error")
    @expose("json")
    def document(self, *args, **kwargs):
        """Render the error document"""
        resp = request.environ.get("tg.original_response")
        try:
            # tg.abort exposes the message as .detail in response
            message = resp.detail
        except Exception:
            message = None

        if hasattr(resp, "status_int"):
            code = resp.status_int
        else:
            code = 404

        if not message:
            message = "We're sorry but we weren't able to process this request."

        values = dict(
            prefix=request.environ.get("SCRIPT_NAME", ""),
            code=request.params.get("code", code),
            message=request.params.get("message", message),
        )
        return values
