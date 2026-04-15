"""Log reader implementation backed by the systemd journalctl command."""

import shutil
import subprocess

from logviewer.models.query import LogQuery
from logviewer.readers.base import LogReader, LogReadError


class JournalctlLogReader(LogReader):
    """Reads system logs by invoking the journalctl command-line tool.

    Translates a LogQuery into a journalctl invocation, capturing
    stdout as the return value. Requires journalctl to be available
    on the system PATH.

    :raises EnvironmentError: If journalctl is not found on the system PATH
        at instantiation time.
    """

    # journalctl expects timestamps in this exact format for -S and -U flags
    _DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        """Verify that journalctl is available on the system PATH.

        :raises EnvironmentError: If journalctl cannot be found.
        """
        if shutil.which('journalctl') is None:
            raise EnvironmentError(
                "journalctl was not found on the system PATH. "
                "This application requires systemd and journalctl to be installed."
            )

    def read_logs(self, query: LogQuery) -> str:
        """Fetch log entries from the systemd journal matching the given query.

        Builds a journalctl command from the query parameters and runs
        it as a subprocess. The --no-pager flag ensures output is
        captured in full rather than paged interactively.

        :param query: The query parameters. The time range is formatted
            to journalctl's required timestamp format. If
            filter_pattern is set, it is passed as a regex to
            journalctl's -g flag.
        :returns: The raw journal output as a string, or an empty string if
            no entries matched.
        :raises LogReadError: If journalctl exits with a non-zero return code.
        """
        cmd = [
            'journalctl',
            '-S', query.start.strftime(self._DATE_FMT),
            '-U', query.end.strftime(self._DATE_FMT),
            '--no-pager',
        ]

        # -g applies a regex filter; omitting it returns all entries in range
        if query.filter_pattern:
            cmd.extend(['-g', query.filter_pattern])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            message = result.stderr.strip() or f"journalctl exited with code {result.returncode}"
            raise LogReadError(message)

        return result.stdout
