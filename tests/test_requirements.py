"""Tests for the system requirements checks."""

from unittest.mock import patch

import pytest

from logviewer.system.requirements import check_all, check_platform, check_systemd


class TestCheckPlatform:
    def test_raises_on_non_linux_platform(self):
        with patch('sys.platform', 'darwin'):
            with pytest.raises(EnvironmentError, match='Linux'):
                check_platform()

    def test_raises_on_windows(self):
        with patch('sys.platform', 'win32'):
            with pytest.raises(EnvironmentError, match='Linux'):
                check_platform()

    def test_passes_on_linux(self):
        with patch('sys.platform', 'linux'):
            check_platform()  # should not raise


class TestCheckSystemd:
    def test_raises_when_systemctl_missing(self):
        with patch('shutil.which', return_value=None):
            with pytest.raises(EnvironmentError, match='systemd'):
                check_systemd()

    def test_passes_when_systemctl_present(self):
        with patch('shutil.which', return_value='/usr/bin/systemctl'):
            check_systemd()  # should not raise


class TestCheckAll:
    def test_raises_on_wrong_platform(self):
        with patch('sys.platform', 'darwin'):
            with pytest.raises(EnvironmentError):
                check_all()

    def test_raises_when_systemd_missing_on_linux(self):
        with patch('sys.platform', 'linux'), patch('shutil.which', return_value=None):
            with pytest.raises(EnvironmentError, match='systemd'):
                check_all()

    def test_passes_when_all_requirements_met(self):
        with patch('sys.platform', 'linux'), \
                patch('shutil.which', return_value='/usr/bin/systemctl'):
            check_all()  # should not raise

    def test_platform_checked_before_systemd(self):
        """check_all should stop at platform check without ever calling shutil.which."""
        with patch('sys.platform', 'darwin'), patch('shutil.which') as mock_which:
            with pytest.raises(EnvironmentError):
                check_all()
            mock_which.assert_not_called()
