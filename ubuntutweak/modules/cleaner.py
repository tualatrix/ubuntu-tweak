#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
from gi.repository import Gdk
from gi.repository import Gtk
import json
from gi.repository import Pango
import thread
import gobject
import logging

from urllib2 import urlopen, Request, URLError
from dbus.exceptions import DBusException
from aptsources.sourceslist import SourcesList
from gettext import ngettext

from ubuntutweak.common.consts import install_ngettext
from ubuntutweak.modules  import TweakModule
from ubuntutweak.utils import icon, set_label_for_stock_button, ppa
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.common.package import PACKAGE_WORKER
from ubuntutweak.ui.dialogs import QuestionDialog, InfoDialog, ErrorDialog
from ubuntutweak.ui.dialogs import AuthenticateFailDialog, ProcessDialog, TerminalDialog
from ubuntutweak.modules.sourcecenter import SOURCE_PARSER
from ubuntutweak.modules.sourcecenter import get_source_logo_from_filename

log = logging.getLogger("Cleaner")

(
    COLUMN_CHECK,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
) = range(5)

install_ngettext()

def get_ppa_source_dict():
    ppa_source_dict = {}
    for id in SOURCE_PARSER:
        url = SOURCE_PARSER.get_url(id)
        ppa_source_dict[url] = id

    return ppa_source_dict

class AbsPkg:
    def __init__(self, pkg, des):
        self.name = pkg
        self.des = des

class CleanConfigDialog(TerminalDialog):
    def __init__(self, parent, pkgs):
        super(CleanConfigDialog, self).__init__(parent=parent)
        self.pkgs = pkgs
        self.done = False
        self.error = False

        self.set_dialog_lable(_('Cleaning Configuration Files'))

    def process_data(self):
        proxy.clean_configs(self.pkgs)
        
    def on_timeout(self):
        self.pulse()

        line, returncode = proxy.get_cmd_pipe()
        log.debug("Clean config result is: %s" % line)
        if line != '':
            line = line.rstrip()
            if line:
                self.set_progress_text(line)
                self.terminal.insert(line)
            else:
                self.terminal.insert('\n')

        if returncode != 'None':
            self.done = True
            if returncode != '0':
                self.error = False

        if not self.done:
            return True
        else:
            self.destroy()

class CleanCacheDailog(ProcessDialog):
    def __init__(self, parent, files):
        super(CleanCacheDailog, self).__init__(parent=parent)
        self.files = files
        self.done = False
        self.error = False
        self.user_action = False

        self.set_dialog_lable(_('Cleaning Package Cache'))
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)

    def process_data(self):
        for file in self.files:
            if self.user_action == True:
                break
            self.set_progress_text(_('Cleaning...%s') % os.path.basename(file))
            result = proxy.delete_file(file)
            if result == 'error':
                self.error = True
                break
        self.done = True

    def on_timeout(self):
        self.pulse()

        if not self.done:
            return True
        else:
            self.destroy()

class CleanPpaDialog(TerminalDialog):
    def __init__(self, parent, pkgs, urls):
        super(CleanPpaDialog, self).__init__(parent=parent)
        self.pkgs = pkgs
        self.urls = urls
        self.downgrade_done = False
        self.removekey_done = False
        self.error = False
        self.user_action = False

        self.set_dialog_lable(_('Purge PPA and Downgrade Packages'))
        self.set_progress_text(_('Downloading Packages...'))

    def process_data(self):
        if self.pkgs:
            proxy.install_select_pkgs(self.pkgs)
        else:
            self.downgrade_done = True

        ppa_source_dict = get_ppa_source_dict()

        # Sort out the unique owner urls, so that the PPAs from same owner will only fetch key fingerprint only once
        key_fingerprint_dict = {}
        for url in self.urls:
            if url in ppa_source_dict:
                id = ppa_source_dict[url]
                key_fingerprint = SOURCE_PARSER.get_key_fingerprint(id)
            else:
                key_fingerprint = ''

            owner, ppa_name = url.split('/')[3:5]

            if owner not in key_fingerprint_dict:
                key_fingerprint_dict[owner] = key_fingerprint

        for url in self.urls:
            owner, ppa_name = url.split('/')[3:5]
            key_fingerprint = key_fingerprint_dict[owner]

            self.set_progress_text(_('Removing key files...'))
            if not key_fingerprint:
                try:
                    #TODO wrap the LP API or use library
                    owner, ppa_name = url.split('/')[3:5]
                    lp_url = 'https://launchpad.net/api/beta/~%s/+archive/%s' % (owner, ppa_name)
                    req =  Request(lp_url)
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

    def on_timeout(self):
        self.pulse()
        if not self.downgrade_done:
            line, returncode = proxy.get_cmd_pipe()
            log.debug("Clean PPA result is: %s, returncode is: %s" % (line, returncode))
            if line != '':
                line = line.rstrip()
                if '.deb' in line:
                    try:
                        package = line.split('.../')[1].split('_')[0]
                        self.set_progress_text(_('Downgrading...%s') % package)
                    except:
                        pass
                if line:
                    self.terminal.insert(line)
                else:
                    self.terminal.insert('\n')

            # TODO if returncode isn't 0?
            if returncode != 'None':
                self.downgrade_done = True

        if not self.removekey_done:
            return True
        else:
            self.destroy()

class DowngradeView(Gtk.TreeView):
    __gsignals__ = {
        'checked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, 
                    (gobject.TYPE_BOOLEAN,)),
        'cleaned': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    (COLUMN_PKG,
     COLUMN_PPA_VERSION,
     COLUMN_SYSTEM_VERSION) = range(3)

    def __init__(self):
        super(DowngradeView, self).__init__()

        model = self.__create_model()
        self.set_model(model)
        model.set_sort_column_id(self.COLUMN_PKG, Gtk.SortType.ASCENDING)

        self.PACKAGE_WORKER = PACKAGE_WORKER

        self.__add_column()

    def __create_model(self):
        model = Gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Package'), renderer, text=self.COLUMN_PKG)
        column.set_sort_column_id(self.COLUMN_PKG)
        self.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        column = Gtk.TreeViewColumn(_('Previous Version'), renderer, text=self.COLUMN_PPA_VERSION)
        column.set_resizable(True)
        column.set_min_width(180)
        self.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        column = Gtk.TreeViewColumn(_('System Version'), renderer, text=self.COLUMN_SYSTEM_VERSION)
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

        pkg_map = PACKAGE_WORKER.get_downgradeable_pkgs(pkg_dict)
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

class PackageView(Gtk.TreeView):
    __gsignals__ = {
        'checked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, 
                    (gobject.TYPE_BOOLEAN,)),
        'cleaned': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        super(PackageView, self).__init__()

        model = self.__create_model()
        self.set_model(model)
        model.set_sort_column_id(COLUMN_NAME, Gtk.SortType.ASCENDING)

        self.__check_list = []
        self.PACKAGE_WORKER = PACKAGE_WORKER

        self.__add_column()

        self.mode = 'package'
        self.update_package_model()
        self.selection = self.get_selection()
        self.set_sensitive(False)

    def get_sourceslist(self):
        return SourcesList()

    def __create_model(self):
        model = Gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                GdkPixbuf.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = Gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_package_toggled)
        column = Gtk.TreeViewColumn(' ', renderer, active = COLUMN_CHECK)
        column.set_sort_column_id(COLUMN_CHECK)
        self.append_column(column)

        self.__column = Gtk.TreeViewColumn(_('Package'))
        self.__column.set_sort_column_id(COLUMN_NAME)
        self.__column.set_spacing(5)
        renderer = Gtk.CellRendererPixbuf()
        self.__column.pack_start(renderer, False)
        self.__column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        self.__column.pack_start(renderer, True)
        self.__column.set_attributes(renderer, markup = COLUMN_DISPLAY)

        self.append_column(self.__column)

    def get_list(self):
        return self.__check_list

    def update_package_model(self):
        self.set_busy()
        model = self.get_model()
        model.clear()
        self.mode = 'package'

        pixbuf = icon.get_from_name('deb')
        list = self.PACKAGE_WORKER.list_autoremovable()
        self.total_num = len(list)
        self.__column.set_title(_('Unneeded Packages'))

        while Gtk.events_pending():
            Gtk.main_iteration()

        for pkg in list:
            desc = self.PACKAGE_WORKER.get_pkgsummary(pkg)

            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, pixbuf,
                   COLUMN_NAME, pkg,
                   COLUMN_DESC, desc,
                   COLUMN_DISPLAY, '<b>%s</b>\n%s' % (pkg, desc)
                )

        self.unset_busy()

    def update_kernel_model(self):
        self.set_busy()
        model = self.get_model()
        model.clear()
        self.mode = 'kernel'

        pixbuf = icon.get_from_name('deb')
        list = self.PACKAGE_WORKER.list_unneeded_kerenl()
        self.total_num = len(list)
        self.__column.set_title(_('Kernel Packages'))

        while Gtk.events_pending():
            Gtk.main_iteration()

        for pkg in list:
            desc = self.PACKAGE_WORKER.get_pkgsummary(pkg)

            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, pixbuf,
                   COLUMN_NAME, pkg,
                   COLUMN_DESC, desc,
                   COLUMN_DISPLAY, '<b>%s</b>\n%s' % (pkg, desc)
                )
        self.unset_busy()

    def update_cache_model(self):
        self.set_busy()
        model = self.get_model()
        model.clear()
        self.mode = 'cache'

        cache_dir = '/var/cache/apt/archives' 
        pixbuf = icon.get_from_name('deb')
        list = map(lambda file: '%s/%s' % (cache_dir, file),
                    filter(lambda x:x.endswith('deb'), os.listdir(cache_dir))) 
        self.total_num = len(list)
        self.__column.set_title(_('Cached Package Files'))

        while Gtk.events_pending():
            Gtk.main_iteration()

        for pkg in list:
            size = str(os.path.getsize(pkg))

            iter = model.append()
            model.set(iter,
                   COLUMN_ICON, pixbuf,
                   COLUMN_CHECK, False,
                   COLUMN_NAME, pkg,
                   COLUMN_DESC, size,
                   COLUMN_DISPLAY, _('<b>%s</b>\nOccupies %s of disk space') % (os.path.basename(pkg), filesizeformat(size)) 

                )
        self.unset_busy()

    def update_ppa_model(self):
        self.set_busy()
        self.__column.set_title('PPA Sources')
        model = self.get_model()
        model.clear()
        self.mode = 'ppa'

        ppa_source_dict = get_ppa_source_dict()

        for source in self.get_sourceslist():
            if ppa.is_ppa(source.uri) and source.type == 'deb' and not source.disabled:
                try:
                    id = ppa_source_dict[source.uri]
                    pixbuf = get_source_logo_from_filename(SOURCE_PARSER[id]['logo'])
                    name = SOURCE_PARSER.get_name(id)
                    comment = SOURCE_PARSER.get_summary(id)
                except:
                    id = source.uri
                    name = ppa.get_short_name(source.uri)
                    comment = ppa.get_homepage(source.uri)
                    pixbuf = get_source_logo_from_filename('')

                self.total_num += 1
                iter = model.append()
                log.debug("Found an enalbed PPA: %s" % name)
                model.set(iter,
                       COLUMN_ICON, pixbuf,
                       COLUMN_CHECK, False,
                       COLUMN_NAME, str(id),
                       COLUMN_DESC, '',
                       COLUMN_DISPLAY, '<b>%s</b>\n%s' % (name, comment),
                    )
        self.unset_busy()

    def update_config_model(self):
        self.set_busy()
        model = self.get_model()
        model.clear()
        self.mode = 'config'
#        command = "dpkg -l |awk '/^rc/ {print $2}'"
        pixbuf = icon.get_from_name('text')

        list = []
        for line in os.popen('dpkg -l'):
            try:
                temp_list = line.split()
                status, pkg = temp_list[0], temp_list[1]
                if status == 'rc':
                    des = temp_list[3:]
                    pkg = AbsPkg(pkg, ' '.join(temp_list[3:]))
                    list.append(pkg) 
            except:
                pass

        self.total_num = len(list)
        self.__column.set_title(_('Package Configuration Files'))

        while Gtk.events_pending():
            Gtk.main_iteration()

        for pkg in list:
            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, pixbuf,
                   COLUMN_NAME, pkg.name,
                   COLUMN_DESC, '',
                   COLUMN_DISPLAY, '<b>%s</b>\n%s' % (pkg.name, pkg.des),
                )
        self.unset_busy()

    def on_package_toggled(self, cell, path):
        model = self.get_model()
        iter = model.get_iter(path)

        check = model.get_value(iter, COLUMN_CHECK)
        model.set(iter, COLUMN_CHECK, not check)
        if not check:
            self.__check_list.append(model.get_value(iter, COLUMN_NAME))
        else:
            self.__check_list.remove(model.get_value(iter, COLUMN_NAME))

        if len(self.__check_list) == self.total_num:
            self.emit('checked', True)
        else:
            self.emit('checked', False)

        self.set_column_title()

    def set_column_title(self):
        if self.mode == 'package' or self.mode == 'kernel':
            n = len(self.__check_list)
            self.__column.set_title(ngettext('%d package selected for removal',
                '%d packages selected for removal', n) % n)
        elif self.mode == 'cache':
            self.compute_cache_size()
            self.__column.set_title(_('%s of disk space will be freed') % filesizeformat(self.size))

    def compute_cache_size(self):
        self.size = 0

        model = self.get_model()
        model.foreach(self.__cache_foreach)

    def __cache_foreach(self, model, path, iter):
        cache = model.get_value(iter, COLUMN_NAME)

        if cache in self.__check_list:
            size = model.get_value(iter, COLUMN_DESC)
            self.size = self.size + int(size)

    def select_all(self, check = True):
        self.__check_list = []

        model = self.get_model()
        model.foreach(self.__select_foreach, check)
        self.emit('checked', check)

        self.set_column_title()

    def __select_foreach(self, model, path, iter, check):
        model.set(iter, COLUMN_CHECK, check)
        if check:
            self.__check_list.append(model.get_value(iter, COLUMN_NAME))

    def clean_selected_package(self):
        self.set_busy()
        state = self.PACKAGE_WORKER.perform_action(self.get_toplevel(), [],self.__check_list)

        if state == 0:
            self.show_success_dialog()
        else:
            self.show_failed_dialog()

        PACKAGE_WORKER.update_apt_cache(True)
        if self.mode == 'package':
            self.update_package_model()
        else:
            self.update_kernel_model()
        self.__check_list = []
        self.emit('cleaned')
        self.unset_busy()

    def clean_selected_cache(self):
        self.set_busy()
        model = self.get_model()

        dialog = CleanCacheDailog(self.get_toplevel(), self.get_list())
        if dialog.run() == Gtk.ResponseType.REJECT:
            dialog.destroy()
            dialog.user_action = True
            self.show_usercancel_dialog()

        if not dialog.user_action:
            if dialog.error == False:
                self.show_success_dialog()
            else:
                self.show_failed_dialog()

        self.update_cache_model()
        self.emit('cleaned')
        self.unset_busy()

    def clean_selected_config(self):
        self.set_busy()
        model = self.get_model()

        dialog = CleanConfigDialog(self.get_toplevel(), self.get_list())
        dialog.run()
        dialog.destroy()
        if dialog.error == True:
            self.show_failed_dialog()
        else:
            self.show_success_dialog()

        PACKAGE_WORKER.update_apt_cache(True)
        self.update_config_model()
        self.emit('cleaned')
        self.unset_busy()

    def clean_selected_ppa(self):
        self.set_busy()
        # name_list is to display the name of PPA
        # url_list is to identify the ppa
        name_list = []
        url_list = []
        for id in self.get_list():
            #TODO
            try:
                name_list.append(SOURCE_PARSER.get_name(int(id)))
                url_list.append(SOURCE_PARSER.get_url(int(id)))
            except:
                name_list.append(ppa.get_short_name(id))
                url_list.append(id)

        package_view = DowngradeView()
        package_view.update_model(url_list)
        sw = Gtk.ScrolledWindow()
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

        dialog = QuestionDialog(message, title=_("You're going to purge: %s") % ', '.join(name_list))
        dialog.set_resizable(True)
        dialog.vbox.pack_start(sw, True, True, 0)
        dialog.show()

        response = dialog.run()
        dialog.destroy()
        # Workflow
        # 1. Downgrade all the PPA packages to offical packages #TODO Maybe not official? Because anther ppa which is enabled may have newer packages then offical
        # 2. If succeed, disable PPA, or keep it

        if response == Gtk.ResponseType.YES:
            self.set_busy()
            log.debug("The select pkgs is: %s", str(select_pkgs))
            dialog = CleanPpaDialog(self.get_toplevel(), select_pkgs, url_list)
            dialog.run()
            dialog.destroy()
            if dialog.error == False:
                self.show_success_dialog()
            else:
                self.show_failed_dialog()
            self.update_ppa_model()
            self.unset_busy()
        else:
            self.update_ppa_model()
        # TODO refresh source?
        self.__check_list = []
        self.emit('cleaned')
        self.unset_busy()

    def show_usercancel_dialog(self):
        InfoDialog(_('Cancelled by user!')).launch()

    def show_success_dialog(self):
        InfoDialog(_('Clean up successful!')).launch()

    def show_failed_dialog(self):
        ErrorDialog(_('Clean up failed!')).launch()

    def set_busy(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(Gdk.Cursor.new(Gdk.WATCH))

    def unset_busy(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(None)

class PackageCleaner(TweakModule):
    __title__ = _('Package Cleaner')
    __desc__ = _('Free up disk space by removing redundant packages and cleaning package download cache.')
    __icon__ = 'edit-clear'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.button_list = []
        self.current_button = 0

        hbox = Gtk.HBox(False, 12)
        self.add_start(hbox, True, True, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox.pack_start(sw, True, True, 0)

        vbox = Gtk.VBox(False, 6)
        hbox.pack_start(vbox, False, False, 0)

        # create tree view
        self.treeview = PackageView()
        self.treeview.set_rules_hint(True)
        self.treeview.connect('checked', self.on_item_checked)
        self.treeview.connect('cleaned', self.on_item_cleaned)
        sw.add(self.treeview)

        # create the button
        self.pkg_button = self.create_button(_('Clean Packages'),
                Gtk.image_new_from_pixbuf(icon.get_from_name('deb')),
                self.treeview.update_package_model)
        vbox.pack_start(self.pkg_button, False, False, 0)

        self.cache_button = self.create_button(_('Clean Cache'), 
                Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.BUTTON),
                self.treeview.update_cache_model)
        vbox.pack_start(self.cache_button, False, False, 0)

        self.config_button = self.create_button(_('Clean Config'),
                Gtk.Image.new_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.BUTTON),
                self.treeview.update_config_model)
        vbox.pack_start(self.config_button, False, False, 0)

        self.kernel_button = self.create_button(_('Clean Kernels'),
                Gtk.image_new_from_pixbuf(icon.get_from_name('start-here')),
                self.treeview.update_kernel_model)
        vbox.pack_start(self.kernel_button, False, False, 0)

        self.ppa_button = self.create_button(_('Purge PPAs'),
                Gtk.image_new_from_pixbuf(icon.get_from_name('start-here')),
                self.treeview.update_ppa_model)
        vbox.pack_start(self.ppa_button, False, False, 0)

        # checkbutton
        self.select_button = Gtk.CheckButton(_('Select All'))
        self.select_button.set_sensitive(False)
        self.__handler_id = self.select_button.connect('toggled', self.on_select_all)
        self.add_start(self.select_button, False, False, 0)

        # button
        hbuttonbox = Gtk.HButtonBox()
        hbuttonbox.set_spacing(12)
        hbuttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        self.add_end(hbuttonbox, False ,False, 0)

        self.clean_button = Gtk.Button(stock=Gtk.STOCK_CLEAR)
        set_label_for_stock_button(self.clean_button, _('_Cleanup'))
        self.clean_button.connect('clicked', self.on_clean_button_clicked)
        self.clean_button.set_sensitive(False)
        hbuttonbox.pack_end(self.clean_button, False, False, 0)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbuttonbox.pack_end(un_lock, False, False, 0)

        self.show_all()

    def create_button(self, text, image, function):
        button = Gtk.ToggleButton(text)
        if len(self.button_list) == 0:
            button.set_active(True)
        self.button_list.append(button)
        button.set_image(image)
        button.set_data('handler', button.connect('toggled', self.on_button_toggled))
        button.set_data('function', function)

        return button

    def on_select_all(self, widget):
        check = widget.get_active()

        self.treeview.select_all(check)

    def on_item_checked(self, widget, all):
        list = widget.get_list()
        if list:
            self.clean_button.set_sensitive(True)
        else:
            self.clean_button.set_sensitive(False)

        self.select_button.handler_block(self.__handler_id)
        if all:
            self.select_button.set_active(True)
        else:
            self.select_button.set_active(False)
        self.select_button.handler_unblock(self.__handler_id)

    def on_item_cleaned(self, widget):
        self.select_button.set_active(False)
        self.clean_button.set_sensitive(False)

    def on_button_toggled(self, widget):
        self.select_button.set_active(False)

        if self.current_button != self.button_list.index(widget):
            button = self.button_list[self.current_button]

            handler = button.get_data('handler')
            button.handler_block(handler)
            button.set_active(False)
            button.handler_unblock(handler)

            widget.set_active(True)
            self.current_button = self.button_list.index(widget)

            function = widget.get_data('function')
            function()
        elif self.current_button == self.button_list.index(widget):
            widget.set_active(True)

    def on_clean_button_clicked(self, widget):
        if proxy.is_authorized():
            mode = self.treeview.mode
            if mode == 'package' or mode == 'kernel':
                self.treeview.clean_selected_package()
            elif mode == 'cache':
                self.treeview.clean_selected_cache()
            elif mode == 'config':
                self.treeview.clean_selected_config()
            elif mode == 'ppa':
                self.treeview.clean_selected_ppa()
        else:
            return

    def on_polkit_action(self, widget, action):
        if action:
            self.treeview.set_sensitive(True)
            self.select_button.set_sensitive(True)
        else:
            AuthenticateFailDialog().launch()
