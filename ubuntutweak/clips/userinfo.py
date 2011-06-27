import os
from gi.repository import Gtk, GLib

from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import EasyTable

class UserInfo(Clip):
    __icon__  = 'config-users'
    __title__ = _('User Information')

    def __init__(self):
        Clip.__init__(self)

        self.table = EasyTable(items=(
                        (Gtk.Label(label=_('Current user:')),
                         Gtk.Label(label=GLib.get_user_name())),
                        (Gtk.Label(label=_('Home directory:')),
                         Gtk.Label(label=GLib.get_home_dir())),
                        (Gtk.Label(label=_('Shell:')),
                         Gtk.Label(label=GLib.getenv('SHELL'))),
                        (Gtk.Label(label=_('Language:')),
                         Gtk.Label(label=GLib.getenv('LANG')))),
                        xpadding=12, ypadding=2)

        self.add_content(self.table)

        self.show_all()
