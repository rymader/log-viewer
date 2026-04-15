"""Toolbar widget containing date/time range controls and the View Logs button."""

from datetime import datetime, time

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

    _START_OF_DAY: time = time(0, 0, 0)
    _END_OF_DAY: time = time(23, 59, 59)

    __gsignals__ = {
        'query-ready': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, date_format: str) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._date_format = date_format

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
        """Build a LogQuery from the current field values.

        Parses the date entries using the locale format string. Returns
        None if either date is incomplete. Time fields are optional — if
        a time field cannot be parsed as HH:MM:SS, a default boundary
        time is used (00:00:00 for start, 23:59:59 for end).

        Raises ValueError (from LogQuery) if start is later than end.
        In normal UI flow this cannot happen because _validate() keeps
        the button disabled for invalid ranges — this only surfaces if
        query is called directly with inverted dates (e.g. in tests).

        :returns: A LogQuery if both dates are complete, otherwise None.
        :raises ValueError: If the resolved start is later than end.
        """
        try:
            start = datetime.strptime(self.start_date_entry.date, self._date_format)
            end = datetime.strptime(self.end_date_entry.date, self._date_format)
        except ValueError:
            return None

        # Apply time if fully entered, otherwise fall back to day boundaries
        start = self._apply_time(start, self.start_time_entry.time, self._START_OF_DAY)
        end = self._apply_time(end, self.end_time_entry.time, self._END_OF_DAY)

        return LogQuery(start, end)

    @staticmethod
    def _apply_time(dt: datetime, time_str: str, default: time) -> datetime:
        """Apply a time string to a date, falling back to a default if unparseable.

        :param dt: The base date to apply the time to.
        :param time_str: A time string in HH:MM:SS format. If empty or
            incomplete, default is used instead.
        :param default: Default time if time_str cannot be parsed.
        :returns: The datetime with the time component applied.
        """
        try:
            return datetime.combine(dt.date(), datetime.strptime(time_str, "%H:%M:%S").time())
        except ValueError:
            return datetime.combine(dt.date(), default)

    def _validate(self, _widget: object = None) -> None:
        """Update button sensitivity and error label based on current field state.

        Called whenever any date or time field changes. Distinguishes
        three states:

        - Incomplete: either date field cannot be parsed. Button disabled,
          error label hidden.
        - Invalid range: both dates parse but start is later than end.
          Button disabled, error label shown.
        - Valid: both dates parse and start is on or before end.
          Button enabled, error label hidden.

        :param _widget: The widget that emitted the change signal (unused).
        """
        try:
            start = datetime.strptime(self.start_date_entry.date, self._date_format)
            end = datetime.strptime(self.end_date_entry.date, self._date_format)
        except ValueError:
            # Incomplete — not an error, just not ready yet
            self._error_label.hide()
            self.view_logs_button.set_sensitive(False)
            return

        start = self._apply_time(start, self.start_time_entry.time, self._START_OF_DAY)
        end = self._apply_time(end, self.end_time_entry.time, self._END_OF_DAY)

        if start > end:
            self._error_label.set_text("End date/time must be on or after start date/time")  # type: ignore[attr-defined]
            self._error_label.show()
            self.view_logs_button.set_sensitive(False)
        else:
            self._error_label.hide()
            self.view_logs_button.set_sensitive(True)

    def _on_view_logs_clicked(self, _button: Gtk.Button) -> None:
        """Build the query and emit 'query-ready' when View Logs is clicked.

        The button is only enabled when _validate() has confirmed the
        input is complete and the range is valid, so query is guaranteed
        to return a LogQuery here.

        :param _button: The Gtk.Button that emitted the 'clicked' signal (unused).
        """
        self.emit("query-ready", self.query)

    def clear(self) -> None:
        """Clear all date and time entry fields."""
        self.start_date_entry.clear()
        self.start_time_entry.clear()
        self.end_date_entry.clear()
        self.end_time_entry.clear()
