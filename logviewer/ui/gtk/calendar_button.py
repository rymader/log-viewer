"""Button widget that opens a calendar date picker popup."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

from logviewer.ui.gtk.calendar_window import CalendarWindow

gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk

if TYPE_CHECKING:
    from logviewer.ui.gtk.date_entry import DateEntry


class CalendarButton(Gtk.Button):  # type: ignore[misc, unused-ignore]
    """A GTK button that opens a CalendarWindow for date selection.

    Labelled with the date_type of its associated DateEntry (e.g.
    'Start Date'). When clicked, it opens a modal CalendarWindow
    parented to the application's top-level window. When a date is
    selected in the calendar, this button re-emits the 'date-entered'
    signal so parent widgets (e.g. Toolbar) can react without needing
    a direct reference to the CalendarWindow.

    Only one CalendarWindow is open at a time — clicking again while
    a calendar is already open closes the existing one before opening
    a new one.

    Signals:
        date-entered: Emitted when the user confirms a date in the
            CalendarWindow.

    Args:
        date_entry: The DateEntry widget this button is paired with.
            Its date_type is used for the button label, its date_format
            is used to format the selected date, and its date setter
            is called to populate the field.
    """

    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_entry: DateEntry) -> None:
        super().__init__(label=date_entry.date_type)

        self.calendar_window: CalendarWindow | None = None
        self.date_entry = date_entry
        self.connect("clicked", self.on_button_clicked)

    def on_button_clicked(self, button: Gtk.Button) -> None:
        """Open the calendar popup, closing any existing instance first.

        Retrieves the top-level window via get_toplevel() and passes it
        to CalendarWindow so the modal can block the correct parent.

        Args:
            button: The Gtk.Button that emitted the 'clicked' signal.
        """
        if self.calendar_window:
            self.calendar_window.destroy()  # Close any existing calendar window

        # get_toplevel() walks the widget hierarchy to find the root Gtk.Window,
        # which is required by set_transient_for for correct modal behavior
        parent = self.get_toplevel()  # type: ignore[attr-defined]
        calendar_window = CalendarWindow(self.date_entry, parent=parent)
        calendar_window.connect("date-entered", self.on_date_selected)
        calendar_window.show_all()  # type: ignore[attr-defined]
        self.calendar_window = calendar_window

    def on_date_selected(self, calendar: CalendarWindow) -> None:
        """Re-emit 'date-entered' when the CalendarWindow confirms a selection.

        Args:
            calendar: The CalendarWindow that emitted the signal.
        """
        self.emit("date-entered")
