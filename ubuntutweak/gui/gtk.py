from gi.repository import Gdk


def set_busy(window):
    if window:
        window.window.set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        window.set_sensitive(False)


def unset_busy(window):
    if window:
        window.window.set_cursor(None)
        window.set_sensitive(True)
