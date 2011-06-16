import os
import glob
from gi.repository import Gtk, GLib

from ubuntutweak import system
from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon

class CleanerInfo(Clip):
    __icon__  = 'computer-janitor'

    def __init__(self):
        Clip.__init__(self)

        cache_number = len(glob.glob('/var/cache/apt/archives/*.deb'))

        if cache_number:
            self.set_title(_('Some cache can be cleaned to free your disk space'))
        else:
            self.set_title(_('Your system is clean'))

        label = Gtk.Label(label=_('%s cache packages can be cleaned.') % cache_number)
        label.set_alignment(0, 0.5)

        self.set_content(label)

        try:
            size = int(os.popen('du -bs ~/.thumbnails').read().split()[0])
        except:
            size = 0

        if size:

            label = Gtk.Label(label=_('%s thumbnails cache can be cleaned.') % \
                    GLib.format_size_for_display(size))
            label.set_alignment(0, 0.5)

            self.set_content(label)

        button = Gtk.Button(label=_('Start Janitor'))
        button.connect('clicked', self.on_button_clicked)
        self.add_action_button(button)

        self.show_all()

    def on_button_clicked(self, widget):
        self.emit('load_feature', 'janitor')
