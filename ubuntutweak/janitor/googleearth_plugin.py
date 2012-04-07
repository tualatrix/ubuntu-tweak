import os
import glob
import shutil
import logging

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat

log = logging.getLogger('googleearth_plugin')

class GoogleearthObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_path(self):
        return self.path

    def get_name(self):
        return '%s' % self.name

    def get_icon(self):
        return icon.get_from_name('text-plain')

    def get_size_display(self):
        return filesizeformat(self.size)


class GoogleearthCachePlugin(JanitorPlugin):
    __title__ = _('Google Earth Cache')
    __category__ = 'application'

    root_path = os.path.expanduser('~/.googleearth')

    def __str__(self):
        return 'GoogleEarthCachePlugin'

    def get_cruft(self):
        try:
            count = 0
            total_size = 0
            for root, dirs, files in os.walk(self.root_path):
                if root == self.root_path and dirs:
                    for dir in dirs:
                        dir_path = os.path.join(self.root_path, dir)

                        try:
                            size = os.popen('du -bs "%s"' % dir_path).read().split()[0]
                        except:
                            size = 0
                        count += 1
                        total_size += int(size)

                        self.emit('find_object',
                                  GoogleearthObject(dir, dir_path, size))
                    else:
                        continue

            self.emit('scan_finished', True, count, total_size)
        except Exception, e:
            log.error(e)
            self.emit('scan_error', e)

    def on_done(self, widget):
        widget.destroy()

    def clean_cruft(self, cruft_list=[], parent=None):
        for index, cruft in enumerate(cruft_list):
            log.debug('Cleaning...%s' % cruft.get_name())
            shutil.rmtree(cruft.get_path())
            self.emit('object_cleaned', cruft)

        self.emit('all_cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Google Earth Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Google Earth Cache (No cache to be cleaned)')
