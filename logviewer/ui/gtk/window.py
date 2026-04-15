"""Main application window for the log viewer."""

import threading

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, Pango

from logviewer.models.query import LogQuery
from logviewer.readers.base import LogReader, LogReadError
from logviewer.ui.gtk.toolbar import Toolbar

_BRAILLE_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


class LogViewer(Gtk.Window):  # type: ignore[misc, unused-ignore]
    """The main application window for the log viewer.

    Composes a Toolbar for query input and a scrollable TextView for
    displaying log output. Depends on the LogReader interface rather
    than any concrete implementation, keeping the window decoupled from
    the underlying log source.

    The reader is injected at construction time (dependency injection),
    making it straightforward to swap in a different reader backend or
    a mock for testing without modifying this class.

    :param reader: The log reader backend to use for fetching logs.
    :param date_format: A strptime-style date format string from the
        system locale, passed through to the Toolbar.
    """

    def __init__(self, reader: LogReader, date_format: str) -> None:
        super().__init__(title="Log Viewer")

        self._reader = reader
        self._loading_frame = 0
        self._loading_timeout_id: int | None = None

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
        self.textview.set_wrap_mode(Gtk.WrapMode.NONE)
        self.textview.modify_font(  # type: ignore[attr-defined]
            Pango.FontDescription.from_string('Monospace 10')
        )
        scrolled_window.add(self.textview) # type: ignore[attr-defined]

    def on_query_ready(self, _toolbar: Toolbar, query: LogQuery) -> None:
        """Start a background fetch when the toolbar emits a ready query.

        Shows a loading message and disables the View Logs button
        immediately, then delegates the actual read to a daemon thread
        so the GTK main loop stays responsive. Results are marshalled
        back onto the UI thread via GLib.idle_add.

        :param _toolbar: The Toolbar that emitted the signal (unused).
        :param query: The LogQuery built from the toolbar's current fields.
        """
        self._loading_frame = 0
        self._loading_timeout_id = GLib.timeout_add(80, self._tick_loading)
        self.toolbar.start_fetch()

        thread = threading.Thread(target=self._fetch_logs, args=(query,), daemon=True)
        thread.start()

    def _tick_loading(self) -> bool:
        """Advance the braille spinner by one frame.

        Runs on the GTK main thread via GLib.timeout_add. Keeps firing
        until _stop_loading() cancels the timeout source.

        :returns: GLib.SOURCE_CONTINUE to keep the timeout active.
        """
        frame = _BRAILLE_FRAMES[self._loading_frame % len(_BRAILLE_FRAMES)]
        self.textview.get_buffer().set_text(f'{frame} Loading')  # type: ignore[attr-defined]
        self._loading_frame += 1
        return GLib.SOURCE_CONTINUE

    def _stop_loading(self) -> None:
        """Cancel the spinner timeout if one is active."""
        if self._loading_timeout_id is not None:
            GLib.source_remove(self._loading_timeout_id)
            self._loading_timeout_id = None

    def _fetch_logs(self, query: LogQuery) -> None:
        """Run read_logs on a worker thread and schedule a UI update.

        Must not touch any GTK widgets directly — all UI updates are
        deferred to the main thread via GLib.idle_add.

        :param query: The query to execute.
        """
        try:
            output = self._reader.read_logs(query)
            GLib.idle_add(self._display_logs, output)
        except LogReadError as e:
            GLib.idle_add(self._display_error, str(e))
        except Exception as e:
            GLib.idle_add(self._display_error, f"Unexpected error: {e}")

    def _display_logs(self, output: str) -> bool:
        """Update the text view with fetched log output.

        Runs on the GTK main thread via GLib.idle_add.

        :param output: The raw log output string. Empty string means no
            entries matched the query.
        :returns: GLib.SOURCE_REMOVE so the idle callback fires once only.
        """
        self._stop_loading()
        self.textview.get_buffer().set_text(  # type: ignore[attr-defined]
            output if output else "No log entries found for the selected date range."
        )
        self.resize(1500, 1000)  # type: ignore[attr-defined]
        self.toolbar.end_fetch()
        return GLib.SOURCE_REMOVE

    def _display_error(self, message: str) -> bool:
        """Display an error message in the text view.

        Runs on the GTK main thread via GLib.idle_add.

        :param message: The error message to display.
        :returns: GLib.SOURCE_REMOVE so the idle callback fires once only.
        """
        self._stop_loading()
        self.textview.get_buffer().set_text(f"Error reading logs:\n\n{message}")  # type: ignore[attr-defined]
        self.toolbar.end_fetch()
        return GLib.SOURCE_REMOVE
