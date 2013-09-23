# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
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
import json
import thread
import logging

from gi.repository import Gtk, GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
from xdg.DesktopEntry import DesktopEntry

from ubuntutweak.common import consts
from ubuntutweak.common.debug import log_func
from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.dialogs import ErrorDialog, InfoDialog, QuestionDialog
from ubuntutweak.gui.dialogs import ProcessDialog
from ubuntutweak.gui.gtk import post_ui, set_busy, unset_busy
from ubuntutweak.utils.parser import Parser
from ubuntutweak.network import utdata
from ubuntutweak.network.downloadmanager import DownloadDialog
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.utils import set_label_for_stock_button, icon
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.apps import CategoryView

log = logging.getLogger("AppCenter")

APPCENTER_ROOT = os.path.join(consts.CONFIG_ROOT, 'appcenter')
APP_VERSION_URL = utdata.get_version_url('/appcenter_version/')
UPDATE_SETTING = GSetting(key='com.ubuntu-tweak.tweak.appcenter-has-update', type=bool)
VERSION_SETTING = GSetting(key='com.ubuntu-tweak.tweak.appcenter-version', type=str)

def get_app_data_url():
    return utdata.get_download_url('/media/utdata/appcenter-%s.tar.gz' %
                                   VERSION_SETTING.get_value())

if not os.path.exists(APPCENTER_ROOT):
    os.mkdir(APPCENTER_ROOT)


class PackageInfo:
    DESKTOP_DIR = '/usr/share/app-install/desktop/'

    def __init__(self, name):
        self.name = name
        self.pkg = AptWorker.get_cache()[name]
        self.desktopentry = DesktopEntry(self.DESKTOP_DIR + name + '.desktop')

    def check_installed(self):
        return self.pkg.isInstalled

    def get_comment(self):
        return self.desktopentry.getComment()

    def get_name(self):
        appname = self.desktopentry.getName()
        if appname == '':
            return self.name.title()

        return appname

    def get_version(self):
        try:
            return self.pkg.versions[0].version
        except:
            return ''


class StatusProvider(object):
    def __init__(self, name):
        self._path = os.path.join(consts.CONFIG_ROOT, name)
        self._is_init = False

        try:
            self._data = json.loads(open(self._path).read())
        except:
            log.debug('No Status data available, set init to True')
            self._data = {'apps': {}, 'cates': {}}
            self._is_init = True

    def set_init(self, active):
        self._is_init = active

    def get_init(self):
        return self._is_init

    def get_data(self):
        return self._data

    def save(self):
        file = open(self._path, 'w')
        file.write(json.dumps(self._data))
        file.close()

    def load_objects_from_parser(self, parser):
        init = self.get_init()

        for key in parser.keys():
            #FIXME because of source id
            if init:
                self._data['apps'][key] = {}
                self._data['apps'][key]['read'] = True
                self._data['apps'][key]['cate'] = parser.get_category(key)
            else:
                if key not in self._data['apps']:
                    self._data['apps'][key] = {}
                    self._data['apps'][key]['read'] = False
                    self._data['apps'][key]['cate'] = parser.get_category(key)

        if init and parser.keys():
            self.set_init(False)

        self.save()

    def count_unread(self, cate):
        i = 0
        for key in self._data['apps']:
            if self._data['apps'][key]['cate'] == cate and not self._data['apps'][key]['read']:
                i += 1
        return i

    def load_category_from_parser(self, parser):
        for cate in parser.keys():
            id = parser.get_id(cate)
            if self._is_init:
                self._data['cates'][id] = 0
            else:
                self._data['cates'][id] = self.count_unread(id)

        self._is_init = False
        self.save()

    def get_cate_unread_count(self, id):
        return self.count_unread(id)

    def get_read_status(self, key):
        try:
            return self._data['apps'][key]['read']
        except:
            return True

    def set_as_read(self, key):
        try:
            self._data['apps'][key]['read'] = True
        except:
            pass
        self.save()

class AppParser(Parser):
    def __init__(self):
        app_data = os.path.join(APPCENTER_ROOT, 'apps.json')

        Parser.__init__(self, app_data, 'package')

    def get_summary(self, key):
        return self.get_by_lang(key, 'summary')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

    def get_category(self, key):
        return self[key]['category']


class AppCategoryView(CategoryView):

    def pre_update_cate_model(self):
        self.model.append(None, (-1,
                                 'installed-apps',
                                 _('Installed Apps')))


class AppView(Gtk.TreeView):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST,
                    None,
                    (GObject.TYPE_INT,)),
        'select': (GObject.SignalFlags.RUN_FIRST,
                    None,
                    (GObject.TYPE_BOOLEAN,))
    }

    (COLUMN_INSTALLED,
     COLUMN_ICON,
     COLUMN_PKG,
     COLUMN_NAME,
     COLUMN_DESC,
     COLUMN_DISPLAY,
     COLUMN_CATE,
     COLUMN_TYPE,
    ) = range(8)

    def __init__(self):
        GObject.GObject.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.filter = None
        self._status = None

        model = self._create_model()
        self._add_columns()
        self.set_model(model)

        self.set_rules_hint(True)
        self.set_search_column(self.COLUMN_NAME)

        self.show_all()

    def _create_model(self):
        model = Gtk.ListStore(
                        GObject.TYPE_BOOLEAN,
                        GdkPixbuf.Pixbuf,
                        GObject.TYPE_STRING,
                        GObject.TYPE_STRING,
                        GObject.TYPE_STRING,
                        GObject.TYPE_STRING,
                        GObject.TYPE_STRING,
                        GObject.TYPE_STRING)

        return model

    def sort_model(self):
        model = self.get_model()
        model.set_sort_column_id(self.COLUMN_NAME, Gtk.SortType.ASCENDING)

    def _add_columns(self):
        renderer = Gtk.CellRendererToggle()
        renderer.set_property("xpad", 6)
        renderer.connect('toggled', self.on_install_toggled)

        column = Gtk.TreeViewColumn('', renderer, active=self.COLUMN_INSTALLED)
        column.set_sort_column_id(self.COLUMN_INSTALLED)
        self.append_column(column)

        column = Gtk.TreeViewColumn('Applications')
        column.set_sort_column_id(self.COLUMN_NAME)
        column.set_spacing(5)
        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, self.icon_column_view_func)
        column.add_attribute(renderer, 'pixbuf', self.COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        renderer.set_property("xpad", 6)
        renderer.set_property("ypad", 6)
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'markup', self.COLUMN_DISPLAY)
        self.append_column(column)

    def set_as_read(self, iter, model):
        package = model.get_value(iter, self.COLUMN_PKG)
        if self._status and not self._status.get_read_status(package):
            appname = model.get_value(iter, self.COLUMN_NAME)
            desc = model.get_value(iter, self.COLUMN_DESC)
            self._status.set_as_read(package)
            model.set_value(iter, self.COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))

    def icon_column_view_func(self, tree_column, renderer, model, iter, data=None):
        pixbuf = model.get_value(iter, self.COLUMN_ICON)
        if pixbuf == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def append_update(self, status, pkgname, summary):
        model = self.get_model()

        icontheme = Gtk.IconTheme.get_default()
        for icon_name in ['application-x-deb', 'package-x-generic', 'package']:
            icon_theme = icontheme.lookup_icon(icon_name,
                                               size=32,
                                               flags=Gtk.IconLookupFlags.NO_SVG)
            if icon_theme:
                break

        if icon_theme:
            pixbuf = icon_theme.load_icon()
        else:
            pixbuf = icon.get_from_name(size=32)

        iter = model.append()
        model.set(iter,
                  self.COLUMN_INSTALLED, status,
                  self.COLUMN_ICON, pixbuf,
                  self.COLUMN_PKG, pkgname,
                  self.COLUMN_NAME, pkgname,
                  self.COLUMN_DESC, summary,
                  self.COLUMN_DISPLAY, '<b>%s</b>\n%s' % (pkgname, summary),
                  self.COLUMN_TYPE, 'update')

    def set_status_active(self, active):
        if active:
            self._status = StatusProvider('appstatus.json')

    def get_status(self):
        return self._status

    @log_func(log)
    def update_model(self, apps=None, only_installed=False):
        '''apps is a list to iter pkgname,
        '''
        model = self.get_model()
        model.clear()

        app_parser = AppParser()

        if self._status:
            self._status.load_objects_from_parser(app_parser)

        if not apps:
            apps = app_parser.keys()

        for pkgname in apps:
            category = app_parser.get_category(pkgname)
            pixbuf = self.get_app_logo(app_parser[pkgname]['logo'])

            try:
                package = PackageInfo(pkgname)
                is_installed = package.check_installed()
                if not is_installed and only_installed:
                    continue
                appname = package.get_name()
                desc = app_parser.get_summary(pkgname)
            except Exception, e:
                # Confirm the invalid package isn't in the count
                # But in the future, Ubuntu Tweak should display the invalid package too
                if self._status and not self._status.get_read_status(pkgname):
                    self._status.set_as_read(pkgname)
                continue

            if self.filter == None or self.filter == category:
                iter = model.append()
                if pkgname in self.to_add or pkgname in self.to_rm:
                    status = not is_installed
                    display = self.__fill_changed_display(appname, desc)
                else:
                    status = is_installed
                    if self._status and not self._status.get_read_status(pkgname):
                        display = '<b>%s <span foreground="#ff0000">(New!!!)</span>\n%s</b>' % (appname, desc)
                    else:
                        display = '<b>%s</b>\n%s' % (appname, desc)

                model.set(iter,
                          self.COLUMN_INSTALLED, status,
                          self.COLUMN_ICON, pixbuf,
                          self.COLUMN_PKG, pkgname,
                          self.COLUMN_NAME, appname,
                          self.COLUMN_DESC, desc,
                          self.COLUMN_DISPLAY, display,
                          self.COLUMN_CATE, str(category),
                          self.COLUMN_TYPE, 'app')

    def __fill_changed_display(self, appname, desc):
        return '<span style="italic" weight="bold"><b>%s</b>\n%s</span>' % (appname, desc)

    def on_install_toggled(self, cell, path):
        def do_app_changed(model, iter, appname, desc):
            model.set(iter,
                      self.COLUMN_DISPLAY, self.__fill_changed_display(appname, desc))
        def do_app_unchanged(model, iter, appname, desc):
            model.set(iter,
                      self.COLUMN_DISPLAY,
                      '<b>%s</b>\n%s' % (appname, desc))

        model = self.get_model()

        iter = model.get_iter((int(path),))
        is_installed = model.get_value(iter, self.COLUMN_INSTALLED)
        pkgname = model.get_value(iter, self.COLUMN_PKG)
        appname = model.get_value(iter, self.COLUMN_NAME)
        desc = model.get_value(iter, self.COLUMN_DESC)
        type = model.get_value(iter, self.COLUMN_TYPE)

        if pkgname:
            if type == 'app':
                is_installed = not is_installed
                if is_installed:
                    if pkgname in self.to_rm:
                        self.to_rm.remove(pkgname)
                        do_app_unchanged(model, iter, appname, desc)
                    else:
                        self.to_add.append(pkgname)
                        do_app_changed(model, iter, appname, desc)
                else:
                    if pkgname in self.to_add:
                        self.to_add.remove(pkgname)
                        do_app_unchanged(model, iter, appname, desc)
                    else:
                        self.to_rm.append(pkgname)
                        do_app_changed(model, iter, appname, desc)

                model.set(iter, self.COLUMN_INSTALLED, is_installed)
            else:
                to_installed = is_installed
                to_installed = not to_installed
                if to_installed == True:
                    self.to_add.append(pkgname)
                else:
                    self.to_add.remove(pkgname)

                model.set(iter, self.COLUMN_INSTALLED, to_installed)

            self.emit('changed', len(self.to_add) + len(self.to_rm))
        else:
            model.set(iter, self.COLUMN_INSTALLED, not is_installed)
            self.emit('select', not is_installed)

    @log_func(log)
    def set_filter(self, filter):
        self.filter = filter

    def get_app_logo(self, file_name):
        path = os.path.join(APPCENTER_ROOT, file_name)
        if not os.path.exists(path) or file_name == '':
            path = os.path.join(consts.DATA_DIR, 'pixmaps/common-logo.png')

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
            if pixbuf.get_width() != 32 or pixbuf.get_height() != 32:
                pixbuf = pixbuf.scale_simple(32, 32, GdkPixbuf.InterpType.BILINEAR)
            return pixbuf
        except:
            return Gtk.IconTheme.get_default().load_icon(Gtk.STOCK_MISSING_IMAGE, 32, 0)

class CheckUpdateDialog(ProcessDialog):

    def __init__(self, parent, url):
        self.status = None
        self.done = False
        self.error = None
        self.user_action = False
        self.url = url

        super(CheckUpdateDialog, self).__init__(parent=parent)
        self.set_dialog_lable(_('Checking update...'))

    def run(self):
        thread.start_new_thread(self.process_data, ())
        GObject.timeout_add(100, self.on_timeout)
        return super(CheckUpdateDialog, self).run()

    def process_data(self):
        import time
        time.sleep(1)
        try:
            self.status = self.get_updatable()
        except IOError:
            self.error = True
        else:
            self.done = True

    def get_updatable(self):
        return utdata.check_update_function(self.url, APPCENTER_ROOT, \
                                            UPDATE_SETTING, VERSION_SETTING, \
                                            auto=False)

    def on_timeout(self):
        self.pulse()

        if self.error:
            self.destroy()
        elif not self.done:
            return True
        else:
            self.destroy()

class FetchingDialog(DownloadDialog):
    def __init__(self, url, parent=None):
        super(FetchingDialog, self).__init__(url=url,
                                    title=_('Fetching online data...'),
                                    parent=parent)
        log.debug("Will start to download online data from: %s", url)

class AppCenter(TweakModule):
    __title__ = _('Application Center')
    __desc__ = _('A simple but efficient way for finding and installing popular applications.')
    __icon__ = 'gnome-app-install'
    __url__ = 'http://ubuntu-tweak.com/app/'
    __urltitle__ = _('Visit Online Application Center')
    __category__ = 'application'
    __utactive__ = False

    def __init__(self):
        TweakModule.__init__(self, 'appcenter.ui')

        set_label_for_stock_button(self.sync_button, _('_Sync'))

        self.to_add = []
        self.to_rm = []

        self.url = APP_VERSION_URL

        self.appview = AppView()
        self.appview.set_status_active(True)
        self.appview.update_model()
        self.appview.sort_model()
        self.appview.connect('changed', self.on_app_status_changed)
        self.app_selection = self.appview.get_selection()
        self.app_selection.connect('changed', self.on_app_selection)
        self.right_sw.add(self.appview)

        self.cateview = AppCategoryView(os.path.join(APPCENTER_ROOT, 'cates.json'))
        self.cateview.set_status_from_view(self.appview)
        self.cateview.update_cate_model()
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_category_changed)
        self.left_sw.add(self.cateview)

        self.update_timestamp()
        self.show_all()

        UPDATE_SETTING.set_value(False)
        UPDATE_SETTING.connect_notify(self.on_have_update, data=None)

        thread.start_new_thread(self.check_update, ())
        GObject.timeout_add(60000, self.update_timestamp)

        self.add_start(self.main_vbox)

        self.connect('realize', self.setup_ui_tasks)

    def setup_ui_tasks(self, widget):
        self.cateview.expand_all()

    def update_timestamp(self):
        self.time_label.set_text(_('Last synced:') + ' ' + utdata.get_last_synced(APPCENTER_ROOT))
        return True

    @post_ui
    def on_have_update(self, *args):
        log.debug("on_have_update")
        if UPDATE_SETTING.get_value():
            dialog = QuestionDialog(_('New application data available, would you like to update?'))
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                dialog = FetchingDialog(get_app_data_url(), self.get_toplevel())
                dialog.connect('destroy', self.on_app_data_downloaded)
                dialog.run()
                dialog.destroy()

    def check_update(self):
        try:
            return utdata.check_update_function(self.url, APPCENTER_ROOT, \
                                            UPDATE_SETTING, VERSION_SETTING, \
                                            auto=True)
        except Exception, error:
            log.error(error)

    def on_app_selection(self, widget, data=None):
        model, iter = widget.get_selected()
        if iter:
            appview = widget.get_tree_view()
            appview.set_as_read(iter, model)
            self.cateview.update_selected_item()

    @log_func(log)
    def on_category_changed(self, widget, data=None):
        model, iter = widget.get_selected()
        cateview = widget.get_tree_view()

        if iter:
            path = model.get_path(iter).to_string()
            only_installed = False

            if path == '0':
                only_installed = True
                self.appview.set_filter(None)
            elif path == '1':
                self.appview.set_filter(None)
            else:
                self.appview.set_filter(model[iter][cateview.CATE_ID])

            self.appview.update_model(only_installed=only_installed)

    def deep_update(self):
        self.package_worker.update_apt_cache(True)
        self.update_app_data()

    def on_apply_button_clicked(self, widget, data=None):
        @log_func(log)
        def on_install_finished(transaction, status, kwargs):
            to_add, to_rm = kwargs['add_and_rm']
            if to_rm:
                worker = AptWorker(self.get_toplevel(),
                                   finish_handler=self.on_package_work_finished,
                                   data=kwargs)
                worker.remove_packages(to_rm)
            else:
               self.on_package_work_finished(None, None, kwargs)

        to_rm = self.appview.to_rm
        to_add = self.appview.to_add

        log.debug("on_apply_button_clicked: to_rm: %s, to_add: %s" % (to_rm, to_add))

        if to_add or to_rm:
            set_busy(self)

            if to_add:
                worker = AptWorker(self.get_toplevel(),
                                   finish_handler=on_install_finished,
                                   data={'add_and_rm': (to_add, to_rm),
                                         'parent': self})
                worker.install_packages(to_add)
            else:
                on_install_finished(None, None, 
                                   {'add_and_rm': (to_add, to_rm),
                                         'parent': self})

    @log_func(log)
    def on_package_work_finished(self, transaction, status, kwargs):
        to_add, to_rm = kwargs['add_and_rm']
        parent = kwargs['parent']

        AptWorker.update_apt_cache(init=True)

        self.emit('call', 'ubuntutweak.modules.updatemanager', 'update_list', {})

        self.appview.to_add = []
        self.appview.to_rm = []
        self.on_category_changed(self.cateview.get_selection())
        self.apply_button.set_sensitive(False)
        unset_busy(parent)

    def on_sync_button_clicked(self, widget):
        dialog = CheckUpdateDialog(widget.get_toplevel(), self.url)
        dialog.run()
        dialog.destroy()
        if dialog.status == True:
            dialog = QuestionDialog(_("Update available, would you like to update?"))
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                dialog = FetchingDialog(get_app_data_url(), self.get_toplevel())
                dialog.connect('destroy', self.on_app_data_downloaded)
                dialog.run()
                dialog.destroy()
        elif dialog.error == True:
            ErrorDialog(_("Network Error, please check your network connection - or the remote server may be down.")).launch()
        else:
            utdata.save_synced_timestamp(APPCENTER_ROOT)
            self.update_timestamp()
            InfoDialog(_("No update available.")).launch()

    def on_app_data_downloaded(self, widget):
        log.debug("on_app_data_downloaded")
        path = widget.get_downloaded_file()
        tarfile = utdata.create_tarfile(path)

        if tarfile.is_valid():
            tarfile.extract(consts.CONFIG_ROOT)
            self.update_app_data()
            utdata.save_synced_timestamp(APPCENTER_ROOT)
            self.update_timestamp()
        else:
            ErrorDialog(_('An error occurred while downloading the file.')).launch()

    def update_app_data(self):
        self.appview.update_model()
        self.cateview.update_cate_model()
        self.cateview.expand_all()

    def on_app_status_changed(self, widget, i):
        if i:
            self.apply_button.set_sensitive(True)
        else:
            self.apply_button.set_sensitive(False)
