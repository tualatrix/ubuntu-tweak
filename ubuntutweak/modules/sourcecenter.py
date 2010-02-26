#!/usr/bin/python
# coding: utf-8

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
import thread
import subprocess
import pango
import gobject
import apt_pkg
import webbrowser
import urllib
from gettext import ngettext
from aptsources.sourceslist import SourcesList

from ubuntutweak.modules  import TweakModule
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.widgets import GconfCheckButton
from ubuntutweak.widgets.dialogs import QuestionDialog, ErrorDialog, InfoDialog, WarningDialog
from ubuntutweak.utils.parser import Parser
from ubuntutweak.network import utdata
from appcenter import AppView, CategoryView, AppParser, AppStatus
from appcenter import CheckUpdateDialog, FetchingDialog
from ubuntutweak.conf import GconfSetting
from ubuntutweak.common import consts
from ubuntutweak.common.config import Config, TweakSettings
from ubuntutweak.common.utils import set_label_for_stock_button
from ubuntutweak.common.package import PACKAGE_WORKER, PackageInfo
from ubuntutweak.common.notify import notify
from ubuntutweak.common.misc import URLLister
from ubuntutweak.common.systeminfo import module_check

APP_PARSER = AppParser()
CONFIG = Config()
PPA_MIRROR = []
UNCONVERT = False
LAUNCHPAD_STR = 'ppa.launchpad.net'
WARNING_KEY = '/apps/ubuntu-tweak/disable_thidparty_warning'
UBUNTU_CN_STR = 'archive.ubuntu.org.cn/ubuntu-cn'
UBUNTU_CN_URL = 'http://archive.ubuntu.org.cn/ubuntu-cn/'
#UBUNTU_CN_URL = 'http://127.0.0.1:8000'
UPDATE_SETTING = GconfSetting(key='/apps/ubuntu-tweak/sourcecenter_update', type=bool)
VERSION_SETTING = GconfSetting(key='/apps/ubuntu-tweak/sourcecenter_version', type=str)

SOURCE_ROOT = os.path.join(consts.CONFIG_ROOT, 'sourcecenter')
SOURCE_VERSION_URL = utdata.get_version_url('/sourcecenter_version/')

def get_source_data_url():
    return utdata.get_download_url('/static/utdata/sourcecenter-%s.tar.gz' %
                                   VERSION_SETTING.get_value())

def refresh_source(parent):
    dialog = UpdateCacheDialog(parent)
    dialog.run()

    new_pkg = []
    for pkg in PACKAGE_WORKER.get_new_package():
        if pkg in APP_PARSER:
            new_pkg.append(pkg)

    new_updates = list(PACKAGE_WORKER.get_update_package())

    if new_pkg or new_updates:
        updateview = UpdateView()

        if new_pkg:
            updateview.update_model(new_pkg)

        if new_updates:
            updateview.update_updates(new_updates)

        dialog = QuestionDialog(_('You can install the new applications by selecting them and choose "Yes".\nOr you can install them at Add/Remove by choose "No".'),
                title=_('New applications are available to update'))

        vbox = dialog.vbox
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(-1, 200)
        vbox.pack_start(sw, False, False, 0)
        sw.add(updateview)

        select_button = gtk.CheckButton(_('Select All'))
        select_button.connect('clicked', on_select_button_clicked, updateview)
        vbox.pack_start(select_button, False, False, 0)
        vbox.show_all()

        res = dialog.run()
        dialog.destroy()

        to_rm = updateview.to_rm
        to_add = updateview.to_add

        if res == gtk.RESPONSE_YES and to_add:
            PACKAGE_WORKER.perform_action(parent, to_add, to_rm)

            PACKAGE_WORKER.update_apt_cache(True)

            done = PACKAGE_WORKER.get_install_status(to_add, to_rm)

            if done:
                InfoDialog(_('Update Successful!')).launch()
            else:
                ErrorDialog(_('Update Failed!')).launch()

        return True
    else:
        dialog = InfoDialog(_("Your system is clean and there's no update yet."),
                        title=_('The software information is up-to-date now'))

        dialog.launch()
        return False

def on_select_button_clicked(widget, updateview):
    updateview.select_all_action(widget.get_active())

class CheckSourceDialog(CheckUpdateDialog):
    def get_updatable(self):
        return utdata.check_update_function(self.url, SOURCE_ROOT, \
                                            UPDATE_SETTING, VERSION_SETTING, \
                                            auto=False)

class DistroParser(Parser):
    def __init__(self):
        super(DistroParser, self).__init__(os.path.join(SOURCE_ROOT, 'distros.json'), 'id')

    def get_codename(self, key):
        return self[key]['codename']

class SourceParser(Parser):
    def __init__(self):
        super(SourceParser, self).__init__(os.path.join(SOURCE_ROOT, 'sources.json'), 'id')

    def init_items(self, key):
        self.reverse_depends = {}

        distro_parser = DistroParser()

        for item in self.get_data():
            if item['fields'].has_key('distros'):
                distros = item['fields']['distros']
                distro_values = ''

                if len(distros) > 1:
                    # If the item in distros is more than 1, so it's a PPA.
                    # Try to parse its real codename, when match the local
                    # Get it, or continue
                    for id in distros:
                        if module_check.get_codename() == distro_parser.get_codename(id):
                            distro_values = distro_parser.get_codename(id)
                            break

                    if distro_values == '':
                        continue
                elif len(distros) == 1:
                    distro_values = distro_parser.get_codename(distros[0])
            else:
                #TODO Remove in the future release, only leave distros
                distro_values = item['fields']['distro']

            if module_check.is_ubuntu(distro_values) and \
                    module_check.get_codename() not in distro_values:
                continue

            item['fields']['id'] = item['pk']
            # But here, always be distro, the only distro correspond with current
            item['fields']['distro'] = distro_values
            self[item['fields'][key]] = item['fields']

            id = item['pk']
            fields = item['fields']

            if fields.has_key('dependencies') and fields['dependencies']:
                for depend_id in fields['dependencies']:
                    if self.reverse_depends.has_key(depend_id):
                        self.reverse_depends[depend_id].append(id)
                    else:
                        self.reverse_depends[depend_id] = [id]

    def has_reverse_depends(self, id):
        if id in self.reverse_depends.keys():
            return True
        else:
            return False

    def get_reverse_depends(self, id):
        return self.reverse_depends[id]

    def get_slug(self, key):
        return self[key]['slug']

    def get_conflicts(self, key):
        if self[key].has_key('conflicts'):
            return self[key]['conflicts']
        else:
            return None

    def get_dependencies(self, key):
        if self[key].has_key('dependencies'):
            return self[key]['dependencies']
        else:
            return None

    def get_summary(self, key):
        return self.get_by_lang(key, 'summary')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

    def get_category(self, key):
        return self[key]['category']

    def get_url(self, key):
        return self[key]['url']

    def get_key(self, key):
        return self[key]['key']

    def get_distro(self, key):
        return self[key]['distro']

    def get_comps(self, key):
        return self[key]['component']

    def get_website(self, key):
        return self[key]['website']

SOURCE_PARSER = SourceParser()

class UpdateView(AppView):
    def __init__(self):
        AppView.__init__(self)

        self.set_headers_visible(False)

    def update_model(self, apps):
        model = self.get_model()

        length = len(apps)
        model.append((None,
                      None,
                      None,
                      None,
                      None,
                      '<span size="large" weight="bold">%s</span>' %
                      ngettext('Available %d New Application',
                               'Available %d New Applications',
                               length) % length,
                      None,
                      None))

        super(UpdateView, self).update_model(apps)

    def update_updates(self, pkgs):
        '''apps is a list to iter pkgname,
        cates is a dict to find what the category the pkg is
        '''
        model = self.get_model()
        length = len(pkgs)

        if pkgs:
            iter = model.append()
            model.set(iter,
                      self.COLUMN_DISPLAY,
                      '<span size="large" weight="bold">%s</span>' %
                      ngettext('Available %d Package Update',
                               'Available %d Package Updates',
                               length) % length)

            apps = []
            updates = []
            for pkg in pkgs:
                if pkg in APP_PARSER:
                    apps.append(pkg)
                else:
                    updates.append(pkg)

            for pkgname in apps:
                pixbuf = self.get_app_logo(APP_PARSER[pkgname]['logo'])

                package = PackageInfo(pkgname)
                appname = package.get_name()
                desc = APP_PARSER.get_summary(pkgname)

                iter = model.append()
                model.set(iter,
                          self.COLUMN_INSTALLED, False,
                          self.COLUMN_ICON, pixbuf,
                          self.COLUMN_PKG, pkgname,
                          self.COLUMN_NAME, appname,
                          self.COLUMN_DESC, desc,
                          self.COLUMN_DISPLAY, '<b>%s</b>\n%s' % (appname, desc),
                          self.COLUMN_TYPE, 'update')

            for pkgname in updates:
                package = PACKAGE_WORKER.get_cache()[pkgname]

                self.append_update(False, package.name, package.summary)
        else:
            iter = model.append()
            model.set(iter,
                      self.COLUMN_DISPLAY,
                        '<span size="large" weight="bold">%s</span>' %
                        _('No Available Package Update'))

    def select_all_action(self, active):
        self.to_rm = []
        self.to_add = []
        model = self.get_model()
        model.foreach(self.__select_foreach, active)
        self.emit('changed', len(self.to_add))

    def __select_foreach(self, model, path, iter, check):
        model.set(iter, self.COLUMN_INSTALLED, check)
        pkg = model.get_value(iter, self.COLUMN_PKG)
        if pkg and check:
            self.to_add.append(pkg)

class UpdateCacheDialog:
    """This class is modified from Software-Properties"""
    def __init__(self, parent):
        self.parent = parent

    def update_cache(self, window_id, lock):
        """start synaptic to update the package cache"""
        try:
            apt_pkg.PkgSystemUnLock()
        except SystemError:
            pass
        cmd = []
        if os.getuid() != 0:
            cmd = ['/usr/bin/gksu',
                   '--desktop', '/usr/share/applications/synaptic.desktop',
                   '--']
        
        cmd += ['/usr/sbin/synaptic', '--hide-main-window',
               '--non-interactive',
               '--parent-window-id', '%s' % (window_id),
               '--update-at-startup']
        subprocess.call(cmd)
        lock.release()

    def run(self):
        """run the dialog, and if reload was pressed run synaptic"""
        self.parent.set_sensitive(False)
        self.parent.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        lock = thread.allocate_lock()
        lock.acquire()
        thread.start_new_thread(self.update_cache,
                               (self.parent.window.xid, lock))
        while lock.locked():
            while gtk.events_pending():
                gtk.main_iteration()
                time.sleep(0.05)
        self.parent.set_sensitive(True)
        self.parent.window.set_cursor(None)

class SourcesView(gtk.TreeView):
    __gsignals__ = {
        'sourcechanged': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }
    (COLUMN_ENABLED,
     COLUMN_ID,
     COLUMN_CATE,
     COLUMN_URL,
     COLUMN_DISTRO,
     COLUMN_COMPS,
     COLUMN_SLUG,
     COLUMN_LOGO,
     COLUMN_NAME,
     COLUMN_COMMENT,
     COLUMN_DISPLAY,
     COLUMN_HOME,
     COLUMN_KEY,
    ) = range(13)

    def __init__(self, status=None):
        gtk.TreeView.__init__(self)

        self.filter = None
        self.modelfilter = None
        self.status = status

        self.model = self.__create_model()
        self.model.set_sort_column_id(self.COLUMN_NAME, gtk.SORT_ASCENDING)
        self.set_model(self.model)

        self.modelfilter = self.model.filter_new()
        self.modelfilter.set_visible_func(self.on_visible_filter, None)
        self.set_search_column(self.COLUMN_NAME)

        self.__add_column()

        self.update_model()
        self.selection = self.get_selection()

    def get_sourceslist(self):
        return SourcesList()

    def __create_model(self):
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                gobject.TYPE_INT,
                gobject.TYPE_INT,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        return model

    def on_visible_filter(self, model, iter, data=None):
        category = self.model.get_value(iter, self.COLUMN_CATE)
        if self.filter == None or self.filter == category:
            return True
        else:
            return False

    def refilter(self):
        if self.filter:
            self.set_model(self.modelfilter)
        else:
            self.set_model(self.model)
        self.modelfilter.refilter()
        self.scroll_to_cell(0)

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_enable_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active=self.COLUMN_ENABLED)
        column.set_sort_column_id(self.COLUMN_ENABLED)
        self.append_column(column)

        column = gtk.TreeViewColumn(_('Third-Party Sources'))
        column.set_sort_column_id(self.COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=self.COLUMN_LOGO)

        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup=self.COLUMN_DISPLAY)

        self.append_column(column)

    def update_model(self):
        self.model.clear()
        sourceslist = self.get_sourceslist()

        if self.status:
            self.status.load_from_app(SOURCE_PARSER)

        for id in SOURCE_PARSER:
            enabled = False
            url = SOURCE_PARSER.get_url(id)
            slug = SOURCE_PARSER.get_slug(id)
            comps = SOURCE_PARSER.get_comps(id)
            distro = SOURCE_PARSER.get_distro(id)
            category = SOURCE_PARSER.get_category(id)

            name = SOURCE_PARSER.get_name(id)
            comment = SOURCE_PARSER.get_summary(id)
            pixbuf = self.get_source_logo(SOURCE_PARSER[id]['logo'])
            website = SOURCE_PARSER.get_website(id)
            key = SOURCE_PARSER.get_key(id)

            for source in sourceslist:
                if url in source.str() and source.type == 'deb':
                    enabled = not source.disabled

            if self.status and not self.status.get_app_readed(slug):
                self.status.set_app_readed(slug)
                display = '<b>%s <span foreground="#ff0000">(New!!!)</span>\n%s</b>' % (name, comment)
            else:
                display = '<b>%s</b>\n%s' % (name, comment)

            iter = self.model.append()
            self.model.set(iter,
                           self.COLUMN_ENABLED, enabled,
                           self.COLUMN_ID, id,
                           self.COLUMN_CATE, category,
                           self.COLUMN_URL, url,
                           self.COLUMN_DISTRO, distro,
                           self.COLUMN_COMPS, comps,
                           self.COLUMN_COMMENT, comment,
                           self.COLUMN_SLUG, slug,
                           self.COLUMN_NAME, name,
                           self.COLUMN_DISPLAY, display,
                           self.COLUMN_LOGO, pixbuf,
                           self.COLUMN_HOME, website,
                           self.COLUMN_KEY, key,
            )

    def get_source_logo(self, file_name):
        path = os.path.join(SOURCE_ROOT, file_name)
        if not os.path.exists(path) or file_name == '':
            path = os.path.join(consts.DATA_DIR, 'pixmaps/ppa-logo.png')

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
            if pixbuf.get_width() != 32 or pixbuf.get_height() != 32:
                pixbuf = pixbuf.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
            return pixbuf
        except:
            return gtk.icon_theme_get_default().load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

    def update_ubuntu_cn_model(self):
        global SOURCES_DATA
        SOURCES_DATA = self.__filter_source_to_mirror()
        self.update_model()

    def unconver_ubuntu_cn_mirror(self):
        global UNCONVERT
        sourceslist = self.get_sourceslist()

        for source in sourceslist:
            if UBUNTU_CN_STR in source.str():
                UNCONVERT = True
                break

    def setup_ubuntu_cn_mirror(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        if UNCONVERT:
            import ubuntutweak.common.sourcedata
            reload(ubuntutweak.common.sourcedata)
            global SOURCES_DATA
            from ubuntutweak.common.sourcedata import SOURCES_DATA
            proxy.replace_entry(UBUNTU_CN_STR, LAUNCHPAD_STR)
            self.update_model()
            self.emit('sourcechanged')
        else:
            iter = self.model.get_iter_first()
            while iter:
                while gtk.events_pending():
                    gtk.main_iteration()

                url  = self.model.get_value(iter, self.COLUMN_URL)

                if self.has_mirror_ppa(url):
                    new_url = url.replace(LAUNCHPAD_STR, UBUNTU_CN_STR)
                    proxy.replace_entry(url, new_url)
                    self.model.set_value(iter, self.COLUMN_URL, new_url)

                iter = self.model.iter_next(iter)

            self.emit('sourcechanged')
            self.update_ubuntu_cn_model()

        if window:
            window.set_cursor(None)

    def __filter_source_to_mirror(self):
        newsource = []
        for item in SOURCES_DATA:
            url = item[0]
            if self.has_mirror_ppa(url):
                url = url.replace(LAUNCHPAD_STR, UBUNTU_CN_STR)
                newsource.append([url, item[1], item[2], item[3]])
            else:
                newsource.append(item)

        return newsource

    def has_mirror_ppa(self, url):
        if TweakSettings.get_use_mirror_ppa():
            return LAUNCHPAD_STR in url and url.split('/')[3] in PPA_MIRROR
        else:
            return False

    def is_mirror_ppa(self, url):
        return UBUNTU_CN_STR in url

    def get_sourcelist_status(self, url):
        for source in self.get_sourceslist():
            if url in source.str() and source.type == 'deb':
                return not source.disabled
        return False

    def on_enable_toggled(self, cell, path):
        model = self.get_model()
        iter = model.get_iter((int(path),))

        id = model.get_value(iter, self.COLUMN_ID)
        name = model.get_value(iter, self.COLUMN_NAME)
        enabled = model.get_value(iter, self.COLUMN_ENABLED)

        conflicts = SOURCE_PARSER.get_conflicts(id)
        dependencies = SOURCE_PARSER.get_dependencies(id)

        #Convert to real model, because will involke the set method
        if type(model) == gtk.TreeModelFilter:
            iter = model.convert_iter_to_child_iter(iter)
            model = model.get_model()

        if not enabled and conflicts:
            conflict_list = []
            conflict_name_list = []
            for conflict_id in conflicts:
                if self.get_source_enabled(conflict_id):
                    conflict_list.append(conflict_id)
                    name_list = [r[self.COLUMN_NAME] for r in model if r[self.COLUMN_ID] == conflict_id]
                    if name_list:
                            conflict_name_list.extend(name_list)

            if conflict_list and conflict_name_list:
                full_name = ', '.join(conflict_name_list)
                ErrorDialog(_('You can\'t enable this Source because'
                              '<b>"%(SOURCE)s"</b> conflicts with it.\nTo '
                              'continue you need to disable <b>"%(SOURCE)s"</b>' \
                              'first.') % {'SOURCE': full_name}).launch()

                model.set(iter, self.COLUMN_ENABLED, enabled)
                return

        if enabled is False and dependencies:
            depend_list = []
            depend_name_list = []
            for depend_id in dependencies:
                if self.get_source_enabled(depend_id) is False:
                    depend_list.append(depend_id)
                    name_list = [r[self.COLUMN_NAME] for r in model if r[self.COLUMN_ID] == depend_id]
                    if name_list:
                            depend_name_list.extend(name_list)

            if depend_list and depend_name_list:
                full_name = ', '.join(depend_name_list)

                dialog = QuestionDialog(\
                            _('To enable this Source, You need to enable <b>"%s"</b> at first.\nDo you wish to continue?') \
                            % full_name,
                            title=_('Dependency Notice'))
                if dialog.run() == gtk.RESPONSE_YES:
                    for depend_id in depend_list:
                        self.set_source_enabled(depend_id)
                    self.set_source_enabled(id)
                else:
                    model.set(iter, self.COLUMN_ENABLED, enabled)

                dialog.destroy()
                return

        if enabled and SOURCE_PARSER.has_reverse_depends(id):
            depend_list = []
            depend_name_list = []
            for depend_id in SOURCE_PARSER.get_reverse_depends(id):
                if self.get_source_enabled(depend_id):
                    depend_list.append(depend_id)
                    name_list = [r[self.COLUMN_NAME] for r in model if r[self.COLUMN_ID] == depend_id]
                    if name_list:
                            depend_name_list.extend(name_list)

            if depend_list and depend_name_list:
                full_name = ', '.join(depend_name_list)

                ErrorDialog(_('You can\'t disable this Source because '
                            '<b>"%(SOURCE)s"</b> depends on it.\nTo continue '
                            'you need to disable <b>"%(SOURCE)s"</b> first.') \
                                 % {'SOURCE': full_name}).launch()

                model.set(iter, self.COLUMN_ENABLED, enabled)
                return

        self.do_source_enable(iter, not enabled)

    def on_source_foreach(self, model, path, iter, id):
        m_id = model.get_value(iter, self.COLUMN_ID)
        if m_id == id:
            if self._foreach_mode == 'get':
                self._foreach_take = model.get_value(iter, self.COLUMN_ENABLED)
            elif self._foreach_mode == 'set':
                self._foreach_take = iter

    def on_source_name_foreach(self, model, path, iter, id):
        m_id = model.get_value(iter, self.COLUMN_ID)
        if m_id == id:
            self._foreach_name_take = model.get_value(iter, self.COLUMN_NAME)

    def get_source_enabled(self, id):
        '''
        Search source by id, then get status from model
        '''
        self._foreach_mode = 'get'
        self._foreach_take = None
        self.model.foreach(self.on_source_foreach, id)
        return self._foreach_take

    def set_source_enabled(self, id):
        '''
        Search source by id, then call do_source_enable
        '''
        self._foreach_mode = 'set'
        self._foreach_status = None
        self.model.foreach(self.on_source_foreach, id)
        self.do_source_enable(self._foreach_take, True)

    def set_source_disable(self, id):
        '''
        Search source by id, then call do_source_enable
        '''
        self._foreach_mode = 'set'
        self._foreach_status = None
        self.model.foreach(self.on_source_foreach, id)
        self.do_source_enable(self._foreach_take, False)

    def do_source_enable(self, iter, enable):
        '''
        Do the really source enable or disable action by iter
        Only emmit signal when source is changed
        '''
        model = self.modelfilter.get_model()

        url = model.get_value(iter, self.COLUMN_URL)
        icon = model.get_value(iter, self.COLUMN_LOGO)
        distro = model.get_value(iter, self.COLUMN_DISTRO)
        comment = model.get_value(iter, self.COLUMN_NAME)
        package = model.get_value(iter, self.COLUMN_SLUG)
        comps = model.get_value(iter, self.COLUMN_COMPS)
        key = model.get_value(iter, self.COLUMN_KEY)

        pre_status = self.get_sourcelist_status(url)

        if key:
            proxy.add_apt_key_from_content(key)

        if not comps and distro:
            distro = distro + '/'
        elif not comps and not distro:
            distro = './'

        if TweakSettings.get_separated_sources():
            result = proxy.set_separated_entry(url, distro, comps,
                                               comment, enable, package)
        else:
            result = proxy.set_entry(url, distro, comps, comment, enable)

        if str(result) == 'enabled':
            model.set(iter, self.COLUMN_ENABLED, True)
        else:
            model.set(iter, self.COLUMN_ENABLED, False)

        if pre_status != enable:
            self.emit('sourcechanged')

        if enable:
            notify.update(_('New source has been enabled'),
                          _('%s is enabled now, Please click the refresh button to update the application cache.') % comment)
            notify.set_icon_from_pixbuf(icon)
            notify.show()

class SourceDetail(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        self.table = gtk.Table(2, 2)
        self.pack_start(self.table)

        gtk.link_button_set_uri_hook(self.click_website)

        items = [_('Homepage'), _('Source URL'), _('Description')]
        for i, text in enumerate(items):
            label = gtk.Label()
            label.set_markup('<b>%s</b>' % text)

            self.table.attach(label, 0, 1,
                              i, i + 1,
                              xoptions=gtk.FILL, xpadding=10, ypadding=5)

        self.homepage_button = gtk.LinkButton('http://ubuntu-tweak.com')
        self.table.attach(self.homepage_button, 1, 2, 0, 1)
        self.url_button = gtk.LinkButton('http://ubuntu-tweak.com')
        self.table.attach(self.url_button, 1, 2, 1, 2)
        self.description = gtk.Label(_('Description is here'))
        self.description.set_line_wrap(True)
        self.table.attach(self.description, 1, 2, 2, 3)

    def click_website(self, widget, link):
        webbrowser.open(link)

    def set_details(self, homepage = None, url = None, description = None):
        if homepage:
            self.homepage_button.destroy()
            self.homepage_button = gtk.LinkButton(homepage, homepage)
            self.homepage_button.show()
            self.table.attach(self.homepage_button, 1, 2, 0, 1)

        if url:
            if LAUNCHPAD_STR in url:
                url_section = url.split('/')
                url = 'https://launchpad.net/~%s/+archive/%s' % (
                        url_section[3], url_section[4])
            self.url_button.destroy()
            self.url_button = gtk.LinkButton(url, url)
            self.url_button.show()
            self.table.attach(self.url_button, 1, 2, 1, 2)

        if description:
            self.description.set_text(description)

class SourceCenter(TweakModule):
    __title__  = _('Source Center')
    __desc__ = _('A source center to keep your applications always up-to-date.\n'
                 'You can also get the application which isn\'t in the official repository.\n'
                 'Data will be automatically synchronized with the remote side.\n'
                 'You can click the "Sync" button to check the update manually.')
    __icon__ = 'software-properties'
    __url__ = 'http://ubuntu-tweak.com/source/'
    __urltitle__ = _('Visit online Source Center')
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'sourcecenter.ui')

        self.url = SOURCE_VERSION_URL
        set_label_for_stock_button(self.sync_button, _('_Sync'))
        self.sourcestatus = AppStatus(name='sourcestatus.json')

        self.sourceview = SourcesView(self.sourcestatus)
        self.sourceview.connect('sourcechanged', self.on_source_changed)
        self.sourceview.selection.connect('changed', self.on_selection_changed)
        self.sourceview.set_sensitive(False)
        self.sourceview.set_rules_hint(True)
        self.right_sw.add(self.sourceview)

        self.cateview = CategoryView(os.path.join(SOURCE_ROOT, 'cates.json'),
                                     self.sourcestatus)
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_category_changed)
        self.left_sw.add(self.cateview)

        self.expander = gtk.Expander(_('Details'))
        self.vbox1.pack_start(self.expander, False, False, 0)
        self.sourcedetail = SourceDetail()
        self.expander.set_sensitive(False)
        self.expander.add(self.sourcedetail)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        self.hbox2.pack_end(un_lock, False, False, 0)
        self.hbox2.reorder_child(un_lock, 0)

        #TODO when server is ready, work on it again
#        try:
#            if os.getenv('LANG').startswith('zh_CN'):
#                if TweakSettings.get_use_mirror_ppa():
#                    gobject.idle_add(self.start_check_cn_ppa)
#                else:
#                    self.sourceview.unconver_ubuntu_cn_mirror()
#        except AttributeError:
#            pass

#        CONFIG.get_client().notify_add('/apps/ubuntu-tweak/use_mirror_ppa',
#                                       self.value_changed)

        self.update_timestamp()
        UPDATE_SETTING.set_value(False)
        UPDATE_SETTING.connect_notify(self.on_have_update, data=None)

        if TweakSettings.get_sync_notify():
            thread.start_new_thread(self.check_update, ())
        gobject.timeout_add(60000, self.update_timestamp)

        self.reparent(self.main_vbox)

    def update_timestamp(self):
        self.time_label.set_text(_('Last synced:') + ' ' + utdata.get_last_synced(SOURCE_ROOT))
        return True

    def on_have_update(self, client, id, entry, data):
        if entry.get_value().get_bool():
            if self.check_update():
                dialog = QuestionDialog(_('New sources data available, would you like to update?'))
                response = dialog.run()
                dialog.destroy()

                if response == gtk.RESPONSE_YES:
                    dialog = FetchingDialog(get_source_data_url(),
                                            self.get_toplevel())
                    dialog.connect('destroy', self.on_source_data_downloaded)
                    dialog.run()
                    dialog.destroy()

    def check_update(self):
        try:
            return utdata.check_update_function(self.url, SOURCE_ROOT, \
                                            UPDATE_SETTING, VERSION_SETTING, \
                                            auto=True)
        except Exception, error:
            print error

    def on_category_changed(self, widget, data = None):
        model, iter = widget.get_selected()
        cateview = widget.get_tree_view()

        if iter:
            if model.get_path(iter)[0] != 0:
                self.sourceview.filter = model.get_value(iter, cateview.CATE_ID)
            else:
                self.sourceview.filter = None

            self.sourceview.refilter()

    def value_changed(self, client, id, entry, data):
        global UNCONVERT
        UNCONVERT = not entry.value.get_bool()
        if len(PPA_MIRROR) == 0:
            self.start_check_cn_ppa()
        if globals().has_key('proxy'):
            self.sourceview.setup_ubuntu_cn_mirror()

    def start_check_cn_ppa(self):
        import socket
        socket.setdefaulttimeout(3)
        try:
            url = urllib.urlopen(UBUNTU_CN_URL)

            parse = URLLister(PPA_MIRROR)
            data = url.read()
            parse.feed(data)
        except:
            pass

    def update_thirdparty(self):
        self.sourceview.update_model()

    def on_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter is None:
            return
        home = model.get_value(iter, self.sourceview.COLUMN_HOME)
        url = model.get_value(iter, self.sourceview.COLUMN_URL)
        description = model.get_value(iter, self.sourceview.COLUMN_COMMENT)

        self.sourcedetail.set_details(home, url, description)

    def on_polkit_action(self, widget, action):
        if action:
            self.sync_button.set_sensitive(True)

            if proxy.get_proxy():
#                if os.getenv('LANG').startswith('zh_CN'):
#                    self.sourceview.setup_ubuntu_cn_mirror()
                self.sourceview.set_sensitive(True)
                self.expander.set_sensitive(True)

                if not CONFIG.get_value_from_key(WARNING_KEY):
                    dialog = WarningDialog(_('It is a possible security risk to '
                        'use packages from Third-Party Sources.\n'
                        'Please be careful and use only sources you trust.'),
                        buttons = gtk.BUTTONS_OK, title = _('Warning'))
                    checkbutton = GconfCheckButton(_('Never show this dialog'), WARNING_KEY)
                    dialog.add_option(checkbutton)

                    dialog.run()
                    dialog.destroy()
            else:
                ServerErrorDialog().launch()
        else:
            AuthenticateFailDialog().launch()

    def on_source_changed(self, widget):
        self.emit('call', 'ubuntutweak.modules.sourceeditor', 'update_source_combo', {})

    def on_update_button_clicked(self, widget):
        if refresh_source(widget.get_toplevel()):
            self.emit('call', 'ubuntutweak.modules.appcenter', 'update_app_data', {})
            self.emit('call', 'ubuntutweak.modules.updatemanager', 'update_list', {})

    def on_source_data_downloaded(self, widget):
        file = widget.get_downloaded_file()
        if widget.downloaded:
            os.system('tar zxf %s -C %s' % (file, consts.CONFIG_ROOT))
            self.update_source_data()
            utdata.save_synced_timestamp(SOURCE_ROOT)
            self.update_timestamp()
        elif widget.error:
            ErrorDialog(_('Some error happened while downloading the file')).launch()

    def update_source_data(self):
        global SOURCE_PARSER
        SOURCE_PARSER = SourceParser()

        self.sourceview.model.clear()
        self.cateview.update_model()
        self.sourceview.update_model()

    def on_sync_button_clicked(self, widget):
        dialog = CheckSourceDialog(widget.get_toplevel(), self.url)
        dialog.run()
        dialog.destroy()
        if dialog.status == True:
            dialog = QuestionDialog(_("Update available, Would you like to update?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                dialog = FetchingDialog(parent=self.get_toplevel(), url=get_source_data_url())
                dialog.connect('destroy', self.on_source_data_downloaded)
                dialog.run()
                dialog.destroy()
        elif dialog.error == True:
            ErrorDialog(_("Network Error, Please check your network connection or the remote server is down.")).launch()
        else:
            InfoDialog(_("No update available.")).launch()
