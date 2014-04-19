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

from gi.repository import GObject, Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.gui.containers import GridPack


class Nautilus(TweakModule):
    __title__ = _('File Manager')
    __desc__ = _('Manage the Nautilus file manager')
    __icon__ = ['file-manager', 'nautilus']
    __category__ = 'system'
    __desktop__ = ['ubuntu', 'ubuntu-2d', 'gnome', 'gnome-classic', 'gnome-shell', 'gnome-fallback', 'gnome-fallback-compiz']

    utext_pathbar = _('Use the location entry instead of the pathbar')
    recursive_search = _('Enable Recursive Search')
    utext_automount = _('Automatically mount media:')
    utext_open = _('Automatically open a folder:')
    utext_prompt = _('Prompt or autorun/autostart programs:')
    utext_thumbnail_icon_size = _('Thumbnail icon size (pixels):')
    utext_thumbnail_cache_age = _('Thumbnail cache time (days):')
    utext_thumbnail_cache_size = _('Maximum thumbnail cache size (MB):')

    def __init__(self):
        TweakModule.__init__(self)

        box = GridPack(
                    WidgetFactory.create("Switch",
                        label=self.utext_pathbar,
                        enable_reset=True,
                        key="org.gnome.nautilus.preferences.always-use-location-entry",
                        backend="gsettings"),
                    WidgetFactory.create('Switch',
                        key='org.gnome.nautilus.preferences.enable-interactive-search',
                        enable_reset=True,
                        reverse=True,
                        label=self.recursive_search,
                        backend="gsettings"),
                    WidgetFactory.create('Switch',
                        key='org.gnome.desktop.media-handling.automount',
                        enable_reset=True,
                        label=self.utext_automount,
                        backend="gsettings"),
                    WidgetFactory.create('Switch',
                        key='org.gnome.desktop.media-handling.automount-open',
                        enable_reset=True,
                        label=self.utext_open,
                        backend="gsettings"),
                    WidgetFactory.create('Switch',
                        key='org.gnome.desktop.media-handling.autorun-never',
                        enable_reset=True,
                        reverse=True,
                        label=self.utext_prompt,
                        backend="gsettings"),
                    Gtk.Separator(),
                    WidgetFactory.create('Scale',
                        key='org.gnome.nautilus.icon-view.thumbnail-size',
                        enable_reset=True,
                        min=16, max=512,
                        step=16,
                        label=self.utext_thumbnail_icon_size,
                        backend="gsettings"),
                    WidgetFactory.create('Scale',
                        key='org.gnome.desktop.thumbnail-cache.maximum-age',
                        enable_reset=True,
                        min=-1, max=180,
                        step=1,
                        label=self.utext_thumbnail_cache_age,
                        backend="gsettings"),
                    WidgetFactory.create('Scale',
                        key='org.gnome.desktop.thumbnail-cache.maximum-size',
                        enable_reset=True,
                        min=-1, max=512,
                        step=1,
                        label=self.utext_thumbnail_cache_size,
                        backend="gsettings"),
        )
        self.add_start(box, False, False, 0)
