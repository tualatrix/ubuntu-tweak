import os
import glob
import logging

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.policykit.dbusproxy import proxy

log = logging.getLogger('aptcache_plugin')

class CacheObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_path(self):
        return self.path

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')


class AptCachePlugin(JanitorPlugin):
    __title__ = _('Apt Cache')
    __category__ = 'system'

    def __str__(self):
        return 'AptCachePlugin'

    def get_cruft(self):
        cruft_list = glob.glob('/var/cache/apt/archives/*.deb')
        cruft_list.sort()
        size = 0

        for deb in cruft_list:
            current_size = os.path.getsize(deb)
            size += current_size

            self.emit('find_object',
                      CacheObject(os.path.basename(deb), deb, current_size))

        self.emit('scan_finished', True, len(cruft_list), size)

    def on_done(self, widget):
        widget.destroy()

    def clean_cruft(self, cruft_list=[], parent=None):
        for index, cruft in enumerate(cruft_list):
            log.debug('Cleaning...%s' % cruft.get_name())
            result = proxy.delete_apt_cache_file(cruft.get_name())

            if bool(result) == False:
                self.emit('clean_error', cruft.get_name())
                break
            else:
                self.emit('object_cleaned', cruft)

        self.emit('all_cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Apt Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Apt Cache (No cache to be cleaned)')
