import os
from gettext import ngettext

from gi.repository import Gio

def get_command_for_type(mime):
    try:
        return Gio.app_info_get_default_for_type('text/plain', False).get_executable()
    except:
        if os.path.exists('/usr/bin/gedit'):
            return 'gedit'
        elif os.path.exists('/usr/bin/leafpad'):
            return 'leafpad'
        elif os.path.exists('/usr/bin/gvim'):
            return 'gvim'
        else:
            return None


def set_label_for_stock_button(button, text):
    label = button.get_child().get_child().get_children()[1]
    label.set_text_with_mnemonic(text)


def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    try:
        bytes = float(bytes)
    except TypeError:
        return "0 bytes"

    if bytes < 1024:
        return ngettext("%(size)d byte", "%(size)d bytes", bytes) % {'size': bytes}
    if bytes < 1024 * 1024:
        return _("%.1f KB") % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return _("%.1f MB") % (bytes / (1024 * 1024))
    return _("%.1f GB") % (bytes / (1024 * 1024 * 1024))
