from gettext import ngettext
from gettext import gettext as _

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
