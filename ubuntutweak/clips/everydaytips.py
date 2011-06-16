import os
import glob
from gi.repository import Gtk, GLib

from ubuntutweak import system
from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon

class EverydayTips(Clip):
    __icon__  = 'info'

    def __init__(self):
        Clip.__init__(self)

        self.set_title(_('Everyday Tips'))

        label = Gtk.Label(label=_('Use "sudo apt-get update" to upgrade your system'))
        label.set_alignment(0, 0.5)

        self.set_content(label)

        self.show_all()
