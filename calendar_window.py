from datetime import datetime

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class CalendarWindow(Gtk.Window):
    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_entry):
        super().__init__(title="Select Date")
        self.date_entry = date_entry
        self.set_border_width(10)
        self.set_default_size(250, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_modal(True)
        self.navigation_mode = False

        calendar = Gtk.Calendar()
        calendar.connect("day-selected", self.on_date_selected)  # Single-click selection
        calendar.connect("prev-month", self.on_navigation)
        calendar.connect("next-month", self.on_navigation)
        calendar.connect("prev-year", self.on_navigation)
        calendar.connect("next-year", self.on_navigation)
        self.add(calendar)

    def on_date_selected(self, calendar):
        if not self.navigation_mode:
            year, month, day = calendar.get_date()
            selected_date = datetime(year, month + 1, day).strftime("%m-%d-%Y")

            self.date_entry.set_date(selected_date)
            self.destroy()
            self.emit("date-entered")
        self.navigation_mode = False

    def on_navigation(self, calendar):
        self.navigation_mode = True
