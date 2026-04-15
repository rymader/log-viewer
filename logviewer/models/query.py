"""Domain model representing a log query."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LogQuery:
    """Represents the parameters for a log query.

    Acts as a plain data transfer object passed from the UI layer to
    the reader layer. Contains no reader-specific formatting — each
    reader is responsible for translating these fields into its own
    query syntax.

    :param start: The inclusive start of the time range to query.
    :param end: The inclusive end of the time range to query.
    :param filter_pattern: An optional regex pattern to filter log entries.
        Defaults to empty string (no filter).
    :raises ValueError: If start is later than end.
    """

    start: datetime
    end: datetime
    filter_pattern: str = ''

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(
                f"start must be earlier than or equal to end "
                f"(got start={self.start!r}, end={self.end!r})"
            )
