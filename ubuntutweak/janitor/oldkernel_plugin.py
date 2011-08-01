import os
import re
import logging

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, PackageObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils import filesizeformat


log = logging.getLogger('OldKernelPlugin')


class OldKernelPlugin(JanitorPlugin):
    __title__ = _('Old Kernel')
    __category__ = 'system'

    def __init__(self):
        JanitorPlugin.__init__(self)
        self.current_kernel_version = '-'.join(os.uname()[2].split('-')[:2])
        log.debug("the current_kernel_version is %s" % self.current_kernel_version)

    def get_cruft(self):
        cache = self.get_cache()
        count = 0
        size = 0

        if cache:
            for pkg in cache:
                if pkg.isInstalled and self.is_old_kernel_package(pkg.name):
                    log.debug("Find old kernerl: %s" % pkg.name)
                    count += 1
                    size += pkg.installedSize
                    self.emit('find_object',
                              PackageObject(pkg.name, pkg.name, pkg.installedSize))

        self.emit('scan_finished', True, count, size)

    def clean_cruft(self, parent, cruft_list):
        set_busy(parent)
        worker = AptWorker(parent, self.on_clean_finished, parent)
        worker.remove_packages([cruft.get_package_name() for cruft in cruft_list])

    def on_clean_finished(self, transaction, status, parent):
        unset_busy(parent)
        self.update_apt_cache(True)
        self.emit('cleaned', True)

    def is_old_kernel_package(self, pkg):
        p_kernel_version = re.compile('[.\d]+-\d+')
        p_kernel_package = re.compile('linux-[a-z\-]+')

        basenames = ['linux-image', 'linux-headers', 'linux-image-debug',
                      'linux-ubuntu-modules', 'linux-header-lum',
                      'linux-backport-modules',
                      'linux-header-lbm', 'linux-restricted-modules']

        if pkg.startswith('linux'):
            package = p_kernel_package.findall(pkg)
            if package:
                package = package[0].rstrip('-')
            else:
                return False

            if package in basenames:
                match = p_kernel_version.findall(pkg)
                if match and self._compare_kernel_version(match[0]):
                    return True
        return False

    def _compare_kernel_version(self, version):
        c1, c2 = self.current_kernel_version.split('-')
        p1, p2 = version.split('-')
        if c1 > p1:
            return True
        elif int(c2) > int(p2):
            return True
        else:
            return False

    def get_summary(self, count, size):
        if count:
            return _('Old Kernel Packages (%d kernel packages to be removed, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Old Kernel Packages (No old kernel package to be removed)')
