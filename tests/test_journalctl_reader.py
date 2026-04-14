"""Tests for the JournalctlLogReader."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from logviewer.models.query import LogQuery
from logviewer.readers.base import LogReader
from logviewer.readers.journalctl import JournalctlLogReader


class TestJournalctlLogReaderInit:
    def test_raises_when_journalctl_missing(self):
        with patch('shutil.which', return_value=None):
            with pytest.raises(EnvironmentError, match='journalctl'):
                JournalctlLogReader()

    def test_succeeds_when_journalctl_present(self):
        with patch('shutil.which', return_value='/usr/bin/journalctl'):
            reader = JournalctlLogReader()
            assert reader is not None

    def test_is_subclass_of_log_reader(self):
        with patch('shutil.which', return_value='/usr/bin/journalctl'):
            reader = JournalctlLogReader()
            assert isinstance(reader, LogReader)


def _make_result(stdout=''):
    result = MagicMock()
    result.stdout = stdout
    return result


class TestJournalctlLogReaderReadLogs:
    @pytest.fixture
    def reader(self):
        with patch('shutil.which', return_value='/usr/bin/journalctl'):
            return JournalctlLogReader()

    def test_passes_formatted_start_timestamp(self, reader):
        query = LogQuery(datetime(2026, 4, 1, 9, 30, 0), datetime(2026, 4, 13, 17, 0, 0))
        with patch('subprocess.run', return_value=_make_result()) as mock_run:
            reader.read_logs(query)
            cmd = mock_run.call_args[0][0]
            assert '-S' in cmd
            assert cmd[cmd.index('-S') + 1] == '2026-04-01 09:30:00'

    def test_passes_formatted_end_timestamp(self, reader):
        query = LogQuery(datetime(2026, 4, 1, 0, 0, 0), datetime(2026, 4, 13, 23, 59, 59))
        with patch('subprocess.run', return_value=_make_result()) as mock_run:
            reader.read_logs(query)
            cmd = mock_run.call_args[0][0]
            assert '-U' in cmd
            assert cmd[cmd.index('-U') + 1] == '2026-04-13 23:59:59'

    def test_includes_no_pager_flag(self, reader):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13))
        with patch('subprocess.run', return_value=_make_result()) as mock_run:
            reader.read_logs(query)
            cmd = mock_run.call_args[0][0]
            assert '--no-pager' in cmd

    def test_includes_grep_flag_when_filter_pattern_set(self, reader):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13), filter_pattern='error')
        with patch('subprocess.run', return_value=_make_result()) as mock_run:
            reader.read_logs(query)
            cmd = mock_run.call_args[0][0]
            assert '-g' in cmd
            assert cmd[cmd.index('-g') + 1] == 'error'

    def test_omits_grep_flag_when_filter_pattern_empty(self, reader):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13), filter_pattern='')
        with patch('subprocess.run', return_value=_make_result()) as mock_run:
            reader.read_logs(query)
            cmd = mock_run.call_args[0][0]
            assert '-g' not in cmd

    def test_returns_stdout(self, reader):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13))
        expected = 'Apr 01 09:30:00 hostname sshd[123]: some log line\n'
        with patch('subprocess.run', return_value=_make_result(stdout=expected)):
            result = reader.read_logs(query)
            assert result == expected
