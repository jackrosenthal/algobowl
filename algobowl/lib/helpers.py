"""
Template Helpers for AlgoBOWL
-----------------------------

This module is exposed in all templates under the name ``h``.
"""

import datetime

import tg


def ftime(dt, duration=None):
    """Format a ``datetime`` object as HTML for view on the page.

    Localtime is normally handled by the browser.  We create <time> elements
    here, and allow client-side javascript to re-format the displayed time.

    Args:
        dt: A datetime object to format.
        duration: An optional datetime or timedelta for the ending time.

    Returns:
        A HTML string.
    """
    fallback_datetime_format = tg.config.get(
        "locale.fallback_datetime_format", "%B %-d, %Y at %-I:%M %p"
    )

    fallback = dt.strftime(fallback_datetime_format)
    timestamp = dt.astimezone().isoformat()

    result = f'<time datetime="{timestamp}">{fallback}</time>'
    if duration:
        if isinstance(duration, datetime.timedelta):
            # convert a duration to an end date
            duration = dt + duration
        if duration < dt:
            raise ValueError("Duration cannot be before the specified time")
        result += f" to {ftime(duration)}"
    return result


def url(path: str) -> str:
    try:
        from algobowl.lib import algocdn
    except ImportError:
        pass
    else:
        try:
            return algocdn.url_map[path]
        except KeyError:
            pass
    return tg.url(path)
