import os
import shutil
import glob

import gobject
from gi.repository import Gtk

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.gui.dialogs import ProcessDialog


class ThumbnailObject(CruftObject):
    def __init__(self, name, path, length, size):
        self.name = name
        self.path = path
        self.length = length
        self.size = size

    def get_path(self):
        return self.path

    def get_name(self):
        return '%s (%d thumbnails)' % (self.name, self.length)

    def get_icon(self):
        return icon.get_from_name('image-x-generic')

    def get_size_display(self):
        return filesizeformat(self.size)


class CleanThumbnailDailog(ProcessDialog):

    def __init__(self, parent, cruft_list):
        super(CleanThumbnailDailog, self).__init__(parent=parent)

        self.cruft_list = cruft_list

        self.set_dialog_lable(_('Cleaning Thumbnail Cache'))
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)

    def run(self):
        gobject.timeout_add(100, self.process_data)
        return super(CleanThumbnailDailog, self).run()

    def process_data(self):
        length = len(self.cruft_list)

        for index, cruft in enumerate(self.cruft_list):
            while Gtk.events_pending():
                Gtk.main_iteration()

            self.set_fraction((index + 1.0) / length)
            self.set_progress_text(_('Cleaning...%s') % cruft.get_name())
            shutil.rmtree(cruft.get_path())

        self.destroy()


class ThumbnailCachePlugin(JanitorPlugin):
    __title__ = _('Thumbnail cache')
    __category__ = 'personal'

    def get_cruft(self):
        try:
            count = 0
            total_size = 0
            for root, dirs, files in os.walk(os.path.expanduser('~/.thumbnails')):
                if files:
                    length = len(files)

                    try:
                        size = os.popen('du -bs "%s"' % root).read().split()[0]
                    except:
                        size = 0
                    count += 1
                    total_size += int(size)

                    self.emit('find_object',
                              ThumbnailObject(os.path.basename(root), root, length, size))

            self.emit('scan_finished', True, count, total_size)
        except Exception, e:
            self.emit('error', e)

    def clean_cruft(self, parent, cruft_list):
        dialog = CleanThumbnailDailog(parent, cruft_list)

        if dialog.run() == Gtk.ResponseType.REJECT:
            dialog.destroy()

        self.emit('cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Thumbnail Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Thumbnail Cache (No cache to be cleaned)')
