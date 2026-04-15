"""Application-level system requirement checks."""

import shutil
import sys


def check_platform() -> None:
    """Verify that the application is running on Linux.

    This application is Linux-only due to its dependency on GTK3 and
    the systemd journal. This check should be called before any other
    application code runs so the user receives a clear error immediately
    rather than a confusing import or runtime failure later.

    :raises EnvironmentError: If the current platform is not Linux.
    """
    if sys.platform != 'linux':
        raise EnvironmentError(
            f"This application requires Linux. "
            f"Current platform: '{sys.platform}'."
        )


def check_systemd() -> None:
    """Verify that systemd is available on this system.

    Uses the presence of systemctl on the PATH as a proxy for systemd
    being available on this system. This is checked at the application
    level because the systemd journal is a core dependency of the entire
    app, regardless of which reader backend is in use.

    :raises EnvironmentError: If systemctl is not found on the system PATH.
    """
    if shutil.which('systemctl') is None:
        raise EnvironmentError(
            "systemd was not found on this system. "
            "This application requires systemd to access the system journal."
        )


def check_all() -> None:
    """Run all application-level system requirement checks.

    Calls each check in order, stopping at the first failure. Should
    be called once at application startup before any other code runs.

    :raises EnvironmentError: If any system requirement is not met.
    """
    check_platform()
    check_systemd()
