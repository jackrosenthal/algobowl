# -*- coding: utf-8 -*-
"""The base Controller API."""

import tg

__all__ = ["BaseController"]


class BaseController(tg.TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, context):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to.

        tg.tmpl_context.identity = tg.request.identity
        environ["is_admin"] = tg.predicates.has_permission("admin").is_met(environ)
        return super().__call__(environ, context)
