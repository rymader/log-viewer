"""Pure validation logic for the toolbar's date/time range inputs.

Kept in a GTK-free module so it can be tested without a display.
"""

from dataclasses import dataclass
from datetime import datetime, time

from logviewer.models.query import LogQuery

_START_OF_DAY = time(0, 0, 0)
_END_OF_DAY = time(23, 59, 59)


@dataclass(frozen=True)
class ValidationResult:
    """The outcome of validating the toolbar's current field values.

    :param ready: Whether the form is ready to submit (button should be enabled).
    :param error: Error message to display, or None if the label should be hidden.
    :param query: The constructed LogQuery when ready is True, otherwise None.
    """

    ready: bool
    error: str | None
    query: LogQuery | None


def _apply_time(dt: datetime, time_str: str, default: time) -> datetime:
    """Apply a time string to a date, falling back to a default if unparseable.

    :param dt: The base date to apply the time to.
    :param time_str: A time string in HH:MM:SS format. If empty or
        incomplete, default is used instead.
    :param default: Default time if time_str cannot be parsed.
    :returns: The datetime with the time component applied.
    """
    try:
        return datetime.combine(dt.date(), datetime.strptime(time_str, "%H:%M:%S").time())
    except ValueError:
        return datetime.combine(dt.date(), default)


def compute_validation(
    start_date_str: str,
    end_date_str: str,
    start_time_str: str,
    end_time_str: str,
    date_format: str,
) -> ValidationResult:
    """Validate toolbar field values and build a LogQuery if they are valid.

    Distinguishes four states:

    - Incomplete: a date field cannot be parsed, or a time field has
      partial input. Returns ready=False, error=None.
    - Invalid time: a fully entered time field has an out-of-range value
      (e.g. hour > 23). Returns ready=False with an error message.
    - Invalid range: all fields parse but start is later than end.
      Returns ready=False with an error message.
    - Valid: all fields are acceptable. Returns ready=True and a LogQuery.

    :param start_date_str: Raw text from the start date entry.
    :param end_date_str: Raw text from the end date entry.
    :param start_time_str: Raw text from the start time entry (may be empty).
    :param end_time_str: Raw text from the end time entry (may be empty).
    :param date_format: strptime-style format string for parsing date fields.
    :returns: A ValidationResult describing the current state.
    """
    try:
        start = datetime.strptime(start_date_str, date_format)
        end = datetime.strptime(end_date_str, date_format)
    except ValueError:
        return ValidationResult(ready=False, error=None, query=None)

    for time_str in (start_time_str, end_time_str):
        if not time_str:
            continue  # empty — _apply_time will use the day boundary default
        if len(time_str) < 8:
            # Partial input — not ready yet, but not a user error
            return ValidationResult(ready=False, error=None, query=None)
        try:
            datetime.strptime(time_str, "%H:%M:%S")
        except ValueError:
            return ValidationResult(
                ready=False,
                error="Invalid time value (hours: 00\u201323, minutes/seconds: 00\u201359)",
                query=None,
            )

    start = _apply_time(start, start_time_str, _START_OF_DAY)
    end = _apply_time(end, end_time_str, _END_OF_DAY)

    if start > end:
        return ValidationResult(
            ready=False,
            error="End date/time must be on or after start date/time",
            query=None,
        )

    return ValidationResult(ready=True, error=None, query=LogQuery(start, end))
