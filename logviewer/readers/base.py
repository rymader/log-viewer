"""Abstract base class defining the log reader interface."""

from abc import ABC, abstractmethod

from logviewer.models.query import LogQuery


class LogReader(ABC):
    """Interface for all log reader implementations.

    Defines the contract that every concrete log reader must fulfil.
    The UI layer depends only on this interface, never on a concrete
    implementation, keeping the reader backend swappable without
    touching any UI code.
    """

    @abstractmethod
    def read_logs(self, query: LogQuery) -> str:
        """Fetch log entries matching the given query.

        :param query: The query parameters including time range and
            optional filter pattern.
        :returns: The log output as a plain string. Returns an empty string
            if no entries matched the query.
        """
