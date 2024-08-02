import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class DateEntry(Gtk.Box):
    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_type):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.date_type = date_type
        self.date_entry = Gtk.Entry()
        self.date_entry.set_placeholder_text("MM-DD-YYYY")
        self.date_entry.connect("changed", self.on_date_entry_changed)

        self.pack_start(self.date_entry, True, True, 0)

    def set_date(self, date_str):
        self.date_entry.set_text(date_str)

    def get_date(self):
        return self.date_entry.get_text().strip()

    def get_date_type(self):
        return self.date_type

    def on_date_entry_changed(self, widget):
        self.emit("date-entered")
