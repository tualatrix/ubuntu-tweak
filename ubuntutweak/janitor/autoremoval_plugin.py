from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat

class PackageObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_size(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')


class AutoRemovalPlugin(JanitorPlugin):
    __title__ = _('Unneeded Packages')
    __category__ = 'system'

    def get_cruft(self):
        cache = self.get_cache()
        if cache:
            for pkg in cache.keys():
                p = self.cache[pkg]
                if p.isAutoRemovable:
                    yield PackageObject(p.summary, p.name, p.installedPackageSize)

    def clean_cruft(self, cruft):
        print 'clean cruft', cruft
        return True
