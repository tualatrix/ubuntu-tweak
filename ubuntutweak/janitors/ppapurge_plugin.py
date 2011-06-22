import os
import re
import time
import json
import thread
import logging

from urllib2 import urlopen, Request, URLError

import gobject
from aptsources.sourceslist import SourcesList
from gi.repository import Gtk, Pango, GObject

from ubuntutweak import system
from ubuntutweak.common import consts
from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitors import JanitorPlugin, CruftObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils import icon, filesizeformat, ppa
from ubuntutweak.gui.dialogs import TerminalDialog, QuestionDialog, ErrorDialog
from ubuntutweak.policykit import proxy


log = logging.getLogger('PPAPlugin')


class NoNeedDowngradeException(Exception):
    pass


class PPAObject(CruftObject):
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name

    def get_uri(self):
        return self.uri

    def get_icon(self):
        path = os.path.join(consts.DATA_DIR, 'pixmaps/ppa-logo.png')

        return icon.get_from_file(path)

    def get_size_display(self):
        return ''

    def get_size(self):
        return 0


class CleanPpaDialog(TerminalDialog):
    def __init__(self, parent, pkgs, urls):
        #TODO cancel button, refresh apt
        super(CleanPpaDialog, self).__init__(parent=parent)
        self.pkgs = pkgs
        self.urls = urls
        self.downgrade_done = False
        self.removekey_done = False
        self.error = ''
        self.user_action = False

        self.set_dialog_lable(_('Purge PPA and Downgrade Packages'))
        self.set_progress_text(_('Downloading Packages...'))

    def search_for_download_package(self, line):
        pattern = re.compile('%s(-\w+)?\/\w+\ (?P<package>.*?) ' % system.CODENAME)
        match = pattern.search(line)
        if match:
            return match.group('package')
        else:
            return match

    def run(self):
        thread.start_new_thread(self.process_data, ())
        gobject.timeout_add(100, self.on_timeout)
        super(CleanPpaDialog, self).run()

    def process_data(self):
        if self.pkgs:
            log.debug("call proxy.install_select_pkgs")
            proxy.install_select_pkgs(self.pkgs)
            log.debug("done proxy.install_select_pkgs")
        else:
            log.debug("No pkgs to downloaded, just done")
            self.downgrade_done = True

        while True:
            if not self.downgrade_done:
                time.sleep(0.2)
                continue

#            ppa_source_dict = get_ppa_source_dict()

            # Sort out the unique owner urls, so that the PPAs from same owner will only fetch key fingerprint only once
            key_fingerprint_dict = {}
            for url in self.urls:
                #TODO get the key_fingerprint
#                if url in ppa_source_dict:
#                    id = ppa_source_dict[url]
#                    key_fingerprint = SOURCE_PARSER.get_key_fingerprint(id)
#                else:
                key_fingerprint = ''

                owner, ppa_name = url.split('/')[3:5]

                if owner not in key_fingerprint_dict:
                    key_fingerprint_dict[owner] = key_fingerprint
            log.debug("Get the key_fingerprint_dict done: %s" % key_fingerprint_dict)
            for url in self.urls:
                owner, ppa_name = url.split('/')[3:5]
                key_fingerprint = key_fingerprint_dict[owner]

                self.set_progress_text(_('Removing key files...'))
                if not key_fingerprint:
                    try:
                        #TODO wrap the LP API or use library
                        owner, ppa_name = url.split('/')[3:5]
                        lp_url = 'https://launchpad.net/api/beta/~%s/+archive/%s' % (owner, ppa_name)
                        req = Request(lp_url)
                        req.add_header("Accept","application/json")
                        lp_page = urlopen(req).read()
                        data = json.loads(lp_page)
                        key_fingerprint = data['signing_key_fingerprint']
                    except Exception, e:
                        log.error(e)
                        continue

                log.debug("Get the key fingerprint: %s", key_fingerprint)
                result = proxy.purge_source(url, key_fingerprint)
                log.debug("Set source: %s to %s" % (url, str(result)))

            self.removekey_done = True
            log.debug("removekey_done is True")
            break

    def on_timeout(self):
        self.pulse()
        if not self.downgrade_done:
            line, returncode = proxy.get_cmd_pipe()
            if line != '':
                log.debug("Clean PPA result is: %s, returncode is: %s" % (line, returncode))
                line = line.rstrip()

                if '.deb' in line:
                    try:
                        package = line.split('.../')[1].split('_')[0]
                        self.set_progress_text(_('Downgrading...%s') % package)
                    except Exception, e:
                        log.error(e)
                else:
                    package = self.search_for_download_package(line)

                    if package:
                        self.set_progress_text(_('Downloading...%s') % package)

                if line:
                    self.terminal.insert(line)
                else:
                    self.terminal.insert('\n')

            # TODO if returncode isn't 0?
            if returncode.isdigit() and int(returncode) > 1:
                self.error = line
            elif returncode != 'None':
                log.debug("downgrade_done, returncode is: %s" % returncode)
                self.downgrade_done = True

        if self.error:
            self.destroy()
        elif not self.downgrade_done or not self.removekey_done:
            return True
        else:
            self.destroy()


class DowngradeView(Gtk.TreeView):
    __gsignals__ = {
        'checked': (GObject.SignalFlags.RUN_FIRST, None,
                    (GObject.TYPE_BOOLEAN,)),
        'cleaned': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    (COLUMN_PKG,
     COLUMN_PPA_VERSION,
     COLUMN_SYSTEM_VERSION) = range(3)

    def __init__(self, plugin):
        gobject.GObject.__init__(self)

        model = Gtk.ListStore(GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)
        self.set_model(model)
        model.set_sort_column_id(self.COLUMN_PKG, Gtk.SortType.ASCENDING)

        self.plugin = plugin

        self._add_column()

    def _add_column(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Package'))
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'text', self.COLUMN_PKG)
        column.set_sort_column_id(self.COLUMN_PKG)
        self.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        column = Gtk.TreeViewColumn(_('Previous Version'))
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.COLUMN_PPA_VERSION)
        column.set_resizable(True)
        column.set_min_width(180)
        self.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        column = Gtk.TreeViewColumn(_('System Version'))
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.COLUMN_SYSTEM_VERSION)
        column.set_resizable(True)
        self.append_column(column)

    def update_model(self, ppas):
        model = self.get_model()
        model.clear()
        pkg_dict = {}
        for ppa_url in ppas:
            path = ppa.get_list_name(ppa_url)
            log.debug('Find the PPA path name: %s', path)
            if path:
                for line in open(path):
                    if line.startswith('Package:'):
                        pkg = line.split()[1].strip()
                        if pkg in pkg_dict:
                            # Join another ppa info to the pkg dict, so that
                            # later we can know if more than two ppa provide
                            # the pkg
                            pkg_dict[pkg].extend([ppa_url])
                        else:
                            pkg_dict[pkg] = [ppa_url]

        pkg_map = self.plugin.get_downgradeable_pkgs(pkg_dict)

        if pkg_map:
            log.debug("Start insert pkg_map to model: %s\n" % str(pkg_map))
            for pkg, (p_verion, s_verion) in pkg_map.items():
                model.append((pkg, p_verion, s_verion))

    def get_downgrade_packages(self):
        model = self.get_model()
        downgrade_list = []
        for row in model:
            pkg, version = row[self.COLUMN_PKG], row[self.COLUMN_SYSTEM_VERSION]
            downgrade_list.append("%s=%s" % (pkg, version))
        log.debug("The package to downgrade is %s" % str(downgrade_list))
        return downgrade_list


class PPAPlugin(JanitorPlugin):
    __title__ = _('PPA')
    __category__ = 'system'

    def get_cruft(self):
        count = 0

        for source in SourcesList():
            if ppa.is_ppa(source.uri) and source.type == 'deb' and not source.disabled:
                count += 1
                name = ppa.get_short_name(source.uri)

                self.emit('find_object', PPAObject(source.uri, name))

        self.emit('scan_finished', True, count, 0)

    def clean_cruft(self, parent, cruft_list):
        set_busy(parent)

        # name_list is to display the name of PPA
        # url_list is to identify the ppa
        name_list = []
        url_list = []
        for cruft in cruft_list:
            name_list.append(ppa.get_short_name(cruft.get_uri()))
            url_list.append(cruft.get_uri())

        package_view = DowngradeView(self)
        package_view.update_model(url_list)
        sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        select_pkgs = package_view.get_downgrade_packages()
        sw.add(package_view)

        #TODO the logic is a little ugly, need to improve the BaseMessageDialog
        if not select_pkgs:
            message = _("It's safe to purge the PPA, no packages need to be downgraded.")
            sw.hide()
        else:
            message = _("To safely purge the PPA, the following packages must be downgraded.")
            sw.show_all()
            sw.set_size_request(500, 100)

        dialog = QuestionDialog(message=message,
                                title=_("You're going to purge: %s") % ', '.join(name_list))
        dialog.set_resizable(True)
        dialog.get_content_area().pack_start(sw, True, True, 0)
        dialog.show()

        response = dialog.run()
        dialog.destroy()
        # Workflow
        # 1. Downgrade all the PPA packages to offical packages
        #TODO Maybe not official? Because anther ppa which is enabled may have newer packages then offical
        # 2. If succeed, disable PPA, or keep it

        if response == Gtk.ResponseType.YES:
            log.debug("The select pkgs is: %s", str(select_pkgs))
            dialog = CleanPpaDialog(parent, select_pkgs, url_list)
            dialog.run()
            dialog.destroy()
            if dialog.error:
                log.error("Error: %s" % dialog.error)
                ErrorDialog(dialog.error).launch()
        # TODO refresh source?

        self.emit('cleaned', True)
        unset_busy(parent)

    def get_downgradeable_pkgs(self, ppa_dict):
        def is_system_origin(version, urls):
            origins = [ppa.get_ppa_origin_name(url) for url in urls]
            system_version = 0
            match = False

            for origin in version.origins:
                if origin.origin:
                    if origin.origin not in origins:
                        log.debug("The origin %s is not in %s, so end the loop" % (origin.origin, str(origins)))
                        match = True
                        break

            if match:
                system_version = version.version
                log.debug("Found match url, the system_version is %s, now iter to system version" % system_version)

            return system_version

        def is_full_match_ppa_origin(pkg, version, urls):
            origins = [ppa.get_ppa_origin_name(url) for url in urls]
            ppa_version = 0
            match = True

            if version == pkg.installed:
                for origin in version.origins:
                    if origin.origin:
                        if origin.origin not in origins:
                            log.debug("The origin %s is not in %s, so end the loop" % (origin.origin, str(origins)))
                            match = False
                            break

                if match:
                    ppa_version = version.version
                    log.debug("Found match url, the ppa_version is %s, now iter to system version" % ppa_version)

            return ppa_version

        log.debug("Check downgrade information")
        downgrade_dict = {}
        for pkg, urls in ppa_dict.items():
            log.debug("The package is: %s, PPA URL is: %s" % (pkg, str(urls)))

            if pkg not in self.get_cache():
                log.debug("    package isn't available, continue next...\n")
                continue

            pkg = self.get_cache()[pkg]
            if not pkg.isInstalled:
                log.debug("    package isn't installed, continue next...\n")
                continue
            versions = pkg.versions

            ppa_version = 0
            system_version = 0
            FLAG = 'PPA'
            try:
                for version in versions:
                    try:
                        #FIXME option to remove the package
                        log.debug("Version uri is %s" % version.uri)

                        # Switch FLAG
                        if FLAG == 'PPA':
                            ppa_version = is_full_match_ppa_origin(pkg, version, urls)
                            FLAG = 'SYSTEM'
                            if ppa_version == 0:
                                raise NoNeedDowngradeException
                        else:
                            system_version = is_system_origin(version, urls)

                        if ppa_version and system_version:
                            downgrade_dict[pkg.name] = (ppa_version, system_version)
                            break
                    except StopIteration:
                        pass
            except NoNeedDowngradeException:
                log.debug("Catch NoNeedDowngradeException, so pass this package: %s" % pkg)
                continue
            log.debug("\n")
        return downgrade_dict

    def get_summary(self, count, size):
        if count:
            return _('%d PPAs to be removed') % count
        else:
            return _('No PPA to be removed')
