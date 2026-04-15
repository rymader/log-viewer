"""Toolbar widget containing date/time range controls and the View Logs button."""

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk

from logviewer.models.query import LogQuery
from logviewer.ui.gtk.calendar_button import CalendarButton
from logviewer.ui.gtk.date_entry import DateEntry
from logviewer.ui.gtk.time_entry import TimeEntry
from logviewer.ui.gtk.validation import compute_validation


class Toolbar(Gtk.Box):  # type: ignore[misc, unused-ignore]
    """A horizontal GTK toolbar with start/end date and time range inputs.

    Displays two date/time pairs (start and end), each consisting of a
    CalendarButton, a DateEntry, and a TimeEntry. Also contains the
    'View Logs' button and an inline validation label.

    The button is enabled only when both date fields are complete and the
    start is on or before the end. If the range is inverted, the button
    stays disabled and the validation label is shown. Time fields are
    optional.

    When the user clicks 'View Logs', a LogQuery is built from the
    current field values and emitted via the 'query-ready' signal.
    Parent widgets (e.g. LogViewer) connect to this signal to trigger
    the log fetch without Toolbar needing any knowledge of the reader.

    Signals:
        query-ready (LogQuery): Emitted when View Logs is clicked and
            a valid query can be constructed.

    :param date_format: A strptime-style date format string derived from
        the system locale, e.g. '%m/%d/%Y'. Passed to DateEntry
        widgets to drive auto-formatting and parsing.
    """

    __gsignals__ = {
        'query-ready': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, date_format: str) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._date_format = date_format
        self._fetch_in_progress = False

        # Create start date/time entries and calendar button
        self.start_date_entry = DateEntry("Start Date", self._date_format)
        self.start_date_entry.connect("date-entered", self._validate)
        self.start_calendar = CalendarButton(self.start_date_entry)
        self.start_calendar.connect("date-entered", self._validate)
        self.start_time_entry = TimeEntry()
        self.start_time_entry.connect("time-entered", self._validate)
        self.pack_start(self.start_calendar, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.start_date_entry, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.start_time_entry, False, False, 0) # type: ignore[attr-defined]

        # Create end date/time entries and calendar button
        self.end_date_entry = DateEntry("End Date", self._date_format)
        self.end_date_entry.connect("date-entered", self._validate)
        self.end_calendar = CalendarButton(self.end_date_entry)
        self.end_calendar.connect("date-entered", self._validate)
        self.end_time_entry = TimeEntry()
        self.end_time_entry.connect("time-entered", self._validate)
        self.pack_start(self.end_calendar, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.end_date_entry, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.end_time_entry, False, False, 0) # type: ignore[attr-defined]

        # Create a button to view logs
        self.view_logs_button = Gtk.Button(label="View Logs")
        self.view_logs_button.set_sensitive(False)
        self.view_logs_button.connect("clicked", self._on_view_logs_clicked)
        self.pack_start(self.view_logs_button, False, False, 0) # type: ignore[attr-defined]

        # Inline validation label — hidden until an invalid range is detected
        self._error_label = Gtk.Label()
        self._error_label.set_no_show_all(True)  # type: ignore[attr-defined]
        self.pack_start(self._error_label, False, False, 0) # type: ignore[attr-defined]

    @property
    def query(self) -> LogQuery | None:
        """Build a LogQuery from the current field values if they are valid.

        Delegates to compute_validation. Returns None if the form is
        incomplete or invalid.

        :returns: A LogQuery if the form is complete and valid, otherwise None.
        """
        return compute_validation(
            self.start_date_entry.date,
            self.end_date_entry.date,
            self.start_time_entry.time,
            self.end_time_entry.time,
            self._date_format,
        ).query

    def start_fetch(self) -> None:
        """Mark a fetch as in progress and recompute button state.

        Called by the window layer when a background read begins. Prevents
        _validate() from re-enabling the button while the fetch is running,
        even if the user edits the form into a valid state mid-flight.
        """
        self._fetch_in_progress = True
        self._validate()

    def end_fetch(self) -> None:
        """Mark a fetch as complete and recompute button state.

        Called by the window layer when a background read finishes
        (success or error). Re-runs _validate() so the button state
        reflects the current form rather than being blindly re-enabled.
        """
        self._fetch_in_progress = False
        self._validate()

    def _validate(self, _widget: object = None) -> None:
        """Update button sensitivity and error label based on current field state.

        Delegates all logic to compute_validation and applies the result
        to the GTK widgets. The button is only enabled when the form is
        valid and no fetch is in progress.

        :param _widget: The widget that emitted the change signal (unused).
        """
        result = compute_validation(
            self.start_date_entry.date,
            self.end_date_entry.date,
            self.start_time_entry.time,
            self.end_time_entry.time,
            self._date_format,
        )
        if result.error:
            self._error_label.set_text(result.error)  # type: ignore[attr-defined]
            self._error_label.show()
        else:
            self._error_label.hide()
        self.view_logs_button.set_sensitive(result.ready and not self._fetch_in_progress)

    def _on_view_logs_clicked(self, _button: Gtk.Button) -> None:
        """Build the query and emit 'query-ready' when View Logs is clicked.

        The button is only enabled when _validate() has confirmed the
        input is complete and the range is valid, so query is guaranteed
        to return a LogQuery here.

        :param _button: The Gtk.Button that emitted the 'clicked' signal (unused).
        """
        query = self.query
        assert query is not None, "button should only be enabled when query is valid"
        self.emit("query-ready", query)

    def clear(self) -> None:
        """Clear all date and time entry fields."""
        self.start_date_entry.clear()
        self.start_time_entry.clear()
        self.end_date_entry.clear()
        self.end_time_entry.clear()
