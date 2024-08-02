# main.py
from log_viewer import LogViewer
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if __name__ == "__main__":
    win = LogViewer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
