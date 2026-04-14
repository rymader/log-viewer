"""Main application window for the log viewer."""

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from logviewer.models.query import LogQuery
from logviewer.readers.base import LogReader
from logviewer.ui.gtk.toolbar import Toolbar


class LogViewer(Gtk.Window):  # type: ignore[misc, unused-ignore]
    """The main application window for the log viewer.

    Composes a Toolbar for query input and a scrollable TextView for
    displaying log output. Depends on the LogReader interface rather
    than any concrete implementation, keeping the window decoupled from
    the underlying log source.

    The reader is injected at construction time (dependency injection),
    making it straightforward to swap in a different reader backend or
    a mock for testing without modifying this class.

    Args:
        reader: The log reader backend to use for fetching logs.
        date_format: A strptime-style date format string from the
            system locale, passed through to the Toolbar.
    """

    def __init__(self, reader: LogReader, date_format: str) -> None:
        super().__init__(title="Log Viewer")

        self._reader = reader

        self.set_border_width(10) # type: ignore[attr-defined]
        self.set_default_size(1600, 850)

        # Create a vertical box layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox) # type: ignore[attr-defined]

        # Create a horizontal toolbar at the top
        self.toolbar = Toolbar(date_format=date_format)
        self.toolbar.connect("query-ready", self.on_query_ready)
        vbox.pack_start(self.toolbar, False, False, 0) # type: ignore[attr-defined]

        # Create a ScrolledWindow to hold the TextView
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0) # type: ignore[attr-defined]

        # Create a TextView widget to display the output
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.textview) # type: ignore[attr-defined]

    def on_query_ready(self, toolbar: Toolbar, query: LogQuery) -> None:
        """Fetch and display logs when the toolbar emits a ready query.

        Connected to the Toolbar's 'query-ready' signal. Passes the
        query to the injected reader, then displays the result in the
        TextView. Shows a descriptive message if no entries were found.
        Clears the toolbar fields after a successful fetch.

        Args:
            toolbar: The Toolbar that emitted the signal.
            query: The LogQuery built from the toolbar's current fields.
        """
        output = self._reader.read_logs(query)

        buffer = self.textview.get_buffer()
        buffer.set_text(output if output else "No log entries found for the selected date range.")
        self.resize(1500, 1000) # type: ignore[attr-defined]
        self.toolbar.clear()
