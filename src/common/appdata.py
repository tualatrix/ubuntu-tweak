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
from consts import *

__all__ = (
    'get_app_describ',
    'get_source_describ',
    'get_app_logo',
    'get_source_logo',
)

def get_app_describ(name):
    name = name.replace(' ', '-').lower()
    try:
        desc = APP_DATA[name]
    except KeyError:
        desc = 'Unknown Error'

    return desc

def get_source_describ(name):
    name = name.replace(' ', '-').lower()
    try:
        desc = SOURCE_DATA[name]
    except KeyError:
        desc = get_app_describ(name)

    return desc

def get_app_logo(name):
    try:
        name = '%s.png' % name.replace(' ', '-').lower()
        path = os.path.join(DATA_DIR, 'applogos', name)

        return gtk.gdk.pixbuf_new_from_file(path)
    except:
        icon = gtk.icon_theme_get_default()
        return icon.load_icon(gtk.STOCK_MISSING_IMAGE, 32, 0)

def get_source_logo(name):
    return get_app_logo(name)

APP_DATA = {
    'agave': _('A color scheme designer'),
    'amarok-nightly': _('Development version of an audio player for KDE'),
    'amule': _('Client for the eD2k and Kad networks'),
    'anjuta': _('GNOME IDE for C/C++, Java, Python'),
    'audacious': _('A skinned multimedia player for many platforms'),
    'audacity': _('Record and edit audio files'),
    'avant-window-navigator': _('Fully customisable dock-like window navigator'),
    'avant-window-navigator-trunk': _('Fully customisable dock-like window navigator(Unstable)'),
    'avidemux': _('A free video editor'),
    'azureus': _('BitTorrent client written in Java'),
    'banshee': _('Audio Management and Playback application'),
    'blueman': _('GTK+ Bluetooth Manager'),
    'backintime-gnome': _('Simple backup system for GNOME Desktop'),
    'backintime-kde4': _('Simple backup system for KDE4 Desktop'),
    'cairo-dock': _('A true dock for linux'),
    'chmsee': _('A chm file viewer written in GTK+'),
    'christine': _('Desired to be small and fast, christine is a simple media player, that let you play your favorite music and videos from one single application.'),
    'chromium-browser': _('Chromium is an open-source browser project that aims to build a safer, faster, and more stable way for all Internet users to experience the web.'),
    'codeblocks': _('The open source, cross-platform IDE'),
    'compizconfig-settings-manager': _('Advanced Desktop Effects Settings Manager'),
    'devhelp': _('An API documentation browser for GNOME.'),
    'deluge-torrent': _('A Bittorrent client written in PyGTK'),
    'nautilus-dropbox': _('Store, Sync and Share your files online.'),
    'eclipse': _('Extensible Tool Platform and Java IDE'),
    'eioffice-personal': _('EIOffice Personal 2009. Free for Chinese users. See http://www.evermoresw.com.'),
    'emesene': _('A client for the Windows Live Message network'),
    'empathy': _('Empathy consists of a rich set of reusable instant messaging widgets, and a GNOME client using those widgets.'),
    'exaile': _('GTK+ based flexible audio player, similar to Amarok'),
    'filezilla': _('File transmission via ftp, sftp and ftps'),
    'pcmanfm': _('An extremly fast and lightweight file manager'),
    'galaxium': _('Galaxium is an instant messenger application designed for the GNOME desktop'),
    'gajim': _('A GTK+ jabber client'),
    'geany': _('A fast and lightweight IDE'),
    'gftp': _('A multithreaded FTP client'),
    'ghex': _('GNOME Hex editor'),
    'gimp': _('The GNU Image Manipulation Program'),
    'gmail-notify': _('Notifies the user upon arrival of new mail in Gmail'),
    'gmchess': _('GMChess is chinese chess game write by gtkmm'),
    'gnome-do': _('A powerful, speedy, and sexy remote control for the GNOME Desktop'),
    'gnome-globalmenu': _('Global Menu Bar for GNOME'),
    'gnome-colors': _('the GNOME-Colors Icon Themes and Shiki-Colors GTK+/Metacity Themes for Debian and Ubuntu.'),
    'gnote': _('a C++ port of Tomboy'),
    'googleearth': _("A program that combines satellite imagery and maps to put the world's geographic information at your fingertips."),
    'google-gadgets': _('Platform for running Google Gadgets on Linux'),
    'google-chrome-unstable': _('Google Chrome is a browser that combines a minimal design with sophisticated technology to make the web faster, safer, and easier.'),
    'gparted': _('GNOME partition editor'),
    'gpicview': _('Lightweight image viewer'),
    'gtk-recordmydesktop': _('Graphical frontend for recordmydesktop'),
    'gtg': _('GTG is a personal organizer for the GNOME desktop environment, it focuses on ease of use and flexibility, while keeping things simple.'),
    'gwibber': _('Gwibber is an open source microblogging client for GNOME'),
    'isomaster': _('A graphical CD image editor'),
    'ibus': _('Intelligent Input Bus for Linux / Unix OS'),
    'ibus-pinyin': _('It is a PinYin engine for IBus.'),
    'ibus-table': _('IBus-Table is the IM Engine framework for table-based input methods, such as ZhengMa, WuBi, ErBi, ChangJie and so on.'),
    'inkscape': _('Create and edit Scalable Vector Graphics images'),
    'kino': _('Non-linear editor for Digital Video data'),
    'lastfm': _('A music player for Last.fm personalized radio'),
    'leafpad': _('GTK+ based simple text editor'),
    'liferea': _('Feed aggregator for GNOME'),
    'mail-notification': _('Mail notification in system tray'),
    'meld': _('Adcal tool to diff and merge files'),
    'mirage': _('A fast and simple GTK+ Image Viewer'),
    'miro': _('Open internet TV, beyond anything else'),
    'midori': _('Webkit based lightweight web browser'),
    'moovida': _('The free media player - play all your files'),
    'monodevelop': _('An IDE to Develop .NET applications.'),
    'mplayer': _('The Ultimate Movie Player For Linux'),
    'netbeans': _('IDE for Java, C/C++, Ruby, UML, etc.'),
    'opera': _('The Opera Web Browser'),
    'pidgin': _('Pidgin is a graphical modular messaging client based on libpurple which is capable of connecting to AIM, MSN, Yahoo!, XMPP, ICQ, IRC, SILC, SIP/SIMPLE, Novell GroupWise, Lotus Sametime, Bonjour, Zephyr, MySpaceIM, Gadu-Gadu, and QQ all at once.'),
    'playonlinux': _('Run your Windows programs on Linux'),
    'picasa': _('Image management application from Google'),
    'screenlets': _('A framework for desktop widgets'),
    'shutter': _('Feature-rich screenshot application(formerly known as GScrot)'),
    'skype': _('Make audio/video calls using this VoIP Software'),
    'smplayer': _('A great MPlayer front-end, written in QT4'),
    'soundconverter': _('Convert audio files into other formats'),
    'spicebird': _('A fully integrated mail, PIM and instant messaging client'),
    'stardict': _('An international dictionary'),
    'swiftweasel': _('Swiftweasel is an optimized build of the Mozilla Firefox web browser for Linux'),
    'specto': _('A desktop application that will watch for events (website updates, emails, file and folder changes...)'),
    'synapse': _('An instant messaging application powered by qt-mono-bindings'),
    'tasque': _('A Useful Task List'),
    'terminator': _('Multiple GNOME terminals in one window'),
    'transmission-gtk': _('Transmission is a fast, easy, and free multi-platform BitTorrent client.'),
    'ubuntu-tweak': _('Ubuntu Tweak makes it easier to configure Ubuntu'),
    'ubuntu-restricted-extras': _('Commonly used restricted packages'),
    'ubudsl': _('configure your USB ADSL modem and connection easier than ever!'),
    'virtualbox': _('A feature rich, high performance virtualization software'),
    'virtualbox-3.0': _('A feature rich, high performance virtualization software'),
    'virtualbox-ose': _('A feature rich, high performance virtualization software'),
    'vlc': _('Read, capture, broadcast your multimedia streams'),
    'vmware-player': _('Run Virtual Machines using VMware'),
    'wine': _('A compatibility layer for running Windows programs'),
    'wine-doors': _('Wine-doors is an application designed to make installing windows software on Linux, Solaris or other Unix systems easier.'),
    'xbmc': _('XBMC is a free and open source software media player and entertainment hub'),
}

SOURCE_DATA = {
    'firefox': _('Development Version of Mozilla Firefox'),
    'compiz-fusion': _('Development version of Compiz Fusion'),
    'google': _("Google's Linux Repository"),
    'kde-4': _('Development Version of K Desktop Environment'),
    'lxde': _('Lightweight X11 Desktop Environment: GPicView, PCManFM'),
    'webkitgtk': _('WebkitGtk+, Liferea (Webkit), Midori and other WebKit related projects.'),
    'medibuntu': _('Multimedia, Entertainment and Distraction In Ubuntu\nMedibuntu is a repository of packages that cannot be included into the Ubuntu distribution for legal reasons (copyright, license, patent, etc).'),
    'openoffice': 'OpenOffice.org 3.1 for Ubuntu',
    'ubuntu-cn': _('Ubuntu repository for Chinese users.\n'
        'Including EIOffice, Ubuntu Tweak, ibus input method, OpenOffice.org 3.0 and other softwares.'),
    'getdeb': _('GetDeb extends the existing software options for Ubuntu (and derived) Linux distributions by providing major updates and software not yet available on the official Ubuntu repositories.'),
    'ubuntu-x': _('Updated versions of X.org drivers, libraries, etc. for Ubuntu.'),
    'gnome-games': _('Gnome Games built from Git, with all experimental features and staging games enabled.'),
    'mozilla-security': _('Ubuntu Mozilla Security Team provides beta and final stable/security updates for mozilla software in its PPA'),
}

if __name__ == '__main__':
    print get_app_describ('Avant Window Navigator')
    print get_app_describ('Banshee')
    print get_source_describ('wine')
