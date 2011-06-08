import os
import glob

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat

class CacheObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')


class AptCachePlugin(JanitorPlugin):
    __title__ = _('Apt Cache')
    __category__ = 'system'

    def get_cruft(self):
        for deb in glob.glob('/var/cache/apt/archives/*.deb'):
            yield CacheObject(os.path.basename(deb), deb, os.path.getsize(deb))

    def clean_cruft(self, cruft):
        print 'clean cruft', cruft
        return True

    def get_sumarry(self, count, size):
        return _('Apt Cache (%d packages to be cleaned, total size: %s') % (count, filesizeformat(size))
