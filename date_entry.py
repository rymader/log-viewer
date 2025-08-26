import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class DateEntry(Gtk.Box):
    __gsignals__ = {
        'date-entered': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, date_type):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._date_type = date_type
        self._date_entry = Gtk.Entry()
        self._date_entry.set_placeholder_text("MM-DD-YYYY")
        self._date_entry.connect("changed", self.on_date_entry_changed)

        self.pack_start(self._date_entry, True, True, 0)

    @property
    def date_type(self):
        return self._date_type

    @property
    def date(self):
        return self._date_entry.get_text()

    @date.setter
    def date(self, date):
        self._date_entry.set_text(date)

    def on_date_entry_changed(self, widget):
        self.emit("date-entered")
