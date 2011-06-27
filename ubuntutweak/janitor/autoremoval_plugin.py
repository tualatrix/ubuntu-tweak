from gi.repository import Gtk

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, PackageObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils import filesizeformat


class AutoRemovalPlugin(JanitorPlugin):
    __title__ = _('Unneeded Packages')
    __category__ = 'system'

    def get_cruft(self):
        cache = self.get_cache()
        count = 0
        size = 0
        if cache:
            for pkg in cache:
                if pkg.isAutoRemovable:
                    count += 1
                    size += pkg.installedSize
                    self.emit('find_object',
                              PackageObject(pkg.summary, pkg.name, pkg.installedSize))

        self.emit('scan_finished', True, count, size)

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
            return _('Unneeded Packages (%d packages to be removed, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Unneeded Packages (No package to be removed)')
