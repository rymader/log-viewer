"""Tests for the DateFormat utility class."""

from logviewer.utils.date_format import DateFormat


class TestDetectSeparator:
    def test_slash_separator(self):
        assert DateFormat.detect_separator('%m/%d/%Y') == '/'

    def test_dash_separator(self):
        assert DateFormat.detect_separator('%Y-%m-%d') == '-'

    def test_dot_separator(self):
        assert DateFormat.detect_separator('%d.%m.%Y') == '.'

    def test_falls_back_to_dash_when_no_separator(self):
        assert DateFormat.detect_separator('%Y%m%d') == '-'


class TestDetectFieldLengths:
    def test_us_format_month_day_year(self):
        assert DateFormat.detect_field_lengths('%m/%d/%Y') == [2, 2, 4]

    def test_european_format_day_month_year(self):
        assert DateFormat.detect_field_lengths('%d/%m/%Y') == [2, 2, 4]

    def test_iso_format_year_month_day(self):
        assert DateFormat.detect_field_lengths('%Y-%m-%d') == [4, 2, 2]

    def test_two_digit_year_produces_length_2(self):
        assert DateFormat.detect_field_lengths('%m/%d/%y') == [2, 2, 2]


class TestToPlaceholder:
    def test_us_format(self):
        assert DateFormat.to_placeholder('%m/%d/%Y') == 'MM/DD/YYYY'

    def test_european_format(self):
        assert DateFormat.to_placeholder('%d/%m/%Y') == 'DD/MM/YYYY'

    def test_iso_format(self):
        assert DateFormat.to_placeholder('%Y-%m-%d') == 'YYYY-MM-DD'

    def test_two_digit_year(self):
        assert DateFormat.to_placeholder('%m/%d/%y') == 'MM/DD/YY'


class TestFormatGroup:
    def test_empty_input(self):
        assert DateFormat.format_group('', [2, 2, 4], '/') == ''

    def test_partial_first_field(self):
        assert DateFormat.format_group('0', [2, 2, 4], '/') == '0'

    def test_complete_first_field(self):
        assert DateFormat.format_group('04', [2, 2, 4], '/') == '04'

    def test_separator_inserted_after_first_field(self):
        assert DateFormat.format_group('041', [2, 2, 4], '/') == '04/1'

    def test_complete_two_fields(self):
        assert DateFormat.format_group('0413', [2, 2, 4], '/') == '04/13'

    def test_separator_inserted_after_second_field(self):
        assert DateFormat.format_group('04132', [2, 2, 4], '/') == '04/13/2'

    def test_complete_all_fields(self):
        assert DateFormat.format_group('04132026', [2, 2, 4], '/') == '04/13/2026'

    def test_iso_format_with_dash_separator(self):
        assert DateFormat.format_group('20260413', [4, 2, 2], '-') == '2026-04-13'

    def test_different_separator(self):
        assert DateFormat.format_group('04132026', [2, 2, 4], '.') == '04.13.2026'
