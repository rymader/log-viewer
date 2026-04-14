"""Toolbar widget containing date/time range controls and the View Logs button."""

from datetime import datetime

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk

from logviewer.models.query import LogQuery
from logviewer.ui.gtk.calendar_button import CalendarButton
from logviewer.ui.gtk.date_entry import DateEntry
from logviewer.ui.gtk.time_entry import TimeEntry


class Toolbar(Gtk.Box):  # type: ignore[misc, unused-ignore]
    """A horizontal GTK toolbar with start/end date and time range inputs.

    Displays two date/time pairs (start and end), each consisting of a
    CalendarButton, a DateEntry, and a TimeEntry. Also contains the
    'View Logs' button, which is disabled until both date fields contain
    valid, parseable dates. Time fields are optional.

    When the user clicks 'View Logs', a LogQuery is built from the
    current field values and emitted via the 'query-ready' signal.
    Parent widgets (e.g. LogViewer) connect to this signal to trigger
    the log fetch without Toolbar needing any knowledge of the reader.

    Signals:
        query-ready (LogQuery): Emitted when View Logs is clicked and
            a valid query can be constructed.

    Args:
        date_format: A strptime-style date format string derived from
            the system locale, e.g. '%m/%d/%Y'. Passed to DateEntry
            widgets to drive auto-formatting and parsing.
    """

    __gsignals__ = {
        'query-ready': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, date_format: str) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._date_format = date_format

        # Create start date/time entries and calendar button
        self.start_date_entry = DateEntry("Start Date", self._date_format)
        self.start_date_entry.connect("date-entered", self.on_date_changed)
        self.start_calendar = CalendarButton(self.start_date_entry)
        self.start_calendar.connect("date-entered", self.on_date_changed)
        self.start_time_entry = TimeEntry()
        self.start_time_entry.connect("time-entered", self.on_date_changed)
        self.pack_start(self.start_calendar, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.start_date_entry, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.start_time_entry, False, False, 0) # type: ignore[attr-defined]

        # Create end date/time entries and calendar button
        self.end_date_entry = DateEntry("End Date", self._date_format)
        self.end_date_entry.connect("date-entered", self.on_date_changed)
        self.end_calendar = CalendarButton(self.end_date_entry)
        self.end_calendar.connect("date-entered", self.on_date_changed)
        self.end_time_entry = TimeEntry()
        self.end_time_entry.connect("time-entered", self.on_date_changed)
        self.pack_start(self.end_calendar, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.end_date_entry, False, False, 0) # type: ignore[attr-defined]
        self.pack_start(self.end_time_entry, False, False, 0) # type: ignore[attr-defined]

        # Create a button to view logs
        self.view_logs_button = Gtk.Button(label="View Logs")
        self.view_logs_button.set_sensitive(False)
        self.view_logs_button.connect("clicked", self._on_view_logs_clicked)
        self.pack_start(self.view_logs_button, False, False, 0) # type: ignore[attr-defined]

    @property
    def query(self) -> LogQuery | None:
        """Build a LogQuery from the current field values.

        Parses the date entries using the locale format string. If
        either date is invalid or incomplete, returns None. Time fields
        are optional — if a time field cannot be parsed as HH:MM:SS,
        a default boundary time is used (00:00:00 for start, 23:59:59
        for end).

        Returns:
            A LogQuery if both dates are valid, otherwise None.
        """
        try:
            start = datetime.strptime(self.start_date_entry.date, self._date_format)
            end = datetime.strptime(self.end_date_entry.date, self._date_format)
        except ValueError:
            return None

        # Apply time if fully entered, otherwise fall back to day boundaries
        start = self._apply_time(start, self.start_time_entry.time, 0, 0, 0)
        end = self._apply_time(end, self.end_time_entry.time, 23, 59, 59)

        return LogQuery(start, end)

    @staticmethod
    def _apply_time(
        dt: datetime, time_str: str, default_h: int, default_m: int, default_s: int
    ) -> datetime:
        """Apply a time string to a date, falling back to defaults if unparseable.

        Args:
            dt: The base date to apply the time to.
            time_str: A time string in HH:MM:SS format. If empty or
                incomplete, defaults are used instead.
            default_h: Default hour if time_str cannot be parsed.
            default_m: Default minute if time_str cannot be parsed.
            default_s: Default second if time_str cannot be parsed.

        Returns:
            The datetime with the time component applied.
        """
        try:
            t = datetime.strptime(time_str, "%H:%M:%S")
            return dt.replace(hour=t.hour, minute=t.minute, second=t.second)
        except ValueError:
            return dt.replace(hour=default_h, minute=default_m, second=default_s)

    def on_date_changed(self, widget: object = None) -> None:
        """Enable or disable the View Logs button based on date field validity.

        Called whenever any date or time field changes. The button is
        enabled only when both date fields can be successfully parsed.
        Time fields are not required for the button to activate.

        Args:
            widget: The widget that emitted the change signal (unused).
        """
        try:
            datetime.strptime(self.start_date_entry.date, self._date_format)
            datetime.strptime(self.end_date_entry.date, self._date_format)
            self.view_logs_button.set_sensitive(True)
        except ValueError:
            self.view_logs_button.set_sensitive(False)

    def _on_view_logs_clicked(self, button: Gtk.Button) -> None:
        """Build the query and emit 'query-ready' when View Logs is clicked.

        Args:
            button: The Gtk.Button that emitted the 'clicked' signal.
        """
        query = self.query
        if query is not None:
            self.emit("query-ready", query)

    def clear(self) -> None:
        """Clear all date and time entry fields."""
        self.start_date_entry.clear()
        self.start_time_entry.clear()
        self.end_date_entry.clear()
        self.end_time_entry.clear()
