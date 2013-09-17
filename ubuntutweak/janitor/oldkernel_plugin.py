import os
import re
import logging

from distutils.version import LooseVersion
from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, PackageObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.common.debug import log_func, get_traceback


log = logging.getLogger('OldKernelPlugin')


class OldKernelPlugin(JanitorPlugin):
    __title__ = _('Old Kernel')
    __category__ = 'system'

    p_kernel_version = re.compile('[.\d]+-\d+')
    p_kernel_package = re.compile('linux-[a-z\-]+')

    def __init__(self):
        JanitorPlugin.__init__(self)
        try:
            self.current_kernel_version = self.p_kernel_version.findall('-'.join(os.uname()[2].split('-')[:2]))[0]
            log.debug("the current_kernel_version is %s" % self.current_kernel_version)
        except Exception, e:
            log.error(e)
            self.current_kernel_version = '3.2.0-36'

    def get_cruft(self):
        try:
            cache = AptWorker.get_cache()
            count = 0
            size = 0

            if cache:
                for pkg in cache:
                    if pkg.is_installed and self.is_old_kernel_package(pkg.name):
                        log.debug("Find old kernerl: %s" % pkg.name)
                        count += 1
                        size += pkg.installed.size
                        self.emit('find_object',
                                  PackageObject(pkg.name, pkg.name, pkg.installed.size),
                                  count)

            self.emit('scan_finished', True, count, size)
        except Exception, e:
            error = get_traceback()
            log.error(error)
            self.emit('scan_error', error)

    def clean_cruft(self, cruft_list=[], parent=None):
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

    def is_old_kernel_package(self, pkg):
        basenames = ['linux-image', 'linux-image-extra', 'linux-headers',
                     'linux-image-debug', 'linux-ubuntu-modules',
                     'linux-header-lum', 'linux-backport-modules',
                     'linux-header-lbm', 'linux-restricted-modules']

        if pkg.startswith('linux'):
            package = self.p_kernel_package.findall(pkg)
            if package:
                package = package[0].rstrip('-')
            else:
                return False

            if package in basenames:
                match = self.p_kernel_version.findall(pkg)
                if match and self._compare_kernel_version(match[0]):
                    return True
        return False

    @log_func(log)
    def _compare_kernel_version(self, version):
        c1, c2 = self.current_kernel_version.split('-')
        p1, p2 = version.split('-')
        if c1 == p1:
            if int(c2) > int(p2):
                return True
            else:
                return False
        else:
            return LooseVersion(c1) > LooseVersion(p1)

    def get_summary(self, count):
        if count:
            return '[%d] %s' % (count, self.__title__)
        else:
            return _('Old Kernel Packages (No old kernel package to be removed)')
