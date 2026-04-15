"""Utilities for detecting system locale settings."""

import locale


def detect_date_format() -> str:
    """Detect the preferred date format from the system locale.

    Sets the process locale to the system default (empty string) and
    reads the date format via nl_langinfo. This should be called once
    at application startup — setting the locale is a process-wide
    side effect and should not be done inside widget constructors.

    The result is a strptime-compatible format string that reflects
    the user's regional date ordering (e.g. '%m/%d/%Y' for US,
    '%d/%m/%Y' for UK).

    :returns: A strptime-style date format string derived from the system
        locale. Falls back to ISO format ('%Y-%m-%d') if the locale
        cannot be determined or does not contain recognised date tokens.
    """
    try:
        locale.setlocale(locale.LC_TIME, '')
        fmt = locale.nl_langinfo(locale.D_FMT)
        if fmt and any(t in fmt for t in ('%d', '%m', '%Y', '%y')):
            return fmt
    except (locale.Error, AttributeError):
        pass
    return '%Y-%m-%d'
