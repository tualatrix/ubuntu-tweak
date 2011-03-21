import os
import glob
from gi.repository import Gtk, GLib

from ubuntutweak import system
from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon

class CleanerInfo(Clip):
    def __init__(self):
        Clip.__init__(self)

        cache_number = len(glob.glob('/var/cache/apt/archives/*.deb'))

        self.set_image_from_pixbuf(icon.get_from_name('edit-clear', size=48))

        if cache_number:
            self.set_title(_('Some cache can be cleaned to free your disk space'))
        else:
            self.set_title(_('Your system is clean'))

        label = Gtk.Label(label=_('%s cache packages can be cleaned.') % cache_number)
        label.set_alignment(0, 0.5)

        self.set_content(label)
