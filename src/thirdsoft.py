#!/usr/bin/python

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

import pygtk
pygtk.require("2.0")
import gtk
import os
import dbus
import time
import thread
import subprocess
import gobject
import apt_pkg

from common.config import Config
from gnome import url_show
from common.consts import *
from common.appdata import *
from common.factory import Factory
from common.policykit import PolkitButton, proxy
from common.systeminfo import module_check
from common.widgets import ListPack, TweakPage, GconfCheckButton, InfoDialog, WarningDialog, ErrorDialog, QuestionDialog
from aptsources.sourceslist import SourceEntry, SourcesList

(
    COLUMN_ENABLED,
    COLUMN_URL,
    COLUMN_DISTRO,
    COLUMN_COMPS,
    COLUMN_LOGO,
    COLUMN_NAME,
    COLUMN_COMMENT,
    COLUMN_DISPLAY,
    COLUMN_HOME,
    COLUMN_KEY,
) = range(10)

(
    ENTRY_URL,
    ENTRY_DISTRO,
    ENTRY_COMPS,
) = range(3)

(
    SOURCE_NAME,
    SOURCE_HOME,
    SOURCE_KEY,
) = range(3)

AWN = ['Avant Window Navigator', 'awn-project.org', '']
Amarok = ['Amarok Nightly', 'amarok.kde.org', '']
Opera = ['Opera', 'www.opera.com', 'opera.gpg']
Skype = ['Skype', 'www.skype.com', '']
PlayOnLinux = ['PlayOnLinux', 'www.playonlinux.com', 'pol.gpg']
Eioffice = ['EIOffice Personal', 'www.evermoresw.com', '']
Midori = ['Midori', 'www.twotoasts.de', '']
Firefox = ['Firefox', 'www.mozilla.org', '']
CompizFusion = ['Compiz Fusion', 'www.compiz-fusion.org/', '']
CairoDock = ['Cairo Dock', 'cairo-dock.org', '']
GnomeDo = ['GNOME Do', 'do.davebsd.com', '']
Banshee = ['Banshee', 'banshee-project.org', '']
Google = ['Google', 'www.google.com/linuxrepositories/index.html', 'google.gpg']
GoogleGadgets = ['Google gadgets', 'desktop.google.com/plugins/', '']
ChmSee = ['chmsee', 'chmsee.gro.clinux.org', '']
KDE4 = ['KDE 4', 'www.kde.org', '']
UbuntuTweak = ['Ubuntu Tweak', 'ubuntu-tweak.com', '']
NautilusDropbox = ['Nautilus-DropBox', 'www.getdropbox.com', '']
Screenlets = ['Screenlets', 'www.screenlets.org', '']
Wine = ['Wine', 'www.winehq.org', 'wine.gpg']
LXDE = ['LXDE', 'lxde.org', '']
Terminator = ['Terminator', 'www.tenshu.net/terminator/', '']
VirtualBox = ['VirtualBox', 'www.virtualbox.org/', 'virtualbox.gpg']
GScrot = ['GScrot', 'launchpad.net/gscrot', '']
Galaxium = ['Galaxium', 'code.google.com/p/galaxium/', '']
Swiftweasel = ['Swiftweasel', 'swiftweasel.tuxfamily.org/', '']
Medibuntu = ['Medibuntu', 'www.medibuntu.org/', 'medibuntu.gpg']
XBMC = ['XBMC', 'xbmc.org', '']

SOURCES_DATA = [
    ['http://ppa.launchpad.net/reacocard-awn/ubuntu/', ['hardy','intrepid'], 'main', AWN],
    ['http://ppa.launchpad.net/project-neon/ubuntu/', ['hardy', 'intrepid'], 'main', Amarok],
    ['http://archive.ubuntu.org.cn/ubuntu-cn/', ['hardy', 'intrepid'], 'main restricted universe multiverse', Eioffice],
    ['http://deb.opera.com/opera/', 'lenny', 'non-free', Opera],
    ['http://download.skype.com/linux/repos/debian', 'stable', 'non-free', Skype],
    ['http://playonlinux.botux.net/', 'hardy', 'main', PlayOnLinux],
    ['http://ppa.launchpad.net/stemp/ubuntu', ['hardy', 'intrepid'], 'main', Midori],
    ['http://ppa.launchpad.net/fta/ubuntu', ['hardy', 'intrepid'], 'main', Firefox],
    ['http://ppa.launchpad.net/compiz/ubuntu', ['hardy', 'intrepid'], 'main', CompizFusion],
    ['http://repository.cairo-dock.org/ubuntu', 'hardy', 'cairo-dock', CairoDock],
    ['http://ppa.launchpad.net/do-core/ubuntu', ['hardy', 'intrepid'], 'main', GnomeDo],
    ['http://ppa.launchpad.net/banshee-team/ubuntu', 'hardy', 'main', Banshee],
    ['http://dl.google.com/linux/deb/', 'stable', 'non-free', Google],
    ['http://ppa.launchpad.net/googlegadgets/ubuntu', 'hardy', 'main', GoogleGadgets],
    ['http://ppa.launchpad.net/lidaobing/ubuntu', 'hardy', 'main', ChmSee],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ubuntu', 'hardy', 'main', KDE4],
    ['http://www.getdropbox.com/static/ubuntu', 'hardy', 'main', NautilusDropbox],
    ['http://ppa.launchpad.net/tualatrix/ubuntu', 'hardy', 'main', UbuntuTweak],
    ['http://ppa.launchpad.net/gilir/ubuntu', 'hardy', 'main', Screenlets],
    ['http://wine.budgetdedicated.com/apt', ['hardy', 'intrepid'], 'main', Wine],
    ['http://ppa.launchpad.net/lxde/ubuntu', 'hardy', 'main', LXDE],
    ['http://ppa.launchpad.net/gnome-terminator/ubuntu', ['hardy', 'intrepid'], 'main', Terminator],
    ['http://download.virtualbox.org/virtualbox/debian', 'hardy', 'non-free', VirtualBox],
    ['http://ppa.launchpad.net/gscrot/ubuntu', ['hardy', 'intrepid'], 'main', GScrot],
    ['http://ppa.launchpad.net/galaxium/ubuntu', 'hardy', 'main', Galaxium],
    ['http://download.tuxfamily.org/swiftweasel', 'hardy', 'multiverse', Swiftweasel],
    ['http://packages.medibuntu.org/', ['hardy', 'intrepid'], 'free non-free', Medibuntu],
    ['http://ppa.launchpad.net/team-xbmc/ubuntu', 'hardy', 'main', XBMC],
]

def filter_sources(light = False):
    newsource = []
    for item in SOURCES_DATA:
        distro = item[1]
        if light and distro == 'hardy' and module_check.is_intrepid():
            newsource.append(item)
        elif module_check.get_codename() in distro:
            newsource.append([item[0], module_check.get_codename(), item[2], item[3]])
        else:
            if distro not in ['hardy', 'intrepid']:
                newsource.append(item)

    return newsource

SOURCES_DATA = filter_sources()

class UpdateCacheDialog:
    """This class is modified from Software-Properties"""
    def __init__(self, parent):
        self.parent = parent

        self.dialog = QuestionDialog(_('<b><big>The information about available software is out-of-date</big></b>\n\nTo install software and updates from newly added or changed sources, you have to reload the information about available software.\n\nYou need a working internet connection to continue.'))

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
        res = self.dialog.run()
        self.dialog.hide()
        if res == gtk.RESPONSE_YES:
            self.parent.set_sensitive(False)
            lock = thread.allocate_lock()
            lock.acquire()
            t = thread.start_new_thread(self.update_cache,
                                       (self.parent.window.xid, lock))
            while lock.locked():
                while gtk.events_pending():
                    gtk.main_iteration()
                    time.sleep(0.05)
            self.parent.set_sensitive(True)
        return res

class SourcesView(gtk.TreeView):
    __gsignals__ = {
        'sourcechanged': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.list = SourcesList()
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_column()

        self.update_model()
        self.selection = self.get_selection()

    def __create_model(self):
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
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

    def __add_column(self):
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_enable_toggled)
        column = gtk.TreeViewColumn(' ', renderer, active = COLUMN_ENABLED)
        column.set_sort_column_id(COLUMN_ENABLED)
        self.append_column(column)

        column = gtk.TreeViewColumn(_('Third-Party Sources'))
        column.set_sort_column_id(COLUMN_NAME)
        column.set_spacing(5)
        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_LOGO)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup = COLUMN_DISPLAY)

        self.append_column(column)

    def update_model(self):
        for entry in SOURCES_DATA:
            enabled = False
            url = entry[ENTRY_URL]
            comps = entry[ENTRY_COMPS]
            distro = entry[ENTRY_DISTRO]

            source = entry[-1]
            name = source[SOURCE_NAME]
            comment = get_source_describ(name)
            logo = gtk.gdk.pixbuf_new_from_file(get_source_logo(name))
            home = source[SOURCE_HOME]
            if home:
                home = 'http://' + home
            key = source[SOURCE_KEY]
            if key:
                key = os.path.join(DATA_DIR, 'aptkeys', source[SOURCE_KEY])

            for source in self.list:
                if url in source.str() and source.type == 'deb':
                    enabled = not source.disabled

            self.model.append((
                enabled,
                url,
                distro,
                comps,
                logo,
                name,
                comment,
                '<b>%s</b>\n%s' % (name, comment),
                home,
                key,
                ))

    def on_enable_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))
        enabled = self.model.get_value(iter, COLUMN_ENABLED)
        url = self.model.get_value(iter, COLUMN_URL)
        distro = self.model.get_value(iter, COLUMN_DISTRO)
        name = self.model.get_value(iter, COLUMN_NAME)
        comps = self.model.get_value(iter, COLUMN_COMPS)
        key = self.model.get_value(iter, COLUMN_KEY)

        if key:
            proxy.add_aptkey(key)

        result = proxy.set_entry(url, distro, comps, name, not enabled)

        if result == 'enabled':
            self.model.set(iter, COLUMN_ENABLED, True)
        else:
            self.model.set(iter, COLUMN_ENABLED, False)
            
        self.emit('sourcechanged')

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

            self.table.attach(label, 0, 1, i, i + 1, xoptions = gtk.FILL, xpadding = 10, ypadding = 5)

        self.homepage_button = gtk.LinkButton('http://ubuntu-tweak.com')
        self.table.attach(self.homepage_button, 1, 2, 0, 1)
        self.url_button = gtk.LinkButton('http://ubuntu-tweak.com')
        self.table.attach(self.url_button, 1, 2, 1, 2)
        self.description = gtk.Label(_('Description is here'))
        self.description.set_line_wrap(True)
        self.table.attach(self.description, 1, 2, 2, 3)

    def click_website(self, widget, link):
        url_show(link)

    def set_details(self, homepage = None, url = None, description = None):
        if homepage:
            self.homepage_button.destroy()
            self.homepage_button = gtk.LinkButton(homepage)
            self.homepage_button.show()
            self.table.attach(self.homepage_button, 1, 2, 0, 1)

        if url:
            if 'ppa.launchpad.net' in url:
                url = 'https://launchpad.net/~%s/+archive' % url.split('/')[3]
            self.url_button.destroy()
            self.url_button = gtk.LinkButton(url)
            self.url_button.show()
            self.table.attach(self.url_button, 1, 2, 1, 2)

        if description:
            self.description.set_text(description)

class ThirdSoft(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Third-Party Softwares Sources'), 
                _('After every releases of Ubuntu comes a feature freeze.\nThis means only applications with bug-fixes get into the repository.\nBy using third-party DEB repositories, you can always keep up-to-date with the latest version.\nAfter adding these repositories, locate and install them using Add/Remove.'))

        self.__config = Config()

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.pack_start(sw)

        self.treeview = SourcesView()
        self.treeview.connect('sourcechanged', self.colleague_changed)
        self.treeview.selection.connect('changed', self.on_selection_changed)
        self.treeview.set_sensitive(False)
        self.treeview.set_rules_hint(True)
        sw.add(self.treeview)

        self.expander = gtk.Expander(_('Details'))
        self.pack_start(self.expander, False, False, 0)
        self.sourcedetail = SourceDetail()
        self.expander.set_sensitive(False)
        self.expander.add(self.sourcedetail)

        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False, False, 5)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 5)

        self.refresh_button = gtk.Button(stock = gtk.STOCK_REFRESH)
        self.refresh_button.set_sensitive(False)
        self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
        hbox.pack_end(self.refresh_button, False, False, 5)

    def on_selection_changed(self, widget):
        model, iter = widget.get_selected()

        home = model.get_value(iter, COLUMN_HOME)
        url = model.get_value(iter, COLUMN_URL)
        description = model.get_value(iter, COLUMN_COMMENT)

        self.sourcedetail.set_details(home, url, description)

    def on_polkit_action(self, widget, action):
        if action:
            if proxy.get_proxy():
                self.treeview.set_sensitive(True)
                self.expander.set_sensitive(True)
                WARNING_KEY = '/apps/ubuntu-tweak/disable_thidparty_warning'

                if not self.__config.get_value(WARNING_KEY):
                    dialog = WarningDialog(_('<b><big>Warning</big></b>\n\nIt is a possible security risk to use packages from Third-Party Sources. Please be careful.'), buttons = gtk.BUTTONS_OK)
                    vbox = dialog.get_child()
                    hbox = gtk.HBox()
                    vbox.pack_start(hbox, False, False, 0)
                    checkbutton = GconfCheckButton(_('Never show this dialog'), WARNING_KEY)
                    hbox.pack_end(checkbutton, False, False, 0)
                    hbox.show_all()

                    dialog.run()
                    dialog.destroy()
            else:
                ErrorDialog(_("<b><big>Service hasn't initialized yet</big></b>\n\nYou need to restart your Ubuntu.")).launch()
        else:
            ErrorDialog(_('<b><big>Could not authenticate</big></b>\n\nAn unexpected error has occurred.')).launch()

    def colleague_changed(self, widget):
        self.refresh_button.set_sensitive(True)
        self.emit('update', 'sourceeditor', 'update_sourceslist')
    
    def on_refresh_button_clicked(self, widget):
        dialog = UpdateCacheDialog(widget.get_toplevel())
        res = dialog.run()

        proxy.set_liststate('normal')
        widget.set_sensitive(False)

        InfoDialog(_('<b><big>The software information is up-to-date now</big></b>\n\nYou can install the new applications through Add/Remove.')).launch()
        self.emit('update', 'installer', 'deep_update')

if __name__ == '__main__':
    from utility import Test
    Test(ThirdSoft)
