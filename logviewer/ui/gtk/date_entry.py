"""Locale-aware date entry widget with auto-formatting."""

from typing import cast

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

from logviewer.utils.date_format import DateFormat


class DateEntry(Gtk.Box):  # type: ignore[misc, unused-ignore]
    """A GTK text entry widget for date input with locale-aware auto-formatting.

    Displays a single-line text field that automatically inserts the
    locale-appropriate separator (e.g. '/' or '-') as the user types
    digits. The format is derived from the date_format string passed
    at construction, allowing the widget to support any regional date
    ordering (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.).

    Emits the 'date-entered' signal whenever the field content changes,
    allowing parent widgets to react to both typed and programmatically
    set values.

    Compatible with CalendarButton: exposes date_type, date_format,
    and the date property setter so CalendarWindow can populate the
    field after a date is selected.

    Signals:
        date-entered: Emitted when the entry text changes.

    Args:
        date_type: A label describing this field's role, e.g. 'Start Date'.
            Used by CalendarButton as its button label.
        date_format: A strptime-style format string defining the expected
            date format, e.g. '%m/%d/%Y'. Typically provided by
            detect_date_format() at application startup.
    """

    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_type: str, date_format: str) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._date_type = date_type
        self._date_format = date_format
        self._updating = False  # Guard flag to prevent recursive signal handling

        self._separator = DateFormat.detect_separator(date_format)
        self._field_lengths = DateFormat.detect_field_lengths(date_format)
        self._total_digits = sum(self._field_lengths)

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text(DateFormat.to_placeholder(date_format))
        # Max length = total digits + one separator per field boundary
        self._entry.set_max_length(self._total_digits + len(self._field_lengths) - 1)
        self._entry.connect("changed", self.on_entry_changed)

        self.pack_start(self._entry, True, True, 0) # type: ignore[attr-defined]

    @property
    def date_type(self) -> str:
        """The label describing this field's role, e.g. 'Start Date'."""
        return self._date_type

    @property
    def date_format(self) -> str:
        """The strptime-style format string this entry enforces."""
        return self._date_format

    @property
    def date(self) -> str:
        """The current text content of the entry field."""
        return cast(str, self._entry.get_text())  # type: ignore[redundant-cast]

    @date.setter
    def date(self, value: str) -> None:
        """Set the entry text directly, bypassing auto-format logic.

        Used by CalendarWindow to populate the field after a date is
        selected. The value should already be formatted correctly for
        the locale (i.e. produced by strftime with this entry's format).

        Args:
            value: The date string to display, e.g. '04/13/2026'.
        """
        self._entry.set_text(value)

    def clear(self) -> None:
        """Clear the entry field."""
        self._entry.set_text("")

    def on_entry_changed(self, widget: Gtk.Entry) -> None:
        """Handle text changes by reformatting the digit input.

        Strips all non-digit characters from the current text, then
        rebuilds the formatted string with separators inserted at the
        correct positions. Uses GLib.idle_add to defer cursor
        positioning until after GTK has finished processing the
        keystroke event, preventing the cursor from jumping mid-field.

        Args:
            widget: The Gtk.Entry that emitted the 'changed' signal.
        """
        # Prevent recursive calls caused by set_text() below
        if self._updating:
            return

        digits = ''.join(c for c in widget.get_text() if c.isdigit())[:self._total_digits]
        formatted = DateFormat.format_group(digits, self._field_lengths, self._separator)

        self._updating = True
        widget.set_text(formatted)
        # Defer cursor move so it runs after GTK's own keystroke cursor positioning
        GLib.idle_add(widget.set_position, len(formatted))
        self._updating = False

        self.emit("date-entered")
