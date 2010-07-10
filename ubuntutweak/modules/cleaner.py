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
import gtk
import thread
import glob
import gobject
import logging
import pango
from dbus.exceptions import DBusException
from aptsources.sourceslist import SourcesList
from gettext import ngettext

from ubuntutweak.common.consts import install_ngettext
from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.utils import *
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.common.package import PACKAGE_WORKER
from ubuntutweak.widgets.dialogs import *
from ubuntutweak.widgets.utils import ProcessDialog, SmartTerminal, TerminalDialog
from ubuntutweak.modules.sourcecenter import SOURCE_PARSER, PPA_URL
from ubuntutweak.modules.sourcecenter import get_source_logo_from_filename
from ubuntutweak.modules.sourcecenter import get_ppa_homepage

log = logging.getLogger("Cleaner") 

(
    COLUMN_CHECK,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
) = range(5)

install_ngettext()

def get_ppa_list_name(url):
    section = url.split('/')
    log.debug("The ppa sections is %s", str(section))
    name = '/var/lib/apt/lists/ppa.launchpad.net_%s_%s_*_Packages' % (section[3], section[4])
    names = glob.glob(name)
    if len(names) == 1:
        return names[0]
    else:
        return ''

def get_ppa_short_name(url):
    section = url.split('/')
    log.debug("The ppa sections is %s", str(section))
    return 'ppa:%s/%s' % (section[3], section[4])

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
        self.set_progress_text(_('Cleaning...%s') % line)

        line, returncode = proxy.get_cmd_pipe()
        log.debug("Clean config result is: %s" % line)
        if line != '':
            line = line.rstrip()
            if line:
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
        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)

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
    def __init__(self, parent, pkgs):
        super(CleanPpaDialog, self).__init__(parent=parent)
        self.pkgs = pkgs
        self.done = False
        self.error = False
        self.user_action = False

        self.set_dialog_lable(_('Purge PPA and Downgrade Packages'))
        self.set_progress_text(_('Purge...'))
        self.expendar.set_label(_('Details'))

    def process_data(self):
        proxy.install_select_pkgs(self.pkgs)

    def on_timeout(self):
        self.pulse()
        line, returncode = proxy.get_cmd_pipe()
        log.debug("Clean PPA result is: %s" % line)
        if line != '':
            line = line.rstrip()
            if '.deb' in line:
                try:
                    package = line.split('.../')[1].split('_')[0]
                    self.set_progress_text(_('Purge...%s') % package)
                except:
                    pass
            if line:
                self.terminal.insert(line)
            else:
                self.terminal.insert('\n')
        if returncode != 'None':
            self.done = True

        if not self.done:
            return True
        else:
            self.destroy()

class DowngradeView(gtk.TreeView):
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
        model.set_sort_column_id(self.COLUMN_PKG, gtk.SORT_ASCENDING)

        self.PACKAGE_WORKER = PACKAGE_WORKER

        self.__add_column()

    def __create_model(self):
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Package'), renderer, text=self.COLUMN_PKG)
        column.set_sort_column_id(self.COLUMN_PKG)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn(_('Previous Version'), renderer, text=self.COLUMN_PPA_VERSION)
        column.set_resizable(True)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn(_('System Version'), renderer, text=self.COLUMN_SYSTEM_VERSION)
        column.set_resizable(True)
        self.append_column(column)

    def update_model(self, ppas):
        model = self.get_model()
        model.clear()
        pkg_dict = {}
        for ppa in ppas:
            path = get_ppa_list_name(ppa)
            if path:
                for line in open(path):
                    if line.startswith('Package:'):
                        pkg = line.split()[1].strip()
                        pkg_dict[pkg] = ppa

                pkg_map = PACKAGE_WORKER.get_downgradeable_pkgs(pkg_dict)
                if pkg_map:
                    for pkg, (p_verion, s_verion) in pkg_map.items():
                        model.append((pkg, p_verion, s_verion))
                else:
                    model.append(("No package need to be downgraded", "", ""))

    def get_downgrade_packages(self):
        model = self.get_model()
        downgrade_list = []
        for row in model:
            pkg, version = row[self.COLUMN_PKG], row[self.COLUMN_SYSTEM_VERSION]
            downgrade_list.append("%s=%s" % (pkg, version))
        log.debug("The package to downgrade is %s" % str(downgrade_list))
        return downgrade_list

class PackageView(gtk.TreeView):
    __gsignals__ = {
        'checked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, 
                    (gobject.TYPE_BOOLEAN,)),
        'cleaned': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        super(PackageView, self).__init__()

        model = self.__create_model()
        self.set_model(model)
        model.set_sort_column_id(COLUMN_NAME, gtk.SORT_ASCENDING)

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
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_package_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_CHECK)
        column.set_sort_column_id(COLUMN_CHECK)
        self.append_column(column)

        self.__column = gtk.TreeViewColumn(_('Package'))
        self.__column.set_sort_column_id(COLUMN_NAME)
        self.__column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        self.__column.pack_start(renderer, False)
        self.__column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
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

        icon = get_icon_with_name('deb', 24)
        list = self.PACKAGE_WORKER.list_autoremovable()
        self.total_num = len(list)
        self.__column.set_title(_('Packages'))

        while gtk.events_pending():
            gtk.main_iteration()

        for pkg in list:
            desc = self.PACKAGE_WORKER.get_pkgsummary(pkg)

            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, icon,
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

        icon = get_icon_with_name('deb', 24)
        list = self.PACKAGE_WORKER.list_unneeded_kerenl()
        self.total_num = len(list)
        self.__column.set_title(_('Packages'))

        while gtk.events_pending():
            gtk.main_iteration()

        for pkg in list:
            desc = self.PACKAGE_WORKER.get_pkgsummary(pkg)

            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, icon,
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
        icon = get_icon_with_name('deb', 24)
        list = map(lambda file: '%s/%s' % (cache_dir, file),
                    filter(lambda x:x.endswith('deb'), os.listdir(cache_dir))) 
        self.total_num = len(list)
        self.__column.set_title(_('Package Cache'))

        while gtk.events_pending():
            gtk.main_iteration()

        for pkg in list:
            size = str(os.path.getsize(pkg))

            iter = model.append()
            model.set(iter,
                   COLUMN_ICON, icon,
                   COLUMN_CHECK, False,
                   COLUMN_NAME, pkg,
                   COLUMN_DESC, size,
                   COLUMN_DISPLAY, _('<b>%s</b>\nOccupies %s of disk space') % (os.path.basename(pkg), filesizeformat(size)) 

                )
        self.unset_busy()

    def update_ppa_model(self):
        self.set_busy()
        model = self.get_model()
        model.clear()
        self.mode = 'ppa'

        ppa_source_dict = {}
        for id in SOURCE_PARSER:
            url = SOURCE_PARSER.get_url(id)
            ppa_source_dict[url] = id

        for source in self.get_sourceslist():
            if PPA_URL in source.uri and source.type == 'deb' and not source.disabled:
                try:
                    id = ppa_source_dict[source.uri]
                    pixbuf = get_source_logo_from_filename(SOURCE_PARSER[id]['logo'])
                    name = SOURCE_PARSER.get_name(id)
                    comment = SOURCE_PARSER.get_summary(id)
                except:
                    id = source.uri
                    name = get_ppa_short_name(source.uri)
                    comment = get_ppa_homepage(source.uri)
                    pixbuf = get_source_logo_from_filename('')

                self.total_num += 1
                iter = model.append()
                log.debug("Found an enalbed PPA: %s" % name)
                model.set(iter,
                       COLUMN_ICON, pixbuf,
                       COLUMN_CHECK, False,
                       COLUMN_NAME, id,
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
        icon = get_icon_with_name('text', 24)

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

        while gtk.events_pending():
            gtk.main_iteration()

        for pkg in list:
            iter = model.append()
            model.set(iter,
                   COLUMN_CHECK, False,
                   COLUMN_ICON, icon,
                   COLUMN_NAME, pkg.name,
                   COLUMN_DESC, 0,
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
        if dialog.run() == gtk.RESPONSE_REJECT:
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
                name_list.append(get_ppa_short_name(id))
                url_list.append(id)

        dialog = QuestionDialog(_("You're going to purge: %s") % ', '.join(name_list))
        dialog.set_resizable(True)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(550, 200)
        dialog.vbox.pack_start(sw, False, False, 0)

        package_view = DowngradeView()
        package_view.update_model(url_list)
        select_pkgs = package_view.get_downgrade_packages()
        sw.add(package_view)
        dialog.show_all()

        response = dialog.run()
        dialog.destroy()
        # Workflow
        # 1. Downgrade all the PPA packages to offical packages #TODO Maybe not official? Because anther ppa which is enabled may have newer packages then offical
        # 2. If succeed, disable PPA, or keep it

        if response == gtk.RESPONSE_YES:
            self.set_busy()
            log.debug("The select pkgs is: %s", str(select_pkgs))
            dialog = CleanPpaDialog(self.get_toplevel(), select_pkgs)
            dialog.run()
            dialog.destroy()
            if dialog.error == False:
                for url in url_list:
                    result = proxy.set_source_enable(url, False)
                    log.debug("Set source: %s to %s" % (url, str(result)))
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
            window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

    def unset_busy(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(None)

class PackageCleaner(TweakModule):
    __title__ = _('Package Cleaner')
    __desc__ = _('Free up disk space by removing redundant packages and cleaning the package download cache.')
    __icon__ = 'edit-clear'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.button_list = []
        self.current_button = 0

        hbox = gtk.HBox(False, 0)
        self.add_start(hbox, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        vbox = gtk.VBox(False, 8)
        hbox.pack_start(vbox, False, False, 5)

        # create tree view
        self.treeview = PackageView()
        self.treeview.set_rules_hint(True)
        self.treeview.connect('checked', self.on_item_checked)
        self.treeview.connect('cleaned', self.on_item_cleaned)
        sw.add(self.treeview)

        # create the button
        self.pkg_button = self.create_button(_('Clean Packages'),
                gtk.image_new_from_pixbuf(get_icon_with_name('deb', 24)),
                self.treeview.update_package_model)
        vbox.pack_start(self.pkg_button, False, False, 0)

        self.cache_button = self.create_button(_('Clean Cache'), 
                gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON),
                self.treeview.update_cache_model)
        vbox.pack_start(self.cache_button, False, False, 0)

        self.config_button = self.create_button(_('Clean Config'),
                gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_BUTTON),
                self.treeview.update_config_model)
        vbox.pack_start(self.config_button, False, False, 0)

        self.kernel_button = self.create_button(_('Clean Kernels'),
                gtk.image_new_from_pixbuf(get_icon_with_name('start-here', 24)),
                self.treeview.update_kernel_model)
        vbox.pack_start(self.kernel_button, False, False, 0)

        self.ppa_button = self.create_button(_('Purge PPAs'),
                gtk.image_new_from_pixbuf(get_icon_with_name('start-here', 24)),
                self.treeview.update_ppa_model)
        vbox.pack_start(self.ppa_button, False, False, 0)

        # checkbutton
        self.select_button = gtk.CheckButton(_('Select All'))
        self.select_button.set_sensitive(False)
        self.__handler_id = self.select_button.connect('toggled', self.on_select_all)
        self.add_start(self.select_button, False, False, 0)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 5)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 5)

        self.clean_button = gtk.Button(stock=gtk.STOCK_CLEAR)
        set_label_for_stock_button(self.clean_button, _('_Cleanup'))
        self.clean_button.connect('clicked', self.on_clean_button_clicked)
        self.clean_button.set_sensitive(False)
        hbox.pack_end(self.clean_button, False, False, 5)

        self.show_all()

    def create_button(self, text, image, function):
        button = gtk.ToggleButton(text)
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
