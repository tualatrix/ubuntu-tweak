import os
import shutil
import glob
import logging

from gi.repository import GObject, Gtk

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.gui.dialogs import ProcessDialog
from ubuntutweak.gui.gtk import post_ui


log = logging.getLogger('thumbnailcache_plugin')

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
            self.emit('scan_error', e)

    def clean_cruft(self, cruft_list=None, parent=None):
        for index, cruft in enumerate(cruft_list):
            log.debug('Cleaning...%s' % cruft.get_name())
            shutil.rmtree(cruft.get_path())
            self.emit('object_cleaned', cruft)

        self.emit('all_cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Thumbnail Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Thumbnail Cache (No cache to be cleaned)')
