import contextlib
import functools
import io

from tg import expose

__all__ = ["logoutput"]


def logoutput(meth):
    """Decorator to use log output"""

    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            meth(*args, **kwargs)
        return {"content": buf.getvalue()}

    return expose("algobowl.templates.logoutput")(wrapper)
