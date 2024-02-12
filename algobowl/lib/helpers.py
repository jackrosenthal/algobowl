"""
Template Helpers for AlgoBOWL
-----------------------------

This module is exposed in all templates under the name ``h``.
"""

from datetime import date, datetime, time, timedelta

import tg


def ftime(dt, duration=None, show_day=False):
    """
    Format a ``date``, ``datetime``, or ``time`` object for view on
    the page. Optionally takes a duration to show a range of time.

    :param dt: A ``date``, ``datetime`` or ``time`` to format.
    :param duration: A ``timedelta`` indicating how long something
                     lasts.
    :param show_day: Show the day of the week.
    :rtype: string
    """
    if show_day:
        date_fmt = tg.config.get("locale.dow_date_fmt", "%A, %B %-d, %Y")
    else:
        date_fmt = tg.config.get("locale.date_fmt", "%B %-d, %Y")
    time_fmt = tg.config.get("locale.time_fmt", "%-I:%M %p")
    dt_sep = tg.config.get("locale.dt_sep", " at ")
    dt_duration_sep = tg.config.get("locale.dt_duration_sep", " from ")
    duration_time_sep = tg.config.get("locale.duration_time_sep", " to ")

    if isinstance(duration, timedelta):
        # convert a duration to an end date
        duration = dt + duration

    if duration is not None and duration < dt:
        raise ValueError("Duration cannot be before the specified time")

    if isinstance(dt, datetime):
        if duration is None:
            # Format date without duration
            return dt.strftime(date_fmt + dt_sep + time_fmt)
        elif isinstance(duration, datetime):
            # Format date with duration
            start = (
                dt.strftime(date_fmt + dt_duration_sep + time_fmt) + duration_time_sep
            )
            if dt.date() == duration.date():
                return start + duration.strftime(time_fmt)
            return start + duration.strftime(date_fmt + dt_sep + time_fmt)
        else:
            raise TypeError("duration must be a timedelta or datetime")

    if isinstance(dt, date):
        return dt.strftime(date_fmt)

    if isinstance(dt, time):
        return dt.strftime(time_fmt)
