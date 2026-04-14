"""Application entry point for the GTK log viewer."""

import sys
from typing import NoReturn

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from logviewer.readers.journalctl import JournalctlLogReader
from logviewer.system.requirements import check_all
from logviewer.ui.gtk.window import LogViewer
from logviewer.utils.locale_utils import detect_date_format


def _show_error_and_exit(message: str) -> NoReturn:
    """Display a GTK error dialog and exit the application.

    Used to surface requirement failures to the user in a GUI-appropriate
    way rather than printing to stderr (which may not be visible if the
    app was launched from a file manager or desktop shortcut).

    Args:
        message: The error message to display in the dialog.
    """
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text="System requirement not met",
    )
    dialog.format_secondary_text(message)  # type: ignore[attr-defined]
    dialog.run()  # type: ignore[attr-defined]
    dialog.destroy()
    sys.exit(1)


def main() -> None:
    """Launch the log viewer application.

    Runs system requirement checks before initialising the UI. Any
    unmet requirement is surfaced as a GTK error dialog so the user
    receives a clear message regardless of how the application was
    launched (terminal, desktop shortcut, file manager, etc.).
    """
    # Verify platform and systemd before any application code runs
    try:
        check_all()
    except EnvironmentError as e:
        _show_error_and_exit(str(e))

    # Construct the reader — raises EnvironmentError if journalctl is missing
    try:
        reader = JournalctlLogReader()
    except EnvironmentError as e:
        _show_error_and_exit(str(e))

    # Detect locale once at startup — setting locale is a process-wide
    # side effect and must not happen inside widget constructors
    date_format = detect_date_format()

    # Inject reader into the window, keeping the UI layer decoupled
    # from the concrete reader implementation
    win = LogViewer(reader=reader, date_format=date_format)
    win.connect("destroy", Gtk.main_quit)  # type: ignore[attr-defined]
    win.show_all()  # type: ignore[attr-defined]
    Gtk.main()  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
