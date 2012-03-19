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

from gi.repository import Gtk, Gio

from ubuntutweak.gui.containers import ListPack, TablePack, GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class Fonts(TweakModule):
    __title__ = _('Fonts')
    __desc__ = _('Fonts Settings')
    __icon__ = 'font-x-generic'
    __category__ = 'appearance'

    """Lock down some function"""
    def __init__(self):
        TweakModule.__init__(self)
        fb = Gtk.FontButton()
        fb.set_font_name('Monospace 24')
        fb.set_show_size(False)
        fb.set_use_size(13)

        box = GridPack(
                    WidgetFactory.create("Scale",
                        label=_("Text scaling factor:"),
                        key="org.gnome.desktop.interface.text-scaling-factor",
                        min=0.5,
                        max=3.0,
                        digits=1,
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Default font:"),
                        key="org.gnome.desktop.interface.font-name",
                        backend="gsettings",
                        default="Ubuntu 11",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Desktop font:"),
                        key="org.gnome.nautilus.desktop.font",
                        backend="gsettings",
                        default="Ubuntu 11",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Monospace font:"),
                        key="org.gnome.desktop.interface.monospace-font-name",
                        backend="gsettings",
                        default="Ubuntu Mono 13",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Document font:"),
                        key="org.gnome.desktop.interface.document-font-name",
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Window title bar font:"),
                        key="/apps/metacity/general/titlebar_font",
                        backend="gconf",
                        default='Ubuntu Bold 11',
                        enable_reset=True),
                    Gtk.Separator(),
                    WidgetFactory.create("ComboBox",
                        label=_("Hinting:"),
                        key="org.gnome.settings-daemon.plugins.xsettings.hinting",
                        values=('none', 'slight', 'medium', 'full'),
                        texts=(_('No hinting'),
                               _('Basic'),
                               _('Moderate'),
                               _('Maximum')),
                        default='slight',
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("ComboBox",
                        label=_("Antialiasing:"),
                        key="org.gnome.settings-daemon.plugins.xsettings.antialiasing",
                        values=('none', 'grayscale', 'rgba'),
                        texts=(_('No antialiasing'),
                               _('Standard grayscale antialiasing'),
                               _('Subpixel antialiasing (LCD screens only)')), 
                        default='rgba',
                        backend="gsettings",
                        enable_reset=True),
            )

        self.add_start(box, False, False, 0)
