"""Modal calendar popup window for date selection."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk

if TYPE_CHECKING:
    from logviewer.ui.gtk.date_entry import DateEntry


class CalendarWindow(Gtk.Window):  # type: ignore[misc, unused-ignore]
    """A modal popup window containing a GTK calendar widget.

    Opened by CalendarButton when the user wants to select a date
    visually rather than typing it. When a date is confirmed,
    the selected value is written back to the associated DateEntry
    and this window destroys itself.

    Navigation signals (prev/next month and year) are distinguished
    from selection signals using the navigation_mode flag, preventing
    a month or year change from being misinterpreted as a date
    confirmation.

    Signals:
        date-entered: Emitted after a date is selected and written to
            the associated DateEntry.

    :param date_entry: The DateEntry widget to populate on selection.
        Must expose date_format and a date setter.
    :param parent: The parent Gtk.Window to set as transient owner.
        Required for correct modal behaviour across window managers.
    """

    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_entry: DateEntry, parent: Gtk.Window | None = None) -> None:
        super().__init__(title="Select Date")
        self.date_entry = date_entry
        self.set_border_width(10)  # type: ignore[attr-defined]
        self.set_default_size(250, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)  # type: ignore[attr-defined]
        self.set_modal(True)
        if parent:
            # set_transient_for is required for modal to block the parent
            # window correctly on all window managers
            self.set_transient_for(parent)
        self.navigation_mode = False

        calendar = Gtk.Calendar()
        calendar.connect("day-selected", self.on_date_selected)
        calendar.connect("prev-month", self.on_navigation)
        calendar.connect("next-month", self.on_navigation)
        calendar.connect("prev-year", self.on_navigation)
        calendar.connect("next-year", self.on_navigation)
        self.add(calendar)  # type: ignore[attr-defined]

    def on_date_selected(self, calendar: Gtk.Calendar) -> None:
        """Handle a day-selected event from the calendar.

        Ignores the event if navigation_mode is True, which means the
        user clicked a month or year arrow rather than a day. Otherwise,
        formats the selected date using the associated entry's format
        string, writes it to the entry, and closes this window.

        :param calendar: The Gtk.Calendar that emitted the signal.
        """
        if not self.navigation_mode:
            date: tuple[int, int, int] = calendar.get_date()  # type: ignore[assignment]
            year, month, day = date
            # GTK calendar months are 0-indexed; datetime expects 1-indexed
            selected_date = datetime(year, month + 1, day).strftime(self.date_entry.date_format)

            self.date_entry.date = selected_date
            self.destroy()
            self.emit("date-entered")

        # Reset flag after every event so the next day click is treated as a selection
        self.navigation_mode = False

    def on_navigation(self, calendar: Gtk.Calendar) -> None:
        """Mark that a navigation action (month/year change) is in progress.

        Called before on_date_selected fires when the user clicks a
        navigation arrow. Setting navigation_mode prevents the
        subsequent day-selected event from being treated as a
        confirmed date selection.

        :param calendar: The Gtk.Calendar that emitted the signal.
        """
        self.navigation_mode = True
