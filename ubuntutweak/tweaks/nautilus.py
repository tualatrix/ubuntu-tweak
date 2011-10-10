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

from gi.repository import GObject, Gio

from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.gui.containers import ListPack, TablePack


class Nautilus(TweakModule):
    __title__ = _('Nautilus Settings')
    __desc__ = _('Manage the default file manager')
    __icon__ = ['file-manager', 'nautilus']
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        box = ListPack(_("File Browser"), (
                  WidgetFactory.create("CheckButton",
                                       label=_('Show advanced permissions in the Nautilus "File Properties" window'),
                                       enable_reset=True,
                                       key="org.gnome.nautilus.preferences.show-advanced-permissions",
                                       backend="gsettings"),
                  WidgetFactory.create("CheckButton",
                                       label=_('Always use the location entry, instead of the pathbar'),
                                       enable_reset=True,
                                       key="org.gnome.nautilus.preferences.always-use-location-entry",
                                       backend="gsettings")))
        self.add_start(box, False, False, 0)

        box = TablePack(_('Thumbnail Settings'), (
                    WidgetFactory.create('SpinButton',
                                         key='org.gnome.nautilus.icon-view.thumbnail-size',
                                         enable_reset=True,
                                         min=16, max=512, step=16,
                                         label=_('Default thumbnail icon size (pixels)'),
                                         backend="gsettings"),
                    WidgetFactory.create('SpinButton',
                                         key='org.gnome.desktop.thumbnail-cache.maximum-size',
                                         enable_reset=True,
                                         min=-1, max=512, step=1,
                                         label=_('Maximum thumbnail cache size (megabytes)'),
                                         backend="gsettings"),
                    WidgetFactory.create('SpinButton',
                                          key='org.gnome.desktop.thumbnail-cache.maximum-age',
                                          enable_reset=True,
                                          min=-1, max=180, step=1,
                                          label=_('Thumbnail cache time (days)'),
                                          backend="gsettings"),
            ))
        self.add_start(box, False, False, 0)

        box = TablePack(_('Automatically Mount Settings'), (
                    WidgetFactory.create('CheckButton',
                                         key='org.gnome.desktop.media-handling.automount',
                                         enable_reset=True,
                                         label=_('Whether to automatically mount media'),
                                         backend="gsettings"),
                    WidgetFactory.create('CheckButton',
                                         key='org.gnome.desktop.media-handling.automount-open',
                                         enable_reset=True,
                                         label=_('Whether to automatically open a folder for automounted media'),
                                         backend="gsettings"),
                    WidgetFactory.create('CheckButton',
                                          key='org.gnome.desktop.media-handling.autorun-never',
                                          enable_reset=True,
                                          label=_('Never prompt or autorun/autostart programs when media are inserted'),
                                          backend="gsettings"),
            ))
        self.add_start(box, False, False, 0)
