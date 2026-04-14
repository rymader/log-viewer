"""Domain model representing a log query."""

from datetime import datetime


class LogQuery:
    """Represents the parameters for a log query.

    Acts as a plain data transfer object passed from the UI layer to
    the reader layer. Contains no reader-specific formatting — each
    reader is responsible for translating these fields into its own
    query syntax.

    Attributes:
        start: The inclusive start of the time range to query.
        end: The inclusive end of the time range to query.
        filter_pattern: An optional regex pattern to filter log entries.
            An empty string means no filtering is applied.

    Args:
        start: The inclusive start of the time range to query.
        end: The inclusive end of the time range to query.
        filter_pattern: An optional regex pattern to filter log entries.
            Defaults to empty string (no filter).
    """

    def __init__(self, start: datetime, end: datetime, filter_pattern: str = ''):
        self.start = start
        self.end = end
        self.filter_pattern = filter_pattern
