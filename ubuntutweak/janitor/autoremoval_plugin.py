from gi.repository import Gtk

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.utils.package import AptWorker


class PackageObject(CruftObject):
    def __init__(self, name, package_name, size):
        self.name = name
        self.package_name = package_name
        self.size = size

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')

    def get_package_name(self):
        return self.package_name


class AutoRemovalPlugin(JanitorPlugin):
    __title__ = _('Unneeded Packages')
    __category__ = 'system'

    def get_cruft(self):
        cache = self.get_cache()
        if cache:
            for pkg in cache.keys():
                p = self.cache[pkg]
                if p.isAutoRemovable:
                    yield PackageObject(p.summary, p.name, p.installedSize)

    def clean_cruft(self, parent, cruft_list):
        set_busy(parent)
        worker = AptWorker(parent, self.on_clean_finished, parent)
        worker.remove_packages([cruft.get_package_name() for cruft in cruft_list])

    def on_clean_finished(self, transaction, status, parent):
        unset_busy(parent)
        self.update_apt_cache(True)
        self.emit('cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Unneeded Packages (%d packages to be removed, total size: %s') % (count, filesizeformat(size))
        else:
            return _('Unneeded Packages (No package to be removed)')
