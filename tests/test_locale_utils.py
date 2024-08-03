"""Tests for the locale detection utility."""

from unittest.mock import patch

from logviewer.utils.locale_utils import detect_date_format


class TestDetectDateFormat:
    def test_returns_locale_format_when_valid(self):
        with patch('locale.setlocale'), patch('locale.nl_langinfo', return_value='%m/%d/%Y'):
            result = detect_date_format()
            assert result == '%m/%d/%Y'

    def test_returns_european_format_from_locale(self):
        with patch('locale.setlocale'), patch('locale.nl_langinfo', return_value='%d/%m/%Y'):
            result = detect_date_format()
            assert result == '%d/%m/%Y'

    def test_falls_back_to_iso_when_locale_raises(self):
        import locale
        with patch('locale.setlocale', side_effect=locale.Error('unsupported locale')):
            result = detect_date_format()
            assert result == '%Y-%m-%d'

    def test_falls_back_to_iso_when_format_has_no_known_tokens(self):
        with patch('locale.setlocale'), patch('locale.nl_langinfo', return_value='%x'):
            result = detect_date_format()
            assert result == '%Y-%m-%d'

    def test_falls_back_to_iso_when_format_is_empty(self):
        with patch('locale.setlocale'), patch('locale.nl_langinfo', return_value=''):
            result = detect_date_format()
            assert result == '%Y-%m-%d'

    def test_falls_back_to_iso_when_nl_langinfo_raises(self):
        with patch('locale.setlocale'), patch('locale.nl_langinfo', side_effect=AttributeError):
            result = detect_date_format()
            assert result == '%Y-%m-%d'
