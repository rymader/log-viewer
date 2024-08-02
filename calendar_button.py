# calendar_button.py
import gi

from calendar_window import CalendarWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class CalendarButton(Gtk.Button):
    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_entry):
        super().__init__(label=date_entry.get_date_type())

        self.calendar_window = None

        self.date_entry = date_entry
        self.connect("clicked", self.on_button_clicked)

    def on_button_clicked(self, button):
        if self.calendar_window:
            self.calendar_window.destroy()  # Close any existing calendar window

        # Create a new calendar popup
        self.calendar_window = CalendarWindow(self.date_entry)
        self.calendar_window.connect("date-entered", self.on_date_selected)

        # Show the calendar window
        self.calendar_window.show_all()

    def on_date_selected(self, calendar):
        self.emit("date-entered")
