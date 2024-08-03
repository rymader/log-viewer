from datetime import datetime

import gi

gi.require_version('Gtk', '3.0')
from calendar_button import CalendarButton
from date_entry import DateEntry
from gi.repository import Gtk


class Toolbar(Gtk.Box):
    def __init__(self, callback):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.callback = callback

        # Create start date entry and button
        self.start_date_entry = DateEntry("Start Date")
        self.start_date_entry.connect("date-entered", self.on_date_changed)
        self.start_calendar = CalendarButton(self.start_date_entry)
        self.start_calendar.connect("date-entered", self.on_date_changed)
        self.pack_start(self.start_calendar, False, False, 0)
        self.pack_start(self.start_date_entry, False, False, 0)

        # Create end date entry and button
        self.end_date_entry = DateEntry("End Date")
        self.end_date_entry.connect("date-entered", self.on_date_changed)
        self.end_calendar = CalendarButton(self.end_date_entry)
        self.end_calendar.connect("date-entered", self.on_date_changed)
        self.pack_start(self.end_calendar, False, False, 0)
        self.pack_start(self.end_date_entry, False, False, 0)

        # Create a button to view logs
        self.view_logs_button = Gtk.Button(label="View Logs")
        self.view_logs_button.set_sensitive(False)  # Initially disabled
        self.view_logs_button.connect("clicked", self.callback)
        self.pack_start(self.view_logs_button, False, False, 0)

    def on_date_changed(self, widget=None):
        # Enable the button only if both date fields are populated
        start_date_text = self.start_date_entry.date
        end_date_text = self.end_date_entry.date

        if start_date_text and end_date_text:
            try:
                datetime.strptime(start_date_text, "%m-%d-%Y")
                datetime.strptime(end_date_text, "%m-%d-%Y")
                self.view_logs_button.set_sensitive(True)
            except ValueError:
                self.view_logs_button.set_sensitive(False)
        else:
            self.view_logs_button.set_sensitive(False)

    @property
    def start_date(self):
        return self.start_date_entry.date

    @property
    def end_date(self):
        return self.end_date_entry.date
