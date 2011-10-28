from gi.repository import Gdk


def set_busy(window):
    if window and window.get_parent_window():
        window.get_parent_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        window.set_sensitive(False)


def unset_busy(window):
    if window and window.get_parent_window():
        window.get_parent_window().set_cursor(None)
        window.set_sensitive(True)

def post_ui(func):
    def func_wrapper(*args, **kwargs):
        Gdk.threads_enter()
        func(*args, **kwargs)
        Gdk.threads_leave()

    return func_wrapper

