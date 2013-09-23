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
import re
import json
import time
import urllib
import thread
import apt_pkg
import logging
import gettext
import subprocess

from urllib2 import urlopen, Request, URLError
from gettext import ngettext
from aptsources.sourceslist import SourcesList

from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Notify

from ubuntutweak import system
from ubuntutweak.common import consts
from ubuntutweak.common.debug import log_func
from ubuntutweak.modules  import TweakModule
from ubuntutweak.policykit.dbusproxy import proxy
from ubuntutweak.gui.widgets import CheckButton
from ubuntutweak.gui.dialogs import QuestionDialog, ErrorDialog, InfoDialog, WarningDialog
from ubuntutweak.gui.gtk import post_ui, set_busy, unset_busy
from ubuntutweak.utils.parser import Parser
from ubuntutweak.network import utdata
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.utils import set_label_for_stock_button
from ubuntutweak.utils import ppa, icon
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.apps import CategoryView

from ubuntutweak.admins.appcenter import AppView, AppParser, StatusProvider
from ubuntutweak.admins.appcenter import CheckUpdateDialog, FetchingDialog, PackageInfo

log = logging.getLogger("SourceCenter")

APP_PARSER = AppParser()
PPA_MIRROR = []
UNCONVERT = False
WARNING_KEY = 'com.ubuntu-tweak.apps.disable-warning'
CONFIG = GSetting(key=WARNING_KEY)
UPDATE_SETTING = GSetting(key='com.ubuntu-tweak.apps.sources-can-update', type=bool)
VERSION_SETTING = GSetting(key='com.ubuntu-tweak.apps.sources-version', type=str)

SOURCE_ROOT = os.path.join(consts.CONFIG_ROOT, 'sourcecenter')
SOURCE_VERSION_URL = utdata.get_version_url('/sourcecenter_version/')
UPGRADE_DICT = {}

def get_source_data_url():
    return utdata.get_download_url('/media/utdata/sourcecenter-%s.tar.gz' %
                                   VERSION_SETTING.get_value())

def get_source_logo_from_filename(file_name):
    path = os.path.join(SOURCE_ROOT, file_name)
    if not os.path.exists(path) or file_name == '':
        path = os.path.join(consts.DATA_DIR, 'pixmaps/ppa-logo.png')

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        if pixbuf.get_width() != 32 or pixbuf.get_height() != 32:
            pixbuf = pixbuf.scale_simple(32, 32, GdkPixbuf.InterpType.BILINEAR)
        return pixbuf
    except:
        return Gtk.IconTheme.get_default().load_icon(Gtk.STOCK_MISSING_IMAGE, 32, 0)

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
            distro_values = ''

            if item['fields'].has_key('distros'):
                distros = item['fields']['distros']

                for id in distros:
                    codename = distro_parser.get_codename(id)
                    if codename in system.UBUNTU_CODENAMES:
                        if system.CODENAME == codename:
                            distro_values = codename
                            break
                    else:
                        distro_values = codename
                        break

                if distro_values == '':
                    continue

            item['fields']['id'] = item['pk']
            item['fields']['distro'] = distro_values
            self[item['fields'][key]] = item['fields']

            UPGRADE_DICT[item['fields']['url']] = distro_values

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

    def get_key_fingerprint(self, key):
        if self[key].has_key('key_fingerprint'):
            return self[key]['key_fingerprint']
        else:
            return ''

    def get_distro(self, key):
        return self[key]['distro']

    def get_comps(self, key):
        return self[key]['component']

    def get_website(self, key):
        return self[key]['website']

    def set_enable(self, key, enable):
        # To make other module use the source enable feature, move the logical to here
        # So that other module can call
        gpg_key = self.get_key(key)
        url = self.get_url(key)
        distro = self.get_distro(key)
        comps = self.get_comps(key)
        comment = self.get_name(key)

        if ppa.is_ppa(url):
            file_name = '%s-%s' % (ppa.get_source_file_name(url), distro)
        else:
            file_name = self.get_slug(key)

        if gpg_key:
            proxy.add_apt_key_from_content(gpg_key)

        if not comps and distro:
            distro = distro + '/'
        elif not comps and not distro:
            distro = './'

        result = proxy.set_separated_entry(url, distro, comps,
                                           comment, enable, file_name)

        return str(result)

SOURCE_PARSER = SourceParser()

class SourceStatus(StatusProvider):
    def load_objects_from_parser(self, parser):
        init = self.get_init()

        for key in parser.keys():
            id = key
            slug = parser.get_slug(key)
            key = slug
            if init:
                log.debug('SourceStatus first init, set %s as read' % id)
                self.get_data()['apps'][key] = {}
                self.get_data()['apps'][key]['read'] = True
                self.get_data()['apps'][key]['cate'] = parser.get_category(id)
            else:
                if key not in self.get_data()['apps']:
                    self.get_data()['apps'][key] = {}
                    self.get_data()['apps'][key]['read'] = False
                    self.get_data()['apps'][key]['cate'] = parser.get_category(id)

        if init and parser.keys():
            log.debug('Init finish, SourceStatus set init to False')
            self.set_init(False)

        self.save()

    def get_read_status(self, key):
        try:
            return self.get_data()['apps'][key]['read']
        except:
            return True

    def set_as_read(self, key):
        try:
            self.get_data()['apps'][key]['read'] = True
        except:
            pass
        self.save()


class NoNeedDowngradeException(Exception):
    pass


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
        GObject.GObject.__init__(self)

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

    def update_downgrade_model(self, ppas):
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

        pkg_map = self.get_downgradeable_pkgs(pkg_dict)

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

            if pkg not in AptWorker.get_cache():
                log.debug("    package isn't available, continue next...\n")
                continue

            pkg = AptWorker.get_cache()[pkg]
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


class UpdateView(AppView):
    def __init__(self):
        AppView.__init__(self)

        self.set_headers_visible(False)

    def update_model(self, apps):
        model = self.get_model()

        length = len(apps)
        iter = model.append()
        model.set(iter,
                  self.COLUMN_INSTALLED, False,
                  self.COLUMN_DISPLAY,
                      '<span size="large" weight="bold">%s</span>' %
                          ngettext('%d New Application Available',
                                   '%d New Applications Available', length) % length,
                  )

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
                      ngettext('%d Package Update Available',
                               '%d Package Updates Available',
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
                        _('No Available Package Updates'))

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


class SourcesView(Gtk.TreeView):
    __gsignals__ = {
        'sourcechanged': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'new_purge': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,))
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

    def __init__(self):
        GObject.GObject.__init__(self)

        self.filter = None
        self.modelfilter = None
        self._status = None
        self.view_mode = 'view'
        self.to_purge = []

        self.model = self.__create_model()
        self.model.set_sort_column_id(self.COLUMN_NAME, Gtk.SortType.ASCENDING)
        self.set_model(self.model)

        self.set_search_column(self.COLUMN_NAME)

        self._add_column()

        self.selection = self.get_selection()

    def get_sourceslist(self):
        return SourcesList()

    def __create_model(self):
        model = Gtk.ListStore(GObject.TYPE_BOOLEAN,
                              GObject.TYPE_INT,
                              GObject.TYPE_INT,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GdkPixbuf.Pixbuf,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)

        return model

    def on_visible_filter(self, model, iter, data=None):
        log.debug("on_visible_filter: %s" % self.model.get_value(iter, self.COLUMN_NAME))
        category = self.model.get_value(iter, self.COLUMN_CATE)
        if self.filter == None or self.filter == category:
            return True
        else:
            return False

    def _add_column(self):
        renderer = Gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_enable_toggled)
        column = Gtk.TreeViewColumn(' ', renderer, active=self.COLUMN_ENABLED)
        column.set_sort_column_id(self.COLUMN_ENABLED)
        self.append_column(column)

        self.source_column = Gtk.TreeViewColumn(_('Third-Party Sources'))
        self.source_column.set_sort_column_id(self.COLUMN_NAME)
        self.source_column.set_spacing(5)
        renderer = Gtk.CellRendererPixbuf()
        self.source_column.pack_start(renderer, False)
        self.source_column.add_attribute(renderer, 'pixbuf', self.COLUMN_LOGO)

        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        self.source_column.pack_start(renderer, True)
        self.source_column.add_attribute(renderer, 'markup', self.COLUMN_DISPLAY)

        self.append_column(self.source_column)

    def set_status_active(self, active):
        if active:
            self._status = SourceStatus('sourcestatus.json')

    def get_status(self):
        return self._status

    def update_source_model(self, find='all', limit=-1, only_enabled=False):
        self.model.clear()
        sourceslist = self.get_sourceslist()
        enabled_list = []

        for source in sourceslist.list:
            if source.type == 'deb' and not source.disabled:
                enabled_list.append(source.uri)

        if self._status:
            self._status.load_objects_from_parser(SOURCE_PARSER)

        index = 0

        for id in SOURCE_PARSER:
            enabled = False
            index = index + 1
            url = SOURCE_PARSER.get_url(id)
            enabled = url in enabled_list

            if enabled:
                enabled_list.remove(url)

            if only_enabled:
                if not enabled:
                    continue
                elif not ppa.is_ppa(url):
                    continue
                else:
                    enabled = not enabled

            slug = SOURCE_PARSER.get_slug(id)
            comps = SOURCE_PARSER.get_comps(id)
            distro = SOURCE_PARSER.get_distro(id)
            category = SOURCE_PARSER.get_category(id)
            
            if find != 'all' and category != find:
                continue

            #TODO real top-10
            if limit > 0 and index >= limit:
                break

            name = SOURCE_PARSER.get_name(id)
            comment = SOURCE_PARSER.get_summary(id)
            pixbuf = get_source_logo_from_filename(SOURCE_PARSER[id]['logo'])
            website = SOURCE_PARSER.get_website(id)
            key = SOURCE_PARSER.get_key(id)

            if self._status and not self._status.get_read_status(slug):
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

        path = os.path.join(consts.DATA_DIR, 'pixmaps/ppa-logo.png')

        pixbuf = icon.get_from_file(path, size=32)

        if enabled_list and only_enabled:
            for url in enabled_list:
                if ppa.is_ppa(url):
                    iter = self.model.append()
                    self.model.set(iter,
                                   self.COLUMN_ENABLED, False,
                                   self.COLUMN_ID, 9999,
                                   self.COLUMN_CATE, -1,
                                   self.COLUMN_URL, url,
                                   self.COLUMN_DISTRO, distro,
                                   self.COLUMN_COMPS, comps,
                                   self.COLUMN_COMMENT, '',
                                   self.COLUMN_SLUG, url,
                                   self.COLUMN_NAME, ppa.get_basename(url),
                                   self.COLUMN_DISPLAY, ppa.get_long_name(url),
                                   self.COLUMN_LOGO, pixbuf,
                                   self.COLUMN_HOME, ppa.get_homepage(url),
                                   self.COLUMN_KEY, '',
                    )

    def set_as_read(self, iter, model):
        if type(model) == Gtk.TreeModelFilter:
            iter = model.convert_iter_to_child_iter(iter)
            model = model.get_model()
        id = model.get_value(iter, self.COLUMN_ID)
        slug = model.get_value(iter, self.COLUMN_SLUG)
        if self._status and not self._status.get_read_status(slug):
            name = model.get_value(iter, self.COLUMN_NAME)
            comment = model.get_value(iter, self.COLUMN_COMMENT)
            self._status.set_as_read(slug)
            model.set_value(iter,
                            self.COLUMN_DISPLAY,
                            '<b>%s</b>\n%s' % (name, comment))

    def get_sourcelist_status(self, url):
        for source in self.get_sourceslist():
            if url in source.str() and source.type == 'deb':
                return not source.disabled
        return False

    @log_func(log)
    def on_enable_toggled(self, cell, path):
        model = self.get_model()
        iter = model.get_iter((int(path),))

        id = model.get_value(iter, self.COLUMN_ID)
        name = model.get_value(iter, self.COLUMN_NAME)
        enabled = model.get_value(iter, self.COLUMN_ENABLED)
        url = model.get_value(iter, self.COLUMN_URL)

        if self.view_mode == 'view':
            conflicts = SOURCE_PARSER.get_conflicts(id)
            dependencies = SOURCE_PARSER.get_dependencies(id)

            #Convert to real model, because will involke the set method
            if type(model) == Gtk.TreeModelFilter:
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

                    dialog = QuestionDialog(title=_('Dependency Notice'),
                                            message= _('To enable this Source, You need to enable <b>"%s"</b> at first.\nDo you wish to continue?') \
                                % full_name)
                    if dialog.run() == Gtk.ResponseType.YES:
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
        else:
            #TODO purge dependencies
            status = not enabled
            model.set(iter, self.COLUMN_ENABLED, status)

            if status:
                self.to_purge.append(url)
            else:
                self.to_purge.remove(url)

            self.emit('new_purge', self.to_purge)

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
        model = self.get_model()

        id = model.get_value(iter, self.COLUMN_ID)
        url = model.get_value(iter, self.COLUMN_URL)
        icon = model.get_value(iter, self.COLUMN_LOGO)
        comment = model.get_value(iter, self.COLUMN_NAME)
        pre_status = self.get_sourcelist_status(url)
        result = SOURCE_PARSER.set_enable(id, enable)

        log.debug("Setting source %s (%d) to %s, result is %s" % (comment, id, str(enable), result))

        if result == 'enabled':
            model.set(iter, self.COLUMN_ENABLED, True)
        else:
            model.set(iter, self.COLUMN_ENABLED, False)

        if pre_status != enable:
            self.emit('sourcechanged')

        if enable:
            notify = Notify.Notification(summary=_('New source has been enabled'),
                                         body=_('%s is enabled now, Please click the refresh button to update the application cache.') % comment)
            notify.set_icon_from_pixbuf(icon)
            notify.set_hint_string ("x-canonical-append", "")
            notify.show()

class SourceCategoryView(CategoryView):
    def pre_update_cate_model(self):
#        self.model.append(None, (-3,
#                                 'latest',
#                                 _('Latest')))

#        self.model.append(None, (-2,
#                                 'top-10',
#                                 _('Top 10')))

        self.model.append(None, (-1,
                                 'enabled-ppa',
                                 _('Enabled PPAs')))

class SourceCenter(TweakModule):
    __title__  = _('Source Center')
    __desc__ = _('A collection of software sources to ensure your applications are always up-to-date.')
    __icon__ = 'software-properties'
    __url__ = 'http://ubuntu-tweak.com/source/'
    __urltitle__ = _('Visit online Source Center')
    __category__ = 'application'
    __keywords__ = 'ppa repository app'
    __utactive__ = False

    def __init__(self):
        TweakModule.__init__(self, 'sourcecenter.ui')

        self.url = SOURCE_VERSION_URL
        set_label_for_stock_button(self.sync_button, _('_Sync'))

        self.cateview = SourceCategoryView(os.path.join(SOURCE_ROOT, 'cates.json'))
        self.cateview.update_cate_model()
        self.cateview.get_selection().connect('changed', self.on_category_changed)
        self.left_sw.add(self.cateview)

        self.sourceview = SourcesView()
        self.sourceview.set_status_active(True)
        self.sourceview.update_source_model()
        self.sourceview.connect('sourcechanged', self.on_source_changed)
        self.sourceview.connect('new_purge', self.on_purge_changed)
        self.sourceview.get_selection().connect('changed', self.on_source_selection)
        self.sourceview.set_rules_hint(True)
        self.right_sw.add(self.sourceview)
        self.cateview.set_status_from_view(self.sourceview)

        self.update_timestamp()
        UPDATE_SETTING.set_value(False)
        UPDATE_SETTING.connect_notify(self.on_have_update, data=None)

        log.debug('Start check update')
        thread.start_new_thread(self.check_update, ())
        GObject.timeout_add(60000, self.update_timestamp)

        if self.check_source_upgradable() and UPGRADE_DICT:
            GObject.idle_add(self.upgrade_sources)

        self.add_start(self.main_vbox)

        self.connect('realize', self.setup_ui_tasks)

        GObject.idle_add(self.show_warning)

    @post_ui
    def show_warning(self):
        if not CONFIG.get_value():
            dialog = WarningDialog(title=_('Warning'),
                                   message=_('It is a possible security risk to '
                'use packages from Third-Party Sources.\n'
                'Please be careful and use only sources you trust.'),
                                   buttons=Gtk.ButtonsType.OK)
            checkbutton = CheckButton(_('Never show this dialog'),
                                      key=WARNING_KEY,
                                      backend='gsettings')
            dialog.add_option_button(checkbutton)

            dialog.run()
            dialog.destroy()

    def setup_ui_tasks(self, widget):
        self.purge_ppa_button.hide()
        self.cateview.expand_all()

    def check_source_upgradable(self):
        log.debug("The check source string is: \"%s\"" % self.__get_disable_string())
        for source in SourcesList():
            if self.__get_disable_string() in source.str() and \
                    source.uri in UPGRADE_DICT and \
                    source.disabled:
                return True

        return False

    def __get_disable_string(self):
        APP="update-manager"
        DIR="/usr/share/locale"

        gettext.bindtextdomain(APP, DIR)
        gettext.textdomain(APP)

        #the "%s" is in front, some is the end, so just return the long one
        translated = gettext.gettext("disabled on upgrade to %s")
        a, b = translated.split('%s')
        return a.strip() or b.strip()

    def update_timestamp(self):
        self.time_label.set_text(_('Last synced:') + ' ' + utdata.get_last_synced(SOURCE_ROOT))
        return True

    @post_ui
    def upgrade_sources(self):
        dialog = QuestionDialog(title=_('Upgrade Third Party Sources'),
                                message=_('After a successful distribution upgrade, '
                                'any third-party sources you use will be disabled by default.\n'
                                'Would you like to re-enable any sources disabled by Update Manager?'))

        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            proxy.upgrade_sources(self.__get_disable_string(), UPGRADE_DICT)
            if not self.check_source_upgradable():
                InfoDialog(_('Upgrade Successful!')).launch()
            else:
                ErrorDialog(_('Upgrade Failed!')).launch()
            self.emit('call', 'ubuntutweak.modules.sourceeditor', 'update_source_combo', {})
            self.update_sourceview()

    @post_ui
    def on_have_update(self, *args):
        if UPDATE_SETTING.get_value():
            dialog = QuestionDialog(_('New source data available, would you like to update?'))
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
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

    def on_source_selection(self, widget, data=None):
        model, iter = widget.get_selected()

        if iter:
            sourceview = widget.get_tree_view()
            sourceview.set_as_read(iter, model)
            self.cateview.update_selected_item()

            home = model.get_value(iter, self.sourceview.COLUMN_HOME)
            url = model.get_value(iter, self.sourceview.COLUMN_URL)
            description = model.get_value(iter, self.sourceview.COLUMN_COMMENT)

            self.set_details(home, url, description)

    def on_category_changed(self, widget, data=None):
        self.update_sourceview()

    def update_sourceview(self):
        self.cateview.set_status_from_view(self.sourceview)
        model, iter = self.cateview.get_selection().get_selected()

        limit = -1
        only_enabled = False
        if iter:
            find = model[iter][self.cateview.CATE_ID] or 'all'
            if find == -3:
                find = 'all'
            elif find == -2:
                find = 'all'
                limit = 10
            elif find == -1:
                find = 'all'
                only_enabled = True
        else:
            find = 'all'
        log.debug("Filter for %s" % find)
        self.sourceview.update_source_model(find=find,
                                     limit=limit,
                                     only_enabled=only_enabled)
        if only_enabled:
            self.purge_ppa_button.show()
            self.purge_ppa_button.set_sensitive(False)
            self.sourceview.source_column.set_title(_('All enabled PPAs (Select and click "Purge PPA" can safely downgrade packages)'))
            self.sourceview.view_mode = 'purge'
        else:
            self.purge_ppa_button.hide()
            self.sourceview.source_column.set_title(_('Third-Party Sources'))
            self.sourceview.view_mode = 'view'

    def set_details(self,
                    homepage='http://ubuntu-tweak.com',
                    url='http://ubuntu-tweak.com',
                    description=None):
        self.homepage_button.set_label(homepage)
        self.homepage_button.set_uri(homepage)

        if ppa.is_ppa(url):
            url = ppa.get_homepage(url)
        self.url_button.set_label(url)
        self.url_button.set_uri(url)

        self.description_label.set_text(description or _('Description is here'))

    def on_source_changed(self, widget):
        self.emit('call', 'ubuntutweak.modules.sourceeditor', 'update_source_combo', {})

    @log_func(log)
    def on_purge_changed(self, widget, purge_list):
        if purge_list:
            self.purge_ppa_button.set_sensitive(True)
        else:
            self.purge_ppa_button.set_sensitive(False)

    def on_update_button_clicked(self, widget):
        @log_func(log)
        def on_update_finished(transaction, status, parent):
            log.debug("on_update_finished")
            unset_busy(parent)

        set_busy(self)
        daemon = AptWorker(widget.get_toplevel(),
                           finish_handler=on_update_finished,
                           data=self)
        daemon.update_cache()

        self.emit('call', 'ubuntutweak.modules.appcenter', 'update_app_data', {})
        self.emit('call', 'ubuntutweak.modules.updatemanager', 'update_list', {})

    def on_source_data_downloaded(self, widget):
        path = widget.get_downloaded_file()
        tarfile = utdata.create_tarfile(path)

        if tarfile.is_valid():
            tarfile.extract(consts.CONFIG_ROOT)
            self.update_source_data()
            utdata.save_synced_timestamp(SOURCE_ROOT)
            self.update_timestamp()
        else:
            ErrorDialog(_('An error occurred whilst downloading the file')).launch()

    def update_source_data(self):
        global SOURCE_PARSER
        SOURCE_PARSER = SourceParser()

        self.sourceview.model.clear()
        self.sourceview.update_source_model()
        self.cateview.update_cate_model()
        self.cateview.expand_all()

    def on_sync_button_clicked(self, widget):
        dialog = CheckSourceDialog(widget.get_toplevel(), self.url)
        dialog.run()
        dialog.destroy()
        if dialog.status == True:
            dialog = QuestionDialog(_("Update available, Would you like to update?"))
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                dialog = FetchingDialog(parent=self.get_toplevel(), url=get_source_data_url())
                dialog.connect('destroy', self.on_source_data_downloaded)
                dialog.run()
                dialog.destroy()
        elif dialog.error == True:
            ErrorDialog(_("Network Error, Please check your network connection or the remote server is down.")).launch()
        else:
            utdata.save_synced_timestamp(SOURCE_ROOT)
            self.update_timestamp()
            InfoDialog(_("No update available.")).launch()

    @log_func(log)
    def on_purge_ppa_button_clicked(self, widget):
        # name_list is to display the name of PPA
        # url_list is to identify the ppa
        set_busy(self)
        name_list = []
        url_list = []
        log.debug("self.sourceview.to_purge: %s" % self.sourceview.to_purge)
        for url in self.sourceview.to_purge:
            name_list.append(ppa.get_short_name(url))
            url_list.append(url)

        log.debug("PPAs to purge: url_list: %s" % url_list)

        package_view = DowngradeView(self)
        package_view.update_downgrade_model(url_list)
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

        dialog = QuestionDialog(title=_("You're going to purge \"%s\":") % ', '.join(name_list),
                                message=message)
        dialog.set_resizable(True)
        dialog.get_content_area().pack_start(sw, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        dialog.destroy()
        # Workflow
        # 1. Downgrade all the PPA packages to offical packages
        #TODO Maybe not official? Because anther ppa which is enabled may have newer packages then offical
        # 2. If succeed, disable PPA, or keep it

        if response == Gtk.ResponseType.YES:
            log.debug("The select pkgs is: %s", str(select_pkgs))
            worker = AptWorker(widget.get_toplevel(),
                               finish_handler=self.on_package_work_finished,
                               data={'parent': self,
                                     'url_list': url_list})
            worker.downgrade_packages(select_pkgs)
        else:
            unset_busy(self)

    @log_func(log)
    def on_package_work_finished(self, transaction, status, kwargs):
        unset_busy(self)

        parent = kwargs['parent']
        url_list = kwargs['url_list']

        for url in url_list:
            #TODO remove vendor key
            result = proxy.purge_source(url, '')
            log.debug("Set source: %s to %s" % (url, str(result)))
        self.sourceview.to_purge = []
        self.update_sourceview()

        notify = Notify.Notification(summary=_('PPA has been purged'),
                                     body=_('It is highly recommend to do a "Refresh" source operation.'))
        notify.set_icon_from_pixbuf(self.get_pixbuf(size=48))
        notify.set_hint_string ("x-canonical-append", "")
        notify.show()
