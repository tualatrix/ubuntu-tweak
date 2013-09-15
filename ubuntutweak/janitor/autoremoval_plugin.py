import logging

from gi.repository import Gtk

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, PackageObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils import filesizeformat


log = logging.getLogger('AutoRemovalPlugin')

class AutoRemovalPlugin(JanitorPlugin):
    __title__ = _('Unneeded Packages')
    __category__ = 'system'

    def get_cruft(self):
        cache = AptWorker.get_cache()
        count = 0
        size = 0
        if cache:
            for pkg in cache:
                if pkg.is_auto_removable and not pkg.name.startswith('linux'):
                    count += 1
                    size += pkg.installed.size
                    self.emit('find_object',
                              PackageObject(pkg.installed.summary, pkg.name, pkg.installed.size),
                              count)

        self.emit('scan_finished', True, count, size)

    def clean_cruft(self, parent=None, cruft_list=[]):
        set_busy(parent)
        worker = AptWorker(parent,
                           finish_handler=self.on_clean_finished,
                           error_handler=self.on_error,
                           data=parent)
        worker.remove_packages([cruft.get_package_name() for cruft in cruft_list])

    def on_error(self, error):
        log.error('AptWorker error with: %s' % error)
        self.emit('clean_error', error)

    def on_clean_finished(self, transaction, status, parent):
        unset_busy(parent)
        AptWorker.update_apt_cache(True)
        self.emit('all_cleaned', True)

    def get_summary(self, count):
        if count:
            return '[%d] %s' % (count, self.__title__)
        else:
            return _('Unneeded Packages (No package to be removed)')
