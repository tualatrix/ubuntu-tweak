from gi.repository import Gdk


def set_busy(window):
    if window and window.get_parent_window():
        window.get_parent_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        window.set_sensitive(False)


def unset_busy(window):
    if window and window.get_parent_window():
        window.get_parent_window().set_cursor(None)
        window.set_sensitive(True)
