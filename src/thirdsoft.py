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

import os
import gtk
import time
import thread
import subprocess
import pango
import gobject
import apt_pkg
import webbrowser

from common.config import Config
from common.consts import *
from common.appdata import get_source_logo, get_source_describ
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

SOURCES_LIST = '/etc/apt/sources.list'

AWN = ['Avant Window Navigator', 'avant-window-navigator', 'awn-project.org', 'awn.gpg']
AWN_TESTING = [_('Avant Window Navigator (Unstable Version)'), 'avant-window-navigator', 'awn-project.org', 'awn-testing.gpg']
Amarok = ['Amarok', 'amarok-nightly', 'amarok.kde.org', 'neon.gpg']
AmuleRelease = [_('aMule (Stable Version)'), 'amule', 'www.amule.org', 'amule-release.gpg']
Blueman = ['Blueman', 'blueman', 'blueman-project.org', 'blueman.gpg']
Backintime = ['Back In Time', 'backintime-gnome', 'backintime.le-web.org', 'backintime.gpg']
Opera = ['Opera', 'opera', 'www.opera.com', 'opera.gpg']
Skype = ['Skype', 'skype', 'www.skype.com', '']
PlayOnLinux = ['PlayOnLinux', 'playonlinux', 'www.playonlinux.com', 'pol.gpg']
Ubuntu_cn = [_('Ubuntu Chinese Repository'), 'ubuntu-cn', 'www.ubuntu.org.cn', '']
Specto = ['Specto', 'specto', 'specto.sourceforge.net', 'specto.gpg']
OpenOffice = ['OpenOffice.org', 'openoffice', 'www.openoffice.org', 'ooo.gpg']
IBus = [_('IBus (Old Version)'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Intrepid = [_('IBus 1.2 for intrepid'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Jaunty = [_('IBus 1.2 for jaunty'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
IBus_Karmic = [_('IBus 1.2 for karmic'), 'ibus', 'code.google.com/p/ibus', 'ibus-dev.gpg']
Midori = ['Midori', 'midori', 'www.twotoasts.de', 'midori.gpg']
Empathy = ['Empathy', 'empathy', 'launchpad.net/~telepathy', 'empathy.gpg']
WebKitGtk = ['WebKitGtk', 'webkitgtk', 'webkitgtk.org', 'webkitgtk.gpg']
Firefox = ['Firefox', 'firefox', 'www.mozilla.org', 'firefox.gpg']
MozillaSecurity = [_('Ubuntu Mozilla Security Team'), 'mozilla-security', 'launchpad.net/~ubuntu-mozilla-security', 'mozilla-security.gpg']
CompizFusion = ['Compiz Fusion', 'compiz-fusion', 'www.compiz-fusion.org', 'compiz-fusion.gpg']
Christine = [_('Christine Media Player'), 'christine', 'www.christine-project.org', 'christine.gpg']
ChromiumBrowser = ['Chromium Browser', 'chromium-browser', 'launchpad.net/chromium-project', 'chromium-browser.gpg']
CairoDock = ['Cairo Dock', 'cairo-dock',  'cairo-dock.org', 'cairo-dock.gpg']
Geany = ['Geany', 'geany', 'www.geany.org', 'geany.gpg']
Gnote = ['Gnote', 'gnote', 'live.gnome.org/Gnote', 'gnote.gpg']
GnomeDo = ['GNOME Do', 'gnome-do', 'do.davebsd.com', 'do.gpg']
GnomeGames = [_('Experimental Gnome Games'), 'gnome-games', 'launchpad.net/~gnome-games-experimental', 'gnome-games.gpg']
GnomeColors = ['Gnome Colors', 'gnome-colors', 'launchpad.net/~gnome-colors-packagers', 'gnome-colors.gpg']
Gmchess = [_('Chinese Chess'), 'gmchess', 'lerosua.org', 'gmchess.gpg']
GlobalMenu = [_('Gnome Global Menu'), 'gnome-globalmenu', 'code.google.com/p/gnome2-globalmenu', 'globalmenu.gpg']
GettingThingsGnome = ['Getting Things Gnome!', 'gtg', 'gtg.fritalk.com', 'gtg.gpg']
GetDeb = [_('GetDeb.net (Mirror)'), 'getdeb', 'www.getdeb.net', '']
Gwibber = ['Gwibber', 'gwibber', 'launchpad.net/gwibber', 'gwibber.gpg']
Gwibber_Daily = [_('Gwibber (Daily Version)'), 'gwibber', 'launchpad.net/gwibber', 'gwibber-daily.gpg']
Gimp_Testing = [_('GIMP (Testing Version)'), 'gimp', 'www.gimp.org', 'gimp-testing.gpg']
Banshee_Stable = [_('Banshee (Stable Version)'), 'banshee', 'banshee-project.org', 'banshee-stable.gpg']
Banshee_Unstable = [_('Banshee (Unstable Version)'), 'banshee', 'banshee-project.org', 'banshee-unstable.gpg']
Google = [_('Google Repository'), 'google', 'www.google.com/linuxrepositories/index.html', 'google.gpg']
Google_Testing = [_('Google Testing Repository'), 'google', 'www.google.com/linuxrepositories/testrepo.html', 'google.gpg']
GoogleGadgets = ['Google gadgets', 'google-gadgets', 'desktop.google.com/plugins/', 'gadgets.gpg']
ChmSee = ['Chmsee', 'chmsee', 'chmsee.gro.clinux.org', 'chmsee.gpg']
KDE4 = ['KDE 4', 'kde-4', 'www.kde.org', 'kde4.gpg']
UbuntuTweak = ['Ubuntu Tweak', 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak.gpg']
UbuntuTweakTesting = [_('Ubuntu Tweak (Unstable Version)'), 'ubuntu-tweak', 'ubuntu-tweak.com', 'tweak-unstable.gpg']
UbuDSL = ['UbuDSL', 'ubudsl', 'www.ubudsl.com', 'ubndsl.gpg']
NautilusDropbox = ['Nautilus DropBox', 'nautilus-dropbox', 'www.getdropbox.com', '']
Screenlets = ['Screenlets', 'screenlets', 'www.screenlets.org', 'screenlets.gpg']
Synapse = ['Synapse', 'synapse', 'synapse.im', 'synapse.gpg']
Smplayer = ['SMPlayer', 'smplayer', 'smplayer.sourceforge.net', 'smplayer.gpg']
MplayerLibs = [_('MPlayer Core Libraries'), 'mplayer', 'launchpad.net/~rvm/+archive/libs', 'mplayer-libs.gpg']
Smplayer_Testing = [_('SMPlayer (Unstable Version)'), 'smplayer', 'smplayer.sourceforge.net', 'smplayer-testing.gpg']
Wine = ['Wine', 'wine', 'www.winehq.org', 'wine.gpg']
LXDE = ['LXDE', 'lxde', 'lxde.org', 'lxde.gpg']
Liferea = ['Liferea', 'liferea', 'liferea.sourceforge.net', 'liferea.gpg']
Terminator = ['Terminator', 'terminator', 'www.tenshu.net/terminator/', 'terminator.gpg']
Transmission_Stable = ['Transmission (Stable Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_stable.gpg']
Transmission_Beta = ['Transmission (Beta Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_beta.gpg']
Transmission_Nightly = ['Transmission (Nightly Version)', 'transmission-gtk', 'www.transmissionbt.com', 'transmission_nightly.gpg']
VirtualBox = ['VirtualBox', 'virtualbox', 'www.virtualbox.org', 'virtualbox.gpg']
VirtualBoxOse = [_('VirtualBox (Open Source Edition)'), 'virtualbox-ose', 'www.virtualbox.org', 'virtualboxose.gpg']
Vlc = [_('VLC media player'), 'vlc', 'www.videolan.org/vlc/', 'vlc.gpg']
Shutter = ['Shutter', 'shutter', 'launchpad.net/shutter', 'shutter.gpg']
Pidgin = ['Pidgin', 'pidgin', 'pidgin.im', 'pidgin.gpg']
Moovida = ['Moovida', 'moovida', 'www.moovida.com', 'moovida.gpg']
Galaxium = ['Galaxium', 'galaxium', 'code.google.com/p/galaxium/', 'galaxium.gpg']
Swiftweasel = ['Swiftweasel', 'swiftweasel', 'swiftweasel.tuxfamily.org', '']
Medibuntu = ['Medibuntu', 'medibuntu', 'www.medibuntu.org', 'medibuntu.gpg']
WineDoors = ['Wine Doors', 'wine-doors', 'www.wine-doors.org', 'wine-doors.gpg']
XBMC = ['XBMC', 'xbmc', 'xbmc.org', 'xbmc.gpg']
UbuntuX = ['Ubuntu X', 'ubuntu-x', 'launchpad.net/~ubuntu-x-swat', 'ubuntu-x.gpg']

SOURCES_DATA = [
    ['http://ppa.launchpad.net/reacocard-awn/ppa/ubuntu/', ['hardy','intrepid'], 'main', AWN],
    ['http://ppa.launchpad.net/awn-testing/ppa/ubuntu', ['hardy','intrepid', 'jaunty', 'karmic'], 'main', AWN_TESTING],
    ['http://ppa.launchpad.net/project-neon/ppa/ubuntu/', ['hardy', 'intrepid'], 'main', Amarok],
    ['http://ppa.launchpad.net/amule-releases/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', AmuleRelease],
    ['http://ppa.launchpad.net/blueman/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Blueman],
    ['http://le-web.org/repository', 'stable', 'main', Backintime],
    ['http://archive.ubuntu.org.cn/ubuntu-cn/', ['hardy', 'intrepid'], 'main restricted universe multiverse', Ubuntu_cn],
    ['http://ppa.launchpad.net/openoffice-pkgs/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', OpenOffice],
    ['http://ppa.launchpad.net/globalmenu-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GlobalMenu],
    ['http://ppa.launchpad.net/markuz/ppa/ubuntu', ['jaunty'], 'main', Christine],
    ['http://ppa.launchpad.net/chromium-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', ChromiumBrowser],
    ['http://ppa.launchpad.net/specto/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Specto],
#    ['http://getdeb.masio.com.mx/', ['hardy', 'intrepid', 'jaunty'], '', GetDeb],
    ['http://ppa.launchpad.net/gnome-colors-packagers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', GnomeColors],
    ['http://ppa.launchpad.net/gtg/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', GettingThingsGnome],
    ['http://ppa.launchpad.net/geany-dev/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Geany],
    ['http://ppa.launchpad.net/gnote/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gnote],
    ['http://ppa.launchpad.net/telepathy/ppa/ubuntu', ['jaunty', 'karmic'], 'main', Empathy],
    ['http://deb.opera.com/opera/', 'lenny', 'non-free', Opera],
    ['http://ppa.launchpad.net/firerabbit/ppa/ubuntu', ['intrepid','jaunty'], 'main', Synapse],
    ['http://download.skype.com/linux/repos/debian', 'stable', 'non-free', Skype],
    ['http://ppa.launchpad.net/rvm/smplayer/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Smplayer],
    ['http://ppa.launchpad.net/rvm/testing/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Smplayer_Testing],
    ['http://ppa.launchpad.net/rvm/libs/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', MplayerLibs],
    ['http://ppa.launchpad.net/gwibber-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Gwibber],
    ['http://ppa.launchpad.net/matthaeus123/mrw-gimp-svn/ubuntu', ['jaunty', 'karmic'], 'main', Gimp_Testing], 
    ['http://ppa.launchpad.net/gwibber-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gwibber_Daily],
    ['http://ppa.launchpad.net/gmchess/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Gmchess],
    ['http://playonlinux.botux.net/', 'hardy', 'main', PlayOnLinux],
    ['http://ppa.launchpad.net/webkit-team/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', WebKitGtk],
    ['http://ppa.launchpad.net/midori/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Midori],
    ['http://ppa.launchpad.net/liferea/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Liferea],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-intrepid/ubuntu', 'intrepid', 'main', IBus_Intrepid],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-jaunty/ubuntu', 'jaunty', 'main', IBus_Jaunty],
    ['http://ppa.launchpad.net/ibus-dev/ibus-1.2-karmic/ubuntu', 'karmic', 'main', IBus_Karmic],
    ['http://ppa.launchpad.net/ibus-dev/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', IBus],
    ['http://ppa.launchpad.net/ubuntu-mozilla-daily/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Firefox],
    ['http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', MozillaSecurity],
    ['http://ppa.launchpad.net/compiz/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', CompizFusion],
    ['http://ppa.launchpad.net/pidgin-developers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Pidgin],
    ['http://ppa.launchpad.net/moovida-packagers/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Moovida],
    ['http://repository.cairo-dock.org/ubuntu', ['hardy', 'intrepid'], 'cairo-dock', CairoDock],
    ['http://ppa.launchpad.net/do-core/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', GnomeDo],
    ['http://ppa.launchpad.net/banshee-team/ppa/ubuntu', ['hardy', 'intrepid'], 'main', Banshee_Stable],
    ['http://ppa.launchpad.net/banshee-unstable-team/ppa/ubuntu', ['hardy', 'intrepid', 'karmic'], 'main', Banshee_Unstable],
    ['http://dl.google.com/linux/deb/', 'stable', 'non-free', Google],
    ['http://dl.google.com/linux/deb/', 'testing', 'non-free', Google_Testing],
    ['http://ppa.launchpad.net/googlegadgets/ppa/ubuntu', 'hardy', 'main', GoogleGadgets],
    ['http://ppa.launchpad.net/lidaobing/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/hardy/ubuntu', 'hardy', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/intrepid/ubuntu', 'intrepid', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/jaunty/ubuntu', 'jaunty', 'main', ChmSee],
    ['http://ppa.launchpad.net/chmsee/karmic/ubuntu', 'karmic', 'main', ChmSee],
    ['http://ppa.launchpad.net/kubuntu-members-kde4/ppa/ubuntu', ['hardy', 'intrepid'], 'main', KDE4],
    ['http://linux.getdropbox.com/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', NautilusDropbox],
    ['http://ppa.launchpad.net/tualatrix/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', UbuntuTweak],
    ['http://ppa.launchpad.net/ubuntu-tweak-testing/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', UbuntuTweakTesting],
    ['http://ppa.launchpad.net/adrian5632/ppa/ubuntu', ['hardy', 'intrepid'], 'main', UbuDSL],
    ['http://ppa.launchpad.net/gilir/ppa/ubuntu', ['hardy', 'intrepid'], 'main', Screenlets],
    ['http://wine.budgetdedicated.com/apt', ['hardy', 'intrepid', 'jaunty'], 'main', Wine],
    ['http://ppa.launchpad.net/lxde/ppa/ubuntu', 'hardy', 'main', LXDE],
    ['http://ppa.launchpad.net/gnome-terminator/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Terminator],
    ['http://ppa.launchpad.net/transmissionbt/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Stable],
    ['http://ppa.launchpad.net/transmissionbt-beta/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Beta],
    ['http://ppa.launchpad.net/transmissionbt-nightly/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', Transmission_Nightly],
    ['http://download.virtualbox.org/virtualbox/debian', ['hardy', 'intrepid', 'jaunty'], 'non-free', VirtualBox],
    ['http://ppa.launchpad.net/debfx/virtualbox/ubuntu', ['intrepid', 'jaunty'], 'main', VirtualBoxOse],
    ['http://ppa.launchpad.net/c-korn/vlc/ubuntu', ['jaunty'], 'main', Vlc],
    ['http://ppa.launchpad.net/shutter/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'main', Shutter],
    ['http://ppa.launchpad.net/galaxium/ppa/ubuntu', ['intrepid', 'jaunty'], 'main', Galaxium],
    ['http://download.tuxfamily.org/swiftweasel', ['hardy', 'intrepid'], 'multiverse', Swiftweasel],
    ['http://packages.medibuntu.org/', ['hardy', 'intrepid', 'jaunty', 'karmic'], 'free non-free', Medibuntu],
    ['http://ppa.launchpad.net/wine-doors-dev-team/ppa/ubuntu', 'intrepid', 'main', WineDoors],
    ['http://ppa.launchpad.net/team-xbmc/ppa/ubuntu', ['hardy', 'intrepid', 'jaunty'], 'main', XBMC],
    ['http://ppa.launchpad.net/gnome-games-experimental/ppa/ubuntu', ['jaunty', 'karmic'], 'main', GnomeGames],
    ['http://ppa.launchpad.net/ubuntu-x-swat/x-updates/ubuntu', ['jaunty', 'karmic'], 'main', UbuntuX],
]

SOURCES_DEPENDENCIES = {
    Midori[0]: WebKitGtk[0],
    Liferea[0]: WebKitGtk[0],
    Smplayer_Testing[0]: MplayerLibs[0],
}

SOURCES_CONFLICTS = {
    Skype[0]: Medibuntu[0],
}

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
            title=_('The information about available software is out-of-date'))

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
        self.model.set_sort_column_id(COLUMN_NAME, gtk.SORT_ASCENDING)
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
            logo = get_source_logo(package)
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

    def get_sourcelist_status(self, url):
        for source in self.get_sourceslist():
            if url in source.str() and source.type == 'deb':
                return not source.disabled
        return False

    def on_enable_toggled(self, cell, path):
        iter = self.model.get_iter((int(path),))

        name = self.model.get_value(iter, COLUMN_NAME)
        enabled = self.model.get_value(iter, COLUMN_ENABLED)

        if enabled is False and name in SOURCES_DEPENDENCIES:
            #FIXME: If more than one dependency
            dependency = SOURCES_DEPENDENCIES[name]
            if self.get_source_enabled(dependency) is False:
                dialog = QuestionDialog(\
                            _('To enable this Source, You need to enable "%s" at first.\nDo you wish to continue?') \
                            % dependency,
                            title=_('Dependency Notice'))
                if dialog.run() == gtk.RESPONSE_YES:
                    self.set_source_enabled(dependency)
                    self.set_source_enabled(name)
                else:
                    self.model.set(iter, COLUMN_ENABLED, enabled)

                dialog.destroy()
            else:
                self.do_source_enable(iter, not enabled)
        elif enabled and name in SOURCES_DEPENDENCIES.values():
            HAVE_REVERSE_DEPENDENCY = False
            for k, v in SOURCES_DEPENDENCIES.items():
                if v == name and self.get_source_enabled(k):
                    ErrorDialog(_('You can\'t disable this Source because "%(SOURCE)s" depends on it.\nTo continue you need to disable "%(SOURCE)s" first.') % {'SOURCE': k}).launch()
                    HAVE_REVERSE_DEPENDENCY = True
                    break
            if HAVE_REVERSE_DEPENDENCY:
                self.model.set(iter, COLUMN_ENABLED, enabled)
            else:
                self.do_source_enable(iter, not enabled)
        elif not enabled and name in SOURCES_CONFLICTS.values() or name in SOURCES_CONFLICTS.keys():
            key = None
            if name in SOURCES_CONFLICTS.keys():
                key = SOURCES_CONFLICTS[name]
            if name in SOURCES_CONFLICTS.values():
                for k, v in SOURCES_CONFLICTS.items():
                    if v == name:
                        key = k
            if self.get_source_enabled(key):
                ErrorDialog(_('You can\'t enable this Source because "%(SOURCE)s" conflicts with it.\nTo continue you need to disable "%(SOURCE)s" first.') % {'SOURCE': key}).launch()
                self.model.set(iter, COLUMN_ENABLED, enabled)
            else:
                self.do_source_enable(iter, not enabled)
        else:
            self.do_source_enable(iter, not enabled)

    def on_source_foreach(self, model, path, iter, name):
        m_name = model.get_value(iter, COLUMN_NAME)
        if m_name == name:
            if self._foreach_mode == 'get':
                self._foreach_take = model.get_value(iter, COLUMN_ENABLED)
            elif self._foreach_mode == 'set':
                self._foreach_take = iter

    def get_source_enabled(self, name):
        '''
        Search source by name, then get status from model
        '''
        self._foreach_mode = 'get'
        self._foreach_take = None
        self.model.foreach(self.on_source_foreach, name)
        return self._foreach_take

    def set_source_enabled(self, name):
        '''
        Search source by name, then call do_source_enable
        '''
        self._foreach_mode = 'set'
        self._foreach_status = None
        self.model.foreach(self.on_source_foreach, name)
        self.do_source_enable(self._foreach_take, True)

    def do_source_enable(self, iter, enable):
        '''
        Do the really source enable or disable action by iter
        Only emmit signal when source is changed
        '''

        url = self.model.get_value(iter, COLUMN_URL)
        distro = self.model.get_value(iter, COLUMN_DISTRO)
        name = self.model.get_value(iter, COLUMN_NAME)
        comps = self.model.get_value(iter, COLUMN_COMPS)
        key = self.model.get_value(iter, COLUMN_KEY)

        pre_status = self.get_sourcelist_status(url)

        if key:
            proxy.add_apt_key(key)

        if comps:
            result = proxy.set_entry(url, distro, comps, name, enable)
        else:
            result = proxy.set_entry(url, distro + '/', comps, name, enable)

        if str(result) == 'enabled':
            self.model.set(iter, COLUMN_ENABLED, True)
        else:
            self.model.set(iter, COLUMN_ENABLED, False)

        if pre_status != enable:
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
                url_section = url.split('/')
                url = 'https://launchpad.net/~%s/+archive/%s' % (url_section[3], url_section[4]) 
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
                _('After every release of Ubuntu there comes a feature freeze.\nThis means only applications with bug-fixes get into the repository.\nBy using third-party DEB repositories, you can always keep up-to-date with the latest version.\nAfter adding these repositories, locate and install them using Add/Remove.'))

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

        #FIXME close it when 0.5.0
        gobject.idle_add(self.check_ppa_entry)

    def check_ppa_entry(self):
        if self.do_check_ppa_entry():
            dialog = QuestionDialog(_('Some of your PPA Sources need to be updated.\nDo you wish to continue?'), title=_('PPA Sources has expired'))
            UPDATE = False
            if dialog.run() == gtk.RESPONSE_YES:
                UPDATE = True
            dialog.destroy()

            if UPDATE:
                self.do_update_ppa_entry()

    def do_check_ppa_entry(self):
        content = open(SOURCES_LIST).read()
        for line in content.split('\n'):
            if self.__is_expire_ppa(line):
                return True
        return False

    def __is_expire_ppa(self, line):
        '''http://ppa.launchpad.net/tualatrix/ppa/ubuntu is the new style
        http://ppa.launchpad.net/tualatrix/ubuntu is the old style
        length check is important
        '''
        try:
            url = line.split()[1]
            if url.startswith('http://ppa.launchpad.net') and \
                    len(url.split('/')) == 5 and \
                    'ppa/ubuntu' not in line:
                return True
        except:
            pass

    def do_update_ppa_entry(self):
        content = open(SOURCES_LIST).read()
        lines = []
        for line in content.split('\n'):
            if self.__is_expire_ppa(line):
                lines.append(line.replace('/ubuntu ', '/ppa/ubuntu '))
            else:
                lines.append(line)

        if proxy.edit_file(SOURCES_LIST, '\n'.join(lines)) == 'error':
            ErrorDialog(_('Please check the permission of the sources.list file'),
                    title=_('Save failed!')).launch()
        else:
            InfoDialog(_('Update Successful!')).launch()

        self.update_thirdparty()

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
                        'Please be careful and use only sources you trust.'),
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

        proxy.set_list_state('normal')
        widget.set_sensitive(False)

        dialog = QuestionDialog(_('You can install the new applications through Add/Remove.\nDo you want to go now?'),
            title = _('The software information is up-to-date now'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.emit('update', 'installer', 'deep_update')
            self.emit('call', 'mainwindow', 'select_module', {'name': 'installer'})
        else:
            self.emit('update', 'installer', 'deep_update')
        dialog.destroy()

if __name__ == '__main__':
    from utility import Test
    Test(ThirdSoft)
