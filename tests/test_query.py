"""Tests for the LogQuery domain model."""

from datetime import datetime

from logviewer.models.query import LogQuery


class TestLogQuery:
    def test_stores_start_and_end(self):
        start = datetime(2026, 4, 1, 0, 0, 0)
        end = datetime(2026, 4, 13, 23, 59, 59)
        query = LogQuery(start, end)
        assert query.start == start
        assert query.end == end

    def test_start_and_end_are_not_mutated(self):
        """Verify LogQuery stores references without altering the datetime objects."""
        start = datetime(2026, 4, 1, 9, 30, 0)
        end = datetime(2026, 4, 13, 17, 0, 0)
        query = LogQuery(start, end)
        assert query.start is start
        assert query.end is end

    def test_default_filter_pattern_is_empty(self):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13))
        assert query.filter_pattern == ''

    def test_custom_filter_pattern_is_stored(self):
        query = LogQuery(datetime(2026, 4, 1), datetime(2026, 4, 13), filter_pattern='error')
        assert query.filter_pattern == 'error'
