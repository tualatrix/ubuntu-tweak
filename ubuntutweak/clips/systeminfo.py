import os
from gi.repository import Gtk

from ubuntutweak import system
from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import EasyTable

class SystemInfo(Clip):
    __icon__ = 'ubuntu-logo'
    __title__ = _('Ubuntu Desktop Information')

    def __init__(self):
        Clip.__init__(self)

        self.table = EasyTable(items=(
                        (Gtk.Label(label=_('Hostname:')),
                         Gtk.Label(label=os.uname()[1])),
                        (Gtk.Label(label=_('Platform:')),
                         Gtk.Label(label=os.uname()[-1])),
                        (Gtk.Label(label=_('Distribution:')),
                         Gtk.Label(label=system.DISTRO)),
                        (Gtk.Label(label=_('Desktop Environment:')),
                         Gtk.Label(label=system.DESKTOP_FULLNAME))),
                        xpadding=12, ypadding=2)
        self.add_content(self.table)

        self.show_all()
