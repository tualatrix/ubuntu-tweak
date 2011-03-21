from gi.repository import Gtk

from ubuntutweak import system
from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import EasyTable

class SystemInfo(Clip):
    def __init__(self):
        Clip.__init__(self)

        self.set_image_from_pixbuf(icon.get_from_name('ubuntu-logo', size=48))
        self.set_title(_('Ubuntu Desktop Information'))

        self.table = EasyTable(items=(
                        (Gtk.Label(label=_('Distribution:')),
                         Gtk.Label(label=system.DISTRO)),
                        (Gtk.Label(label=_('Desktop Environment:')),
                         Gtk.Label(label=system.DESKTOP_FULLNAME))),
                        xpadding=12, ypadding=2)
        self.set_content(self.table)
