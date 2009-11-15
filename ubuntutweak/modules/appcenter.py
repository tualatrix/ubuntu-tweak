
# Ubuntu Tweak - PyGTK based desktop configure tool
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
import urllib
import urllib2
import gettext
import gobject
import pango

from ubuntutweak.conf import settings
from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets.dialogs import ErrorDialog, InfoDialog, QuestionDialog
from ubuntutweak.widgets.dialogs import ProcessDialog
from ubuntutweak.utils import icon
from ubuntutweak.utils.parser import Parser
from ubuntutweak.network.downloadmanager import DownloadDialog

#TODO old stuff
from ubuntutweak.common.consts import *
from ubuntutweak.common.package import package_worker, PackageInfo

(
    COLUMN_INSTALLED,
    COLUMN_ICON,
    COLUMN_PKG,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
    COLUMN_CATE,
    COLUMN_TYPE,
) = range(8)

(
    CATE_ID,
    CATE_ICON,
    CATE_NAME,
) = range(3)

APPCENTER_ROOT = os.path.join(settings.CONFIG_ROOT, 'appcenter')
APP_VERSION_URL = 'http://127.0.0.1:8000/app_version/'
APP_URL = 'http://127.0.0.1:8000/static/appcenter.tar.gz'

if not os.path.exists(APPCENTER_ROOT):
    os.mkdir(APPCENTER_ROOT)

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

class CategoryView(gtk.TreeView):
    def __init__(self, path):
        gtk.TreeView.__init__(self)

        self.parser = CateParser(path)

        self.set_headers_visible(False)
        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()
        self.update_model()

        selection = self.get_selection()
        selection.select_iter(self.model.get_iter_first())

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gobject.TYPE_INT,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING)
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Categories'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=CATE_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(CATE_NAME)
        column.set_attributes(renderer, text=CATE_NAME)

        self.append_column(column)

    def update_model(self):
        self.model.clear()

        iter = self.model.append()
        self.model.set(iter, 
                CATE_ID, 0,
                CATE_ICON, icon.get_with_file(os.path.join(DATA_DIR, 'appcates', 'all.png'), size=16),
                CATE_NAME, _('All Categories'))

        for item in self.get_cate_items():
            iter = self.model.append()
            id, name, pixbuf = self.parse_cate_item(item)
            self.model.set(iter, 
                    CATE_ID, id,
                    CATE_ICON, pixbuf,
                    CATE_NAME, name)

    def get_cate_items(self):
        for k in self.parser.keys():
            item = self.parser[k]
            item['name'] = self.parser.get_name(k)
            yield item

    def parse_cate_item(self, item):
        id = item['id']
        name = item['name']
        pixbuf = self.get_cate_logo(item['logo'])

        return id, name, pixbuf

    def get_cate_logo(self, file):
        path = os.path.join(APPCENTER_ROOT, file)
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            if pixbuf.get_width() != 16 or pixbuf.get_height() != 16:
                pixbuf = pixbuf.scale_simple(16, 16, gtk.gdk.INTERP_BILINEAR)
            return pixbuf
        except:
            return gtk.icon_theme_get_default().load_icon(gtk.STOCK_MISSING_IMAGE, 16, 0)

class AppView(gtk.TreeView):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,))
    }

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.to_add = []
        self.to_rm = []
        self.filter = None

        model = self.__create_model()
        self.__add_columns()
        self.set_model(model)

        self.set_rules_hint(True)
        self.set_search_column(COLUMN_NAME)

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
        model.set_sort_column_id(COLUMN_NAME, gtk.SORT_ASCENDING)

    def __add_columns(self):
        renderer = gtk.CellRendererToggle()
        renderer.set_property("xpad", 6)
        renderer.connect('toggled', self.on_install_toggled)

        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_INSTALLED)
        column.set_cell_data_func(renderer, self.install_column_view_func)
        column.set_sort_column_id(COLUMN_INSTALLED)
        self.append_column(column)

        column = gtk.TreeViewColumn('Applications')
        column.set_sort_column_id(COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, self.icon_column_view_func)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        renderer.set_property("xpad", 6)
        renderer.set_property("ypad", 6)
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'markup', COLUMN_DISPLAY)
        self.append_column(column)

    def install_column_view_func(self, cell_layout, renderer, model, iter):
        package = model.get_value(iter, COLUMN_PKG)
        if package == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def icon_column_view_func(self, cell_layout, renderer, model, iter):
        icon = model.get_value(iter, COLUMN_ICON)
        if icon == None:
            renderer.set_property("visible", False)
        else:
            renderer.set_property("visible", True)

    def clear_model(self):
        self.get_model().clear()

    def append_app(self, status, pixbuf, pkgname, appname, desc, category, type='app'):
        model = self.get_model()

        model.append((status,
                pixbuf,
                pkgname,
                appname,
                desc,
                '<b>%s</b>\n%s' % (appname, desc),
                category,
                type))

    def append_changed_app(self, status, pixbuf, pkgname, appname, desc, category):
        model = self.get_model()

        model.append((status,
                pixbuf,
                pkgname,
                appname,
                desc,
                '<span foreground="#ffcc00"><b>%s</b>\n%s</span>' % (appname, desc),
                category,
                'app'))

    def append_update(self, status, pkgname, summary):
        model = self.get_model()
        self.to_add.append(pkgname)

        icontheme = gtk.icon_theme_get_default()
        for icon_name in ['application-x-deb', 'package-x-generic', 'package']:
            icon = icontheme.lookup_icon(icon_name, 32, gtk.ICON_LOOKUP_NO_SVG)
            if icon:
                break

        if icon:
            pixbuf = icon.load_icon()
        else:
            pixbuf = icontheme.load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

        model.append((status,
                      pixbuf,
                      pkgname,
                      pkgname,
                      summary,
                      '<b>%s</b>\n%s' % (pkgname, summary),
                      None,
                      'update'))

    def update_model(self, apps=None):
        '''apps is a list to iter pkgname,
        '''
        def do_append(is_installed, pixbuf, pkgname, appname, desc, category):
            if pkgname in self.to_add or pkgname in self.to_rm:
                self.append_changed_app(not is_installed,
                        pixbuf,
                        pkgname,
                        appname,
                        desc,
                        category)
            else:
                self.append_app(is_installed,
                        pixbuf,
                        pkgname,
                        appname,
                        desc,
                        category)

        model = self.get_model()
        model.clear()

        icon = gtk.icon_theme_get_default()

        app_parser = AppParser()

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
            except KeyError:
                continue

            if self.filter == None:
                do_append(is_installed, pixbuf, pkgname, appname, desc, category)
            else:
                if self.filter == category:
                    do_append(is_installed, pixbuf, pkgname, appname, desc, category)

    def on_install_toggled(self, cell, path):
        def do_app_changed(model, iter, appname, desc):
                model.set(iter, COLUMN_DISPLAY, '<span style="italic" weight="bold"><b>%s</b>\n%s</span>' % (appname, desc))
        def do_app_unchanged(model, iter, appname, desc):
                model.set(iter, COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc))

        model = self.get_model()

        iter = model.get_iter((int(path),))
        is_installed = model.get_value(iter, COLUMN_INSTALLED)
        pkgname = model.get_value(iter, COLUMN_PKG)
        appname = model.get_value(iter, COLUMN_NAME)
        desc = model.get_value(iter, COLUMN_DESC)
        type = model.get_value(iter, COLUMN_TYPE)

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

            model.set(iter, COLUMN_INSTALLED, is_installed)
        else:
            to_installed = is_installed
            to_installed = not to_installed
            if to_installed == True:
                self.to_add.append(pkgname)
            else:
                self.to_add.remove(pkgname)

            model.set(iter, COLUMN_INSTALLED, to_installed)

        self.emit('changed', len(self.to_add) + len(self.to_rm))

    def set_filter(self, filter):
        self.filter = filter

    def get_app_logo(self, file):
        path = os.path.join(APPCENTER_ROOT, file)
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            if pixbuf.get_width() != 32 or pixbuf.get_height() != 32:
                pixbuf = pixbuf.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
            return pixbuf
        except:
            return gtk.icon_theme_get_default().load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

def check_update_function(version_url):
    local_timestamp = os.path.join(APPCENTER_ROOT, 'timestamp')

    remote_version = urllib.urlopen(version_url).read()
    if os.path.exists(local_timestamp):
        local_version = open(local_timestamp).read().split('.')[0].split('-')[-1]
    else:
        local_version = '0'

    if remote_version > local_version:
        return True
    else:
        return False

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
        return check_update_function(self.url)

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
    __desc__ = _('A simple but more effecient method for finding and installing popular packages than the default Add/Remove.')
    __icon__ = 'gnome-app-install'
    __url__ = 'http://ubuntu-tweak.com'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'appcenter.ui')

        self.to_add = []
        self.to_rm = []

        self.package_worker = package_worker

        self.cateview = CategoryView(os.path.join(APPCENTER_ROOT, 'cates.json'))
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_category_changed)
        self.left_sw.add(self.cateview)

        self.appview = AppView()
        self.appview.update_model()
        self.appview.sort_model()
        self.appview.connect('changed', self.on_app_status_changed)
        self.right_sw.add(self.appview)

        self.show_all()

        gobject.idle_add(self.on_idle_check)

    def reparent(self):
        self.main_vbox.reparent(self.inner_vbox)

    def on_idle_check(self):
        gtk.gdk.threads_enter()
        if self.check_update():
            dialog = QuestionDialog(_('New application data available, would you like to update?'))
            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_YES:
                dialog = FetchingDialog(APP_URL, self.get_toplevel())
                dialog.connect('destroy', self.on_app_data_downloaded)
                dialog.run()
                dialog.destroy()

        gtk.gdk.threads_leave()

    def check_update(self):
        try:
            return check_update_function(APP_VERSION_URL)
        except Exception, e:
            #TODO use logging
            print e

    def on_category_changed(self, widget, data = None):
        model, iter = widget.get_selected()

        if iter:
            if model.get_path(iter)[0] != 0:
                self.appview.set_filter(model.get_value(iter, CATE_ID))
            else:
                self.appview.set_filter(None)

            self.appview.clear_model()
            self.appview.update_model()

    def deep_update(self):
        package_worker.update_apt_cache(True)
        self.update_app_data()

    def normal_update(self):
        self.update_apt_cache()

    def on_apply_button_clicked(self, widget, data = None):
        to_rm = self.appview.to_rm
        to_add = self.appview.to_add
        self.package_worker.perform_action(widget.get_toplevel(), to_add, to_rm)

        package_worker.update_apt_cache(True)

        done = package_worker.get_install_status(to_add, to_rm)

        if done:
            self.apply_button.set_sensitive(False)
            InfoDialog(_('Update Successful!')).launch()
        else:
            ErrorDialog(_('Update Failed!')).launch()

        self.appview.to_add = []
        self.appview.to_rm = []
        self.appview.clear_model()
        self.appview.update_model()

    def on_refresh_button_clicked(self, widget):
        dialog = CheckUpdateDialog(widget.get_toplevel(), APP_VERSION_URL)
        dialog.run()
        dialog.destroy()
        if dialog.status == True:
            dialog = QuestionDialog(_("Update available, Do you want to update?"))
            dialog.run()
            dialog.destroy()

            dialog = FetchingDialog(APP_URL, self.get_toplevel())
            dialog.connect('destroy', self.on_app_data_downloaded)
            dialog.run()
            dialog.destroy()
        elif dialog.error == True:
            ErrorDialog(_("Network Error, Please check your network or the remote server going down")).launch()
        else:
            InfoDialog(_("No update available")).launch()

    def on_app_data_downloaded(self, widget):
        file = widget.get_downloaded_file()
        #FIXME
        if widget.downloaded:
            os.system('tar zxf %s -C %s' % (file, settings.CONFIG_ROOT))
            self.update_app_data()

    def update_app_data(self):
        self.cateview.update_model()
        self.appview.update_model()

    def on_app_status_changed(self, widget, i):
        if i:
            self.apply_button.set_sensitive(True)
        else:
            self.apply_button.set_sensitive(False)
