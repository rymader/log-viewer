"""Time entry widget with auto-formatting."""

from typing import cast

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

from logviewer.utils.date_format import DateFormat


class TimeEntry(Gtk.Box):  # type: ignore[misc, unused-ignore]
    """A GTK text entry widget for time input in HH:MM:SS format.

    Displays a single-line text field that automatically inserts ':'
    separators as the user types digits. The format is always 24-hour
    HH:MM:SS, which is locale-independent and unambiguous.

    Time is treated as optional — an empty or incomplete field is
    valid and should be interpreted by the caller as "use a default"
    (typically 00:00:00 for start time and 23:59:59 for end time).

    Emits the 'time-entered' signal whenever the field content changes.

    Signals:
        time-entered: Emitted when the entry text changes.
    """

    __gsignals__ = {
        'time-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    # HH, MM, SS — each field is 2 digits
    _FIELD_LENGTHS = [2, 2, 2]
    _SEPARATOR = ':'

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._updating = False  # Guard flag to prevent recursive signal handling

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("HH:MM:SS")
        self._entry.set_max_length(8)  # HH:MM:SS = 8 characters
        self._entry.connect("changed", self.on_entry_changed)

        self.pack_start(self._entry, True, True, 0) # type: ignore[attr-defined]

    @property
    def time(self) -> str:
        """The current text content of the entry field."""
        return cast(str, self._entry.get_text())  # type: ignore[redundant-cast]  # type: ignore[return-value]

    @time.setter
    def time(self, value: str) -> None:
        """Set the entry text directly.

        :param value: The time string to display, e.g. '14:30:00'.
        """
        self._entry.set_text(value)

    def clear(self) -> None:
        """Clear the entry field."""
        self._entry.set_text("")

    def on_entry_changed(self, widget: Gtk.Entry) -> None:
        """Handle text changes by reformatting the digit input.

        Strips all non-digit characters, then rebuilds the formatted
        HH:MM:SS string with ':' separators inserted as digits are
        entered. Uses GLib.idle_add to defer cursor positioning until
        after GTK has finished processing the keystroke event.

        :param widget: The Gtk.Entry that emitted the 'changed' signal.
        """
        # Prevent recursive calls caused by set_text() below
        if self._updating:
            return

        digits = ''.join(c for c in widget.get_text() if c.isdigit())[:6]
        formatted = DateFormat.format_group(digits, self._FIELD_LENGTHS, self._SEPARATOR)

        self._updating = True
        widget.set_text(formatted)
        # Defer cursor move so it runs after GTK's own keystroke cursor positioning
        GLib.idle_add(widget.set_position, len(formatted))
        self._updating = False

        self.emit("time-entered")
