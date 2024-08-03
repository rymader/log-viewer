import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from toolbar import Toolbar


class LogViewer(Gtk.Window):
    def __init__(self):
        super().__init__(title="Log Viewer")

        self.set_border_width(10)
        self.set_default_size(600, 150)

        # Create a vertical box layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Create a horizontal toolbar at the top
        self.toolbar = Toolbar(self.on_button_clicked)
        vbox.pack_start(self.toolbar, False, False, 0)

        # Create a ScrolledWindow to hold the TextView
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0)

        # Create a TextView widget to display the output
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.textview)  # Add TextView to the ScrolledWindow

    def on_button_clicked(self, widget):
        start_date = self.toolbar.start_date
        end_date = self.toolbar.end_date

        process = subprocess.Popen(['python3', 'log_reader.py', start_date, end_date], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Update the TextView with the script's output
        buffer = self.textview.get_buffer()

        buffer.set_text(stdout.decode('utf-8') + stderr.decode('utf-8'))
        self.resize(1500, 1000)
