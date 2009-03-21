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
import pango
import gobject
import apt_pkg
import webbrowser

from common.config import Config
from common.consts import *
from common.appdata import *
from common.policykit import PolkitButton, proxy
from common.systeminfo import module_check
from common.widgets import ListPack, TweakPage, GconfCheckButton
from common.widgets.dialogs import *
from aptsources.sourceslist import SourceEntry, SourcesList

(
    COLUMN_ENABLED,
    COLUMN_URL,
    COLUMN_DISTRO,
    COLUMN_COMPS,
    COLUMN_PACKAGE,
    COLUMN_LOGO,
    COLUMN_NAME,
    COLUMN_COMMENT,
    COLUMN_DISPLAY,
    COLUMN_HOME,
    COLUMN_KEY,
) = range(11)

(
    ENTRY_URL,
    ENTRY_DISTRO,
    ENTRY_COMPS,
) = range(3)

(
    SOURCE_NAME,
    SOURCE_PACKAGE,
    SOURCE_HOME,
    SOURCE_KEY,
) = range(4)

AWN = ['Avant Window Navigator', 'avant-window-navigator', 'awn-project.org', 'awn.gpg']
AWN_TESTING = [_('Avant Window Navigator (Unstable Version)'), 'avant-window-navigator', 'awn-project.org', 'awn-testing.gpg']
Amarok = ['Amarok', 'amarok-nightly', 'amarok.kde.org', 'neon.gpg']
Opera = ['Opera', 'opera', 'www.opera.com', 'opera.gpg']
Skype = ['Skype', 'skype', 'www.skype.com', '']
PlayOnLinux = ['PlayOnLinux', 'playonlinux', 'www.playonlinux.com', 'pol.gpg']
Ubuntu_cn = [_('Ubuntu Chinese Repository'), 'ubuntu-cn', 'www.ubuntu.org.cn', '']
Specto = ['Specto', 'specto', 'specto.sourceforge.net', 'specto.gpg']
OpenOffice = ['OpenOffice.org', 'openoffice', 'www.openoffice.org', 'ooo.gpg']
Ibus = ['Ibus', 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
Midori = ['Midori', 'midori', 'www.twotoasts.de', 'midori.gpg']
Firefox = ['Firefox', 'firefox', 'www.mozilla.org', 'firefox.gpg']
CompizFusion = ['Compiz Fusion', 'compiz-fusion', 'www.compiz-fusion.org/', 'compiz-fusion.gpg']
ChromiumBrowser = ['Chromium Browser', 'chromium-browser', 'launchpad.net/chromium-project', 'chromium-browser.gpg']
CairoDock = ['Cairo Dock', 'cairo-dock',  'cairo-dock.org', 'cairo-dock.gpg']
GnomeDo = ['GNOME Do', 'gnome-do', 'do.davebsd.com', 'do.gpg']
GlobalMenu = [_('Gnome Global Menu'), 'gnome-globalmenu', 'code.google.com/p/gnome2-globalmenu', 'globalmenu.gpg']
GettingThingsGnome = ['Getting Things Gnome!', 'gtg', 'gtg.fritalk.com', 'gtg.gpg']
Gwibber = ['Gwibber', 'gwibber', 'launchpad.net/gwibber', 'gwibber.gpg']
Banshee_Stable = [_('Banshee (Stable Version)'), 'banshee', 'banshee-project.org', 'banshee-stable.gpg']
Banshee_Unstable = [_('Banshee (Unstable Version)'), 'banshee', 'banshee-project.org', 'banshee-unstable.gpg']
Google = ['Google', 'google', 'www.google.com/linuxrepositories/index.html', 'google.gpg']
GoogleGadgets = ['Google gadgets', 'google-gadgets', 'desktop.google.com/plugins/', 'gadgets.gpg']
ChmSee = ['Chmsee', 'chmsee', 'chmsee.gro.clinux.org', 'chmsee.gpg']
KDE4 = ['KDE 4', 'kde-4', 'www.kde.org', 'kde4.gpg']
UbuntuTweak = ['Ubuntu Tweak', 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak.gpg']
UbuntuTweakTesting = [_('Ubuntu Tweak (Unstable Version)'), 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak-unstable.gpg']
NautilusDropbox = ['Nautilus DropBox', 'nautilus-dropbox', 'www.getdropbox.com', '']
Screenlets = ['Screenlets', 'screenlets', 'www.screenlets.org', 'screenlets.gpg']
Wine = ['Wine', 'wine', 'www.winehq.org', 'wine.gpg']
LXDE = ['LXDE', 'lxde', 'lxde.org', 'lxde.gpg']
Terminator = ['Terminator', 'terminator', 'www.tenshu.net/terminator/', 'terminator.gpg']
Transmission_Stable = ['Transmission (Stable Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_stable.gpg']
Transmission_Beta = ['Transmission (Beta Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_beta.gpg']
Transmission_Nightly = ['Transmission (Nightly Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_nightly.gpg']
VirtualBox = ['VirtualBox', 'virtualbox', 'www.virtualbox.org/', 'virtualbox.gpg']
Shutter = ['Shutter', 'shutter', 'launchpad.net/shutter', 'shutter.gpg']
Galaxium = ['Galaxium', 'galaxium', 'code.google.com/p/galaxium/', 'galaxium.gpg']
Swiftweasel = ['Swiftweasel', 'swiftweasel', 'swiftweasel.tuxfamily.org/', '']
Medibuntu = ['Medibuntu', 'medibuntu', 'www.medibuntu.org', 'medibuntu.gpg']
WineDoors = ['Wine Doors', 'wine-doors', 'www.wine-doors.org', 'wine-doors.gpg']
XBMC = ['XBMC', 'xbmc', 'xbmc.org', 'xbmc.gpg']

SOURCES_DATA = [
    ['http://ppa.launchpad.net/reacocard-awn/ubuntu/', ['hardy','intrepid'], 'main', AWN],
    ['http://ppa.launchpad.net/awn-testing/ppa/ubuntu', ['hardy','intrepid', 'jaunty'], 'main', AWN_TESTING],
    ['http://ppa.launchpad.net/project-neon/ubuntu/', ['hardy', 'intrepid'], 'main', Amarok],
    ['http://archive.ubuntu.org.cn/ubuntu-cn/', ['hardy', 'intrepid'], 'main restricted universe multiverse', Ubuntu_cn],
    ['http://ppa.launchpad.net/openoffice-pkgs/ubuntu', 'intrepid', 'main', OpenOffice],
    ['http://ppa.launchpad.net/globalmenu-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GlobalMenu],
    ['http://ppa.launchpad.net/chromium-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', ChromiumBrowser],
    ['http://ppa.launchpad.net/specto/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Specto],
    ['http://ppa.launchpad.net/gtg/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', GettingThingsGnome],
    ['http://deb.opera.com/opera/', 'lenny', 'non-free', Opera],
    ['http://download.skype.com/linux/repos/debian', 'stable', 'non-free', Skype],
    ['http://ppa.launchpad.net/gwibber-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Gwibber],
    ['http://playonlinux.botux.net/', 'hardy', 'main', PlayOnLinux],
    ['http://ppa.launchpad.net/webkit-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Midori],
    ['http://ppa.launchpad.net/ibus-dev/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', Ibus],
    ['http://ppa.launchpad.net/ubuntu-mozilla-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Firefox],
    ['http://ppa.launchpad.net/compiz/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', CompizFusion],
    ['http://repository.cairo-dock.org/ubuntu', ['hardy', 'intrepid'], 'cairo-dock', CairoDock],
    ['http://ppa.launchpad.net/do-core/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GnomeDo],
    ['http://ppa.launchpad.net/banshee-team/ubuntu', ['hardy', 'intrepid'], 'main', Banshee_Stable],
    ['http://ppa.launchpad.net/banshee-unstable-team/ubuntu', ['hardy', 'intrepid'], 'main', Banshee_Unstable],
    ['http://dl.google.com/linux/deb/', 'stable', 'non-free', Google],
    ['http://ppa.launchpad.net/googlegadgets/ubuntu', 'hardy', 'main', GoogleGadgets],
    ['http://ppa.launchpad.net/lidaobing/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', ChmSee],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ubuntu', ['hardy', 'intrepid'], 'main', KDE4],
    ['http://linux.getdropbox.com/ubuntu', ['hardy', 'intrepid'], 'main', NautilusDropbox],
    ['http://ppa.launchpad.net/tualatrix/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', UbuntuTweak],
    ['http://ppa.launchpad.net/ubuntu-tweak-testing/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', UbuntuTweakTesting],
    ['http://ppa.launchpad.net/gilir/ubuntu', ['hardy', 'intrepid'], 'main', Screenlets],
    ['http://wine.budgetdedicated.com/apt', ['hardy', 'intrepid'], 'main', Wine],
    ['http://ppa.launchpad.net/lxde/ubuntu', 'hardy', 'main', LXDE],
    ['http://ppa.launchpad.net/gnome-terminator/ubuntu', ['hardy', 'intrepid'], 'main', Terminator],
    ['http://ppa.launchpad.net/transmissionbt/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Stable],
    ['http://ppa.launchpad.net/transmissionbt-beta/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Beta],
    ['http://ppa.launchpad.net/transmissionbt-nightly/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Nightly],
    ['http://download.virtualbox.org/virtualbox/debian', ['hardy', 'intrepid'], 'non-free', VirtualBox],
    ['http://ppa.launchpad.net/shutter/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Shutter],
    ['http://ppa.launchpad.net/galaxium/ubuntu', 'hardy', 'main', Galaxium],
    ['http://download.tuxfamily.org/swiftweasel', ['hardy', 'intrepid'], 'multiverse', Swiftweasel],
    ['http://packages.medibuntu.org/', ['hardy', 'intrepid', 'jaunty'], 'free non-free', Medibuntu],
    ['http://ppa.launchpad.net/wine-doors-dev-team/ppa/ubuntu', 'intrepid', 'main', WineDoors],
    ['http://ppa.launchpad.net/team-xbmc/ubuntu', ['hardy', 'intrepid'], 'main', XBMC],
]

def is_ubuntu(distro):
    if type(distro) == list:
        for dis in distro:
            if dis in module_check.get_supported_ubuntu():
                return True
            return False
    else:
        if distro in module_check.get_supported_ubuntu():
            return True
        return False

def filter_sources():
    newsource = []
    for item in SOURCES_DATA:
        distro = item[1]
        if is_ubuntu(distro):
            if module_check.get_codename() in distro:
                newsource.append([item[0], module_check.get_codename(), item[2], item[3]])
        else:
            newsource.append(item)

    return newsource

SOURCES_DATA = filter_sources()

class UpdateCacheDialog:
    """This class is modified from Software-Properties"""
    def __init__(self, parent):
        self.parent = parent

        self.dialog = QuestionDialog(_('To install software and updates from '
            'newly added or changed sources, you have to reload the information '
            'about available software.\n\n'
            'You need a working internet connection to continue.'), 
            title = _('The information about available software is out-of-date'))

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

        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_column()

        self.update_model()
        self.selection = self.get_selection()

    def get_sourceslist(self):
        from aptsources.sourceslist import SourcesList
        return SourcesList()

    def __create_model(self):
        model = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
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
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup = COLUMN_DISPLAY)

        self.append_column(column)

    def update_model(self):
        self.model.clear()
        sourceslist = self.get_sourceslist()

        for entry in SOURCES_DATA:
            enabled = False
            url = entry[ENTRY_URL]
            comps = entry[ENTRY_COMPS]
            distro = entry[ENTRY_DISTRO]

            source = entry[-1]
            name = source[SOURCE_NAME]
            package = source[SOURCE_PACKAGE]
            comment = get_source_describ(package)
            logo = gtk.gdk.pixbuf_new_from_file(get_source_logo(package))
            home = source[SOURCE_HOME]
            if home:
                home = 'http://' + home
            key = source[SOURCE_KEY]
            if key:
                key = os.path.join(DATA_DIR, 'aptkeys', source[SOURCE_KEY])

            for source in sourceslist:
                if url in source.str() and source.type == 'deb':
                    enabled = not source.disabled

            self.model.append((
                enabled,
                url,
                distro,
                comps,
                package,
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
        name = self.model.get_value(iter, COLUMN_PACKAGE)
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
        webbrowser.open(link)

    def set_details(self, homepage = None, url = None, description = None):
        if homepage:
            self.homepage_button.destroy()
            self.homepage_button = gtk.LinkButton(homepage)
            self.homepage_button.show()
            self.table.attach(self.homepage_button, 1, 2, 0, 1)

        if url:
            if 'ppa.launchpad.net' in url:
                url = 'https://launchpad.net/~%s/+archive/ppa' % url.split('/')[3]
            self.url_button.destroy()
            self.url_button = gtk.LinkButton(url)
            self.url_button.show()
            self.table.attach(self.url_button, 1, 2, 1, 2)

        if description:
            self.description.set_text(description)

class ThirdSoft(TweakPage):
    def __init__(self):
        TweakPage.__init__(self, 
                _('Third-Party Software Sources'), 
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

        hbox = gtk.HBox(False, 5)
        self.pack_end(hbox, False, False, 0)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 0)

        self.refresh_button = gtk.Button(stock = gtk.STOCK_REFRESH)
        self.refresh_button.set_sensitive(False)
        self.refresh_button.connect('clicked', self.on_refresh_button_clicked)
        hbox.pack_end(self.refresh_button, False, False, 0)

    def update_thirdparty(self):
        self.treeview.update_model()

    def on_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter is None:
            return
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
                    dialog = WarningDialog(_('It is a possible security risk to '
                        'use packages from Third-Party Sources.\n'
                        'Please be careful.'), 
                        buttons = gtk.BUTTONS_OK, title = _('Warning'))
                    vbox = dialog.get_child()
                    hbox = gtk.HBox()
                    vbox.pack_start(hbox, False, False, 0)
                    checkbutton = GconfCheckButton(_('Never show this dialog'), WARNING_KEY)
                    hbox.pack_end(checkbutton, False, False, 0)
                    hbox.show_all()

                    dialog.run()
                    dialog.destroy()
            else:
                ServerErrorDialog().launch()
        else:
            AuthenticateFailDialog().launch()

    def colleague_changed(self, widget):
        self.refresh_button.set_sensitive(True)
        self.emit('update', 'sourceeditor', 'update_sourceslist')
    
    def on_refresh_button_clicked(self, widget):
        dialog = UpdateCacheDialog(widget.get_toplevel())
        res = dialog.run()

        proxy.set_liststate('normal')
        widget.set_sensitive(False)

        InfoDialog(_('You can install the new applications through Add/Remove.'),
            title = _('The software information is up-to-date now')).launch()
        self.emit('update', 'installer', 'deep_update')

if __name__ == '__main__':
    from utility import Test
    Test(ThirdSoft)
