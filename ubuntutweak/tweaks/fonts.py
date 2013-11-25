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

from ubuntutweak import system
from ubuntutweak.gui.containers import ListPack, TablePack, GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class Fonts(TweakModule):
    __title__ = _('Fonts')
    __desc__ = _('Fonts Settings')
    __icon__ = 'font-x-generic'
    __category__ = 'appearance'
    __desktop__ = ['ubuntu', 'gnome-fallback', 'gnome', 'ubuntu-2d', 'gnome-classic', 'gnome-shell', 'gnome-fallback-compiz']

    utext_text_scaling = _("Text scaling factor:")
    utext_default_font = _("Default font:")
    utext_monospace_font = _("Monospace font:")
    utext_document_font = _("Document font:")
    utext_window_title_font = _("Window title bar font:")
    utext_hinting = _("Hinting:")
    utext_antialiasing = _("Antialiasing:")

    """Lock down some function"""
    def __init__(self):
        TweakModule.__init__(self)
        fb = Gtk.FontButton()
        fb.set_font_name('Monospace 24')
        fb.set_show_size(False)
        fb.set_use_size(13)

        if system.CODENAME == 'precise':
            window_font_label, window_font_button, window_font_reset_button = WidgetFactory.create("FontButton",
                       label=self.utext_window_title_font,
                       key="/apps/metacity/general/titlebar_font",
                       backend="gconf",
                       enable_reset=True)
        else:
            window_font_label, window_font_button, window_font_reset_button = WidgetFactory.create("FontButton",
                       label=self.utext_window_title_font,
                       key="org.gnome.desktop.wm.preferences.titlebar-font",
                       backend="gsettings",
                       enable_reset=True)

        box = GridPack(
                    WidgetFactory.create("Scale",
                        label=self.utext_text_scaling,
                        key="org.gnome.desktop.interface.text-scaling-factor",
                        min=0.5,
                        max=3.0,
                        step=0.1,
                        digits=1,
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=self.utext_default_font,
                        key="org.gnome.desktop.interface.font-name",
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=_("Desktop font:"),
                        key="org.gnome.nautilus.desktop.font",
                        backend="gsettings",
                        default="Ubuntu 11",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=self.utext_monospace_font,
                        key="org.gnome.desktop.interface.monospace-font-name",
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("FontButton",
                        label=self.utext_document_font,
                        key="org.gnome.desktop.interface.document-font-name",
                        backend="gsettings",
                        enable_reset=True),
                    (window_font_label, window_font_button, window_font_reset_button),
                    Gtk.Separator(),
                    WidgetFactory.create("ComboBox",
                        label=self.utext_hinting,
                        key="org.gnome.settings-daemon.plugins.xsettings.hinting",
                        values=('none', 'slight', 'medium', 'full'),
                        texts=(_('No hinting'),
                               _('Basic'),
                               _('Moderate'),
                               _('Maximum')),
                        backend="gsettings",
                        enable_reset=True),
                    WidgetFactory.create("ComboBox",
                        label=self.utext_antialiasing,
                        key="org.gnome.settings-daemon.plugins.xsettings.antialiasing",
                        values=('none', 'grayscale', 'rgba'),
                        texts=(_('No antialiasing'),
                               _('Standard grayscale antialiasing'),
                               _('Subpixel antialiasing (LCD screens only)')), 
                        backend="gsettings",
                        enable_reset=True),
            )

        self.add_start(box, False, False, 0)
