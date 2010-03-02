
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
import time
import json
import gobject
import pango
import thread

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets.dialogs import ErrorDialog, InfoDialog, QuestionDialog
from ubuntutweak.widgets.dialogs import ProcessDialog
from ubuntutweak.utils.parser import Parser
from ubuntutweak.network import utdata
from ubuntutweak.network.downloadmanager import DownloadDialog
from ubuntutweak.conf import GconfSetting
from ubuntutweak.common import consts
from ubuntutweak.common.config import TweakSettings
from ubuntutweak.common.utils import set_label_for_stock_button
from ubuntutweak.common.package import PACKAGE_WORKER, PackageInfo

APPCENTER_ROOT = os.path.join(consts.CONFIG_ROOT, 'appcenter')
APP_VERSION_URL = utdata.get_version_url('/appcenter_version/')
UPDATE_SETTING = GconfSetting(key='/apps/ubuntu-tweak/appcenter_update', type=bool)
VERSION_SETTING = GconfSetting(key='/apps/ubuntu-tweak/appcenter_version', type=str)

def get_app_data_url():
    return utdata.get_download_url('/static/utdata/appcenter-%s.tar.gz' %
                                   VERSION_SETTING.get_value())

if not os.path.exists(APPCENTER_ROOT):
    os.mkdir(APPCENTER_ROOT)

class StatusProvider(object):
    def __init__(self, name):
        self.__path = os.path.join(consts.CONFIG_ROOT, name)
        self.__init = False

        try:
            self.__data = json.loads(open(self.__path).read())
        except:
            self.__data = {'apps': {}, 'cates': {}}
            self.__init = True

    def set_init(self, active):
        self.__init = active

    def get_init(self):
        return self.__init

    def get_data(self):
        return self.__data

    def save(self):
        file = open(self.__path, 'w')
        file.write(json.dumps(self.__data))
        file.close()

    def load_objects_from_parser(self, parser):
        for key in parser.keys():
            #FIXME because of source id
            if self.get_init():
                self.__data['apps'][key] = {}
                self.__data['apps'][key]['read'] = True
                self.__data['apps'][key]['cate'] = parser.get_category(key)
            else:
                if key not in self.__data['apps']:
                    self.__data['apps'][key] = {}
                    self.__data['apps'][key]['read'] = False
                    self.__data['apps'][key]['cate'] = parser.get_category(key)

        self.set_init(False)
        self.save()

    def count_unread(self, cate):
        i = 0
        for key in self.__data['apps']:
            if self.__data['apps'][key]['cate'] == cate and not self.__data['apps'][key]['read']:
                i += 1
        return i

    def load_category_from_parser(self, parser):
        for cate in parser.keys():
            id = parser.get_id(cate)
            if self.__init:
                self.__data['cates'][id] = 0
            else:
                self.__data['cates'][id] = self.count_unread(id)

        self.__init = False
        self.save()

    def get_cate_unread_count(self, id):
        try:
            return self.__data['cates'].pop(id)
        except:
            return 0

    def get_read_status(self, key):
        try:
            return self.__data['apps'][key]['read']
        except:
            return True

    def set_as_read(self, key):
        try:
            self.__data['apps'][key]['read'] = True
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

class CateParser(Parser):
    #TODO Maybe move to the common code pakcage
    def __init__(self, path):
        Parser.__init__(self, path, 'slug')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

    def get_id(self, key):
        return self[key]['id']

class CategoryView(gtk.TreeView):
    (
        CATE_ID,
        CATE_NAME,
        CATE_DISPLAY,
    ) = range(3)

    def __init__(self, path):
        gtk.TreeView.__init__(self)

        self.path = path
        self.__status = None
        self.parser = None
        self.set_headers_visible(False)
        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gobject.TYPE_INT,
                    gobject.TYPE_STRING,
                    gobject.TYPE_STRING)
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Category'))

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.CATE_NAME)
        column.set_attributes(renderer, markup=self.CATE_DISPLAY)
        self.append_column(column)

    def set_status_from_view(self, view):
        self.__status = view.get_status()

    def update_model(self):
        self.model.clear()
        self.parser = CateParser(self.path)

        iter = self.model.append()
        self.model.set(iter, 
                self.CATE_ID, 0,
                self.CATE_NAME, 'all-category',
                self.CATE_DISPLAY, _('All Categories'))

        for slug in self.get_cate_items():
            iter = self.model.append()
            id = self.parser.get_id(slug)
            name = self.parser.get_name(slug)
            display = name

            if self.__status:
                self.__status.load_category_from_parser(self.parser)
                count = self.__status.get_cate_unread_count(id)
                if count:
                    display = '<b>%s (%d)</b>' % (name, count)

            self.model.set(iter, 
                           self.CATE_ID, id,
                           self.CATE_NAME, name,
                           self.CATE_DISPLAY, display)

    def get_cate_items(self):
        keys = self.parser.keys()
        keys.sort()
        return keys

class AppView(gtk.TreeView):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_INT,))
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
        gtk.TreeView.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.filter = None
        self.__status = None

        model = self.__create_model()
        self.__add_columns()
        self.set_model(model)

        self.set_rules_hint(True)
        self.set_search_column(self.COLUMN_NAME)

        self.show_all()

    def __create_model(self):
        model = gtk.ListStore(
                        gobject.TYPE_BOOLEAN,
                        gtk.gdk.Pixbuf,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING)

        return model

    def sort_model(self):
        model = self.get_model()
        model.set_sort_column_id(self.COLUMN_NAME, gtk.SORT_ASCENDING)

    def __add_columns(self):
        renderer = gtk.CellRendererToggle()
        renderer.set_property("xpad", 6)
        renderer.connect('toggled', self.on_install_toggled)

        column = gtk.TreeViewColumn('', renderer, active=self.COLUMN_INSTALLED)
        column.set_cell_data_func(renderer, self.install_column_view_func)
        column.set_sort_column_id(self.COLUMN_INSTALLED)
        self.append_column(column)

        column = gtk.TreeViewColumn('Applications')
        column.set_sort_column_id(self.COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, self.icon_column_view_func)
        column.set_attributes(renderer, pixbuf=self.COLUMN_ICON)

        renderer = gtk.CellRendererText()
        renderer.set_property("xpad", 6)
        renderer.set_property("ypad", 6)
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'markup', self.COLUMN_DISPLAY)
        self.append_column(column)

    def set_as_read(self, iter, model):
        package = model.get_value(iter, self.COLUMN_PKG)
        if self.__status and not self.__status.get_read_status(package):
            appname = model.get_value(iter, self.COLUMN_NAME)
            desc = model.get_value(iter, self.COLUMN_DESC)
            self.__status.set_as_read(package)
            model.set_value(iter, self.COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))

    def install_column_view_func(self, cell_layout, renderer, model, iter):
        package = model.get_value(iter, self.COLUMN_PKG)
        if package == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def icon_column_view_func(self, cell_layout, renderer, model, iter):
        pixbuf = model.get_value(iter, self.COLUMN_ICON)
        if pixbuf == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def clear_model(self):
        self.get_model().clear()

    def append_update(self, status, pkgname, summary):
        model = self.get_model()

        icontheme = gtk.icon_theme_get_default()
        for icon_name in ['application-x-deb', 'package-x-generic', 'package']:
            icon_theme = icontheme.lookup_icon(icon_name,
                                               size=32,
                                               flags=gtk.ICON_LOOKUP_NO_SVG)
            if icon_theme:
                break

        if icon_theme:
            pixbuf = icon_theme.load_icon()
        else:
            pixbuf = icontheme.load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

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
            self.__status = StatusProvider('appstatus.json')

    def get_status(self):
        return self.__status

    def update_model(self, apps=None):
        '''apps is a list to iter pkgname,
        '''
        model = self.get_model()
        model.clear()

        app_parser = AppParser()

        if self.__status:
            self.__status.load_objects_from_parser(app_parser)

        if not apps:
            apps = app_parser.keys()

        for pkgname in apps:
            category = app_parser.get_category(pkgname)
            pixbuf = self.get_app_logo(app_parser[pkgname]['logo'])

            try:
                package = PackageInfo(pkgname)
                is_installed = package.check_installed()
                appname = package.get_name()
                desc = app_parser.get_summary(pkgname)
            except:
                # Confirm the invalid package isn't in the count
                # But in the future, Ubuntu Tweak should display the invalid package too
                if self.__status and not self.__status.get_read_status(pkgname):
                    self.__status.set_as_read(pkgname)
                continue

            if self.filter == None or self.filter == category:
                iter = model.append()
                if pkgname in self.to_add or pkgname in self.to_rm:
                    status = not is_installed
                    display = self.__fill_changed_display(appname, desc)
                else:
                    status = is_installed
                    if self.__status and not self.__status.get_read_status(pkgname):
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
                          self.COLUMN_CATE, category,
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

    def set_filter(self, filter):
        self.filter = filter

    def get_app_logo(self, file_name):
        path = os.path.join(APPCENTER_ROOT, file_name)
        if not os.path.exists(path) or file_name == '':
            path = os.path.join(consts.DATA_DIR, 'pixmaps/common-logo.png')

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            if pixbuf.get_width() != 32 or pixbuf.get_height() != 32:
                pixbuf = pixbuf.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
            return pixbuf
        except:
            return gtk.icon_theme_get_default().load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

class CheckUpdateDialog(ProcessDialog):

    def __init__(self, parent, url):
        self.status = None
        self.done = False
        self.error = None
        self.user_action = False
        self.url = url

        super(CheckUpdateDialog, self).__init__(parent=parent)
        self.set_dialog_lable(_('Checking update...'))

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

class AppCenter(TweakModule):
    __title__ = _('Application Center')
    __desc__ = _('A simple but more efficient way for finding and installing popular applications.\n'
                 'Data will be automatically synchronized with the remote server.\n'
                 'You can click the "Sync" button to perform a manual check for updates.')
    __icon__ = 'gnome-app-install'
    __url__ = 'http://ubuntu-tweak.com/app/'
    __urltitle__ = _('Visit Online Application Center')
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'appcenter.ui')

        set_label_for_stock_button(self.sync_button, _('_Sync'))

        self.to_add = []
        self.to_rm = []

        self.package_worker = PACKAGE_WORKER
        self.url = APP_VERSION_URL

        self.appview = AppView()
        self.appview.set_status_active(TweakSettings.get_enable_new_item())
        self.appview.update_model()
        self.appview.sort_model()
        self.appview.connect('changed', self.on_app_status_changed)
        self.app_selection = self.appview.get_selection()
        self.app_selection.connect('changed', self.on_app_selection)
        self.right_sw.add(self.appview)

        self.cateview = CategoryView(os.path.join(APPCENTER_ROOT, 'cates.json'))
        self.cateview.set_status_from_view(self.appview)
        self.cateview.update_model()
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_category_changed)
        self.left_sw.add(self.cateview)

        self.update_timestamp()
        self.show_all()

        UPDATE_SETTING.set_value(False)
        UPDATE_SETTING.connect_notify(self.on_have_update, data=None)

        if TweakSettings.get_sync_notify():
            thread.start_new_thread(self.check_update, ())
        gobject.timeout_add(60000, self.update_timestamp)

        self.reparent(self.main_vbox)

    def update_timestamp(self):
        self.time_label.set_text(_('Last synced:') + ' ' + utdata.get_last_synced(APPCENTER_ROOT))
        return True

    def on_have_update(self, client, id, entry, data):
        if entry.get_value().get_bool():
            dialog = QuestionDialog(_('New application data available, would you like to update?'))
            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_YES:
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
            print error

    def on_app_selection(self, widget, data=None):
        model, iter = widget.get_selected()
        if iter:
            appview = widget.get_tree_view()
            appview.set_as_read(iter, model)
            self.cateview.update_model()

    def on_category_changed(self, widget, data=None):
        model, iter = widget.get_selected()
        cateview = widget.get_tree_view()

        if iter:
            if model.get_path(iter)[0] != 0:
                self.appview.set_filter(model.get_value(iter, cateview.CATE_ID))
            else:
                self.appview.set_filter(None)

            self.appview.clear_model()
            self.appview.update_model()

    def deep_update(self):
        self.package_worker.update_apt_cache(True)
        self.update_app_data()

    def on_apply_button_clicked(self, widget, data = None):
        to_rm = self.appview.to_rm
        to_add = self.appview.to_add
        self.package_worker.perform_action(widget.get_toplevel(), to_add, to_rm)

        self.package_worker.update_apt_cache(True)

        done = self.package_worker.get_install_status(to_add, to_rm)

        if done:
            self.apply_button.set_sensitive(False)
            InfoDialog(_('Update Successful!')).launch()
        else:
            ErrorDialog(_('Update Failed!')).launch()

        self.emit('call', 'ubuntutweak.modules.updatemanager', 'normal_update', {})

        self.appview.to_add = []
        self.appview.to_rm = []
        self.appview.clear_model()
        self.appview.update_model()

    def on_sync_button_clicked(self, widget):
        dialog = CheckUpdateDialog(widget.get_toplevel(), self.url)
        dialog.run()
        dialog.destroy()
        if dialog.status == True:
            dialog = QuestionDialog(_("Update available, would you like to update?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                dialog = FetchingDialog(get_app_data_url(), self.get_toplevel())
                dialog.connect('destroy', self.on_app_data_downloaded)
                dialog.run()
                dialog.destroy()
        elif dialog.error == True:
            ErrorDialog(_("Network Error, please check your network connection - or the remote server may be down.")).launch()
        else:
            InfoDialog(_("No update available.")).launch()

    def on_app_data_downloaded(self, widget):
        file = widget.get_downloaded_file()
        #FIXME
        if widget.downloaded:
            os.system('tar zxf %s -C %s' % (file, consts.CONFIG_ROOT))
            self.update_app_data()
            utdata.save_synced_timestamp(APPCENTER_ROOT)
            self.update_timestamp()
        elif widget.error:
            ErrorDialog(_('An error occurred while downloading the file.')).launch()

    def update_app_data(self):
        self.appview.update_model()
        self.cateview.update_model()

    def on_app_status_changed(self, widget, i):
        if i:
            self.apply_button.set_sensitive(True)
        else:
            self.apply_button.set_sensitive(False)
