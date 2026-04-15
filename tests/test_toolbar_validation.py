"""Tests for the pure toolbar validation logic."""


from logviewer.models.query import LogQuery
from logviewer.ui.gtk.validation import compute_validation

DATE_FORMAT = '%m/%d/%Y'


class TestComputeValidationIncomplete:
    def test_empty_dates_returns_not_ready(self):
        result = compute_validation('', '', '', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is None
        assert result.query is None

    def test_only_start_date_returns_not_ready(self):
        result = compute_validation('04/01/2026', '', '', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is None

    def test_only_end_date_returns_not_ready(self):
        result = compute_validation('', '04/13/2026', '', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is None

    def test_partial_start_time_returns_not_ready(self):
        result = compute_validation('04/01/2026', '04/13/2026', '09:30', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is None

    def test_partial_end_time_returns_not_ready(self):
        result = compute_validation('04/01/2026', '04/13/2026', '', '23:59', DATE_FORMAT)
        assert not result.ready
        assert result.error is None


class TestComputeValidationInvalidTime:
    def test_start_time_hour_out_of_range(self):
        result = compute_validation('04/01/2026', '04/13/2026', '80:00:00', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is not None
        assert 'hours' in result.error

    def test_end_time_minute_out_of_range(self):
        result = compute_validation('04/01/2026', '04/13/2026', '', '99:99:99', DATE_FORMAT)
        assert not result.ready
        assert result.error is not None

    def test_invalid_time_produces_error_message(self):
        result = compute_validation('04/01/2026', '04/13/2026', '25:00:00', '', DATE_FORMAT)
        assert result.error is not None
        assert '00' in result.error  # contains range hint


class TestComputeValidationInvalidRange:
    def test_end_before_start_returns_not_ready(self):
        result = compute_validation('04/13/2026', '04/01/2026', '', '', DATE_FORMAT)
        assert not result.ready
        assert result.error is not None
        assert 'after' in result.error.lower()

    def test_same_date_earlier_end_time_returns_not_ready(self):
        result = compute_validation('04/01/2026', '04/01/2026', '12:00:00', '08:00:00', DATE_FORMAT)
        assert not result.ready
        assert result.error is not None


class TestComputeValidationValid:
    def test_valid_dates_no_times_returns_ready(self):
        result = compute_validation('04/01/2026', '04/13/2026', '', '', DATE_FORMAT)
        assert result.ready
        assert result.error is None
        assert isinstance(result.query, LogQuery)

    def test_valid_dates_with_times_returns_ready(self):
        result = compute_validation('04/01/2026', '04/13/2026', '09:30:00', '17:00:00', DATE_FORMAT)
        assert result.ready
        assert result.query is not None

    def test_same_start_and_end_is_valid(self):
        result = compute_validation('04/01/2026', '04/01/2026', '', '', DATE_FORMAT)
        assert result.ready

    def test_same_datetime_is_valid(self):
        result = compute_validation('04/01/2026', '04/01/2026', '12:00:00', '12:00:00', DATE_FORMAT)
        assert result.ready

    def test_query_uses_start_of_day_default_for_start_time(self):
        result = compute_validation('04/01/2026', '04/13/2026', '', '', DATE_FORMAT)
        assert result.query is not None
        assert result.query.start.hour == 0
        assert result.query.start.minute == 0
        assert result.query.start.second == 0

    def test_query_uses_end_of_day_default_for_end_time(self):
        result = compute_validation('04/01/2026', '04/13/2026', '', '', DATE_FORMAT)
        assert result.query is not None
        assert result.query.end.hour == 23
        assert result.query.end.minute == 59
        assert result.query.end.second == 59

    def test_query_uses_supplied_times_when_provided(self):
        result = compute_validation('04/01/2026', '04/13/2026', '09:30:00', '17:45:00', DATE_FORMAT)
        assert result.query is not None
        assert result.query.start.hour == 9
        assert result.query.start.minute == 30
        assert result.query.end.hour == 17
        assert result.query.end.minute == 45
