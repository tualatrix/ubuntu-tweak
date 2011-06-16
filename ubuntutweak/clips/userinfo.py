import os
from gi.repository import Gtk, GLib

from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import EasyTable

class UserInfo(Clip):
    def __init__(self):
        Clip.__init__(self)

        self.set_title(_('User Information'))

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
        self.set_content(self.table)

        self.show_all()

    def get_image_pixbuf(self):
        return icon.get_from_name('config-users', size=48)
