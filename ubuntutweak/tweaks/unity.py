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

import os
import re
import logging

from gi.repository import GObject, Gtk, Gio, GdkPixbuf

from ubuntutweak import system
from ubuntutweak.utils import icon
from ubuntutweak.gui.containers import ListPack, GridPack, SinglePack
from ubuntutweak.gui.treeviews import get_local_path
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.settings.compizsettings import CompizPlugin, CompizSetting

log = logging.getLogger('Unity')


class EdgeComboBox(Gtk.ComboBox):
    edge_settings = (
        ('expo', 'expo_edge', _('Show Workspaces')),
        ('scale', 'initiate_all_edge', _('Show Windows')),
        ('core', 'show_desktop_edge', _('Show Desktop')),
        ('widget', 'toggle_edge', _('Show Widgets')),
    )

    __gsignals__ = {
        'edge_changed': (GObject.SignalFlags.RUN_FIRST,
                         None,
                         (GObject.TYPE_STRING,))
    }

    (COLUMN_PLUGIN,
     COLUMN_KEY,
     COLUMN_TEXT) = range(3)

    edge = GObject.property(type=str, default='')
    old_plugin = GObject.property(type=str, default='')
    old_key = GObject.property(type=str, default='')
    max_index = GObject.property(type=int, default=0)

    def __init__(self, edge):
        '''
        edge will be: TopLeft, BottomLeft
        '''
        GObject.GObject.__init__(self)

        model = Gtk.ListStore(GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)
        renderer = Gtk.CellRendererText()
        self.pack_start(renderer, False)
        self.add_attribute(renderer, 'text', self.COLUMN_TEXT)
        self.set_model(model)

        self.edge = edge
        enable = False
        count = 0

        for name, key, text in self.edge_settings:
            if CompizPlugin.is_available(name, key):
                model.append((name, key, text))

                setting = CompizSetting("%s.%s" % (name, key))
                log.debug("CompizSetting: %s, value: %s, key: %s" % \
                        (name, setting.get_value(), edge))

                if setting.get_value() == edge:
                    enable = True
                    self.old_plugin = name
                    self.old_key = key
                    self.set_active(count)
                    log.info("The %s is holding %s" % (edge, name))

                count = count + 1

        model.append(('', '', '-'))

        if not enable:
            self.set_active(count)
        self.max_index = count
        self.connect("changed", self.on_changed)

    def on_changed(self, widget):
        plugin = self.get_current_plugin()
        key = self.get_current_key()
        log.debug("ComboBox changed: from %s to %s" % (self.old_plugin, plugin))

        if self.old_plugin:
            for name, key, text in self.edge_settings:
                if name == self.old_plugin:
                    log.debug('%s has to unset (%s)' % (name, key))
                    setting = CompizSetting("%s.%s" % (name, key))
                    setting.set_value('')
                    break

        self.old_plugin = plugin
        self.old_key = key

        log.debug('%s changed to "%s"' % (widget.edge, plugin))
        self.emit('edge_changed', plugin)

    def set_to_none(self):
        self.handler_block_by_func(self.on_changed)
        log.debug("on_edge_changed: from %s to none" % self.get_current_plugin())
        self.set_active(self.max_index)
        self.handler_unblock_by_func(self.on_changed)

    def get_current_plugin(self):
        iter = self.get_active_iter()
        model = self.get_model()

        return model.get_value(iter, self.COLUMN_PLUGIN)

    def get_current_key(self):
        iter = self.get_active_iter()
        model = self.get_model()

        return model.get_value(iter, self.COLUMN_KEY)


class Unity(TweakModule):
    __title__ = _('Unity')
    __desc__ = _('Tweak the powerful Unity desktop')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']

    def __init__(self):
        TweakModule.__init__(self)

        version_pattern = re.compile('\d.\d+.\d')

        if system.DESKTOP == 'ubuntu':
            hbox = Gtk.HBox(spacing=12)
            hbox.pack_start(self.create_edge_setting(), True, False, 0)
            self.add_start(hbox, False, False, 0)

            settings_box = []
            grid_pack = GridPack(
                        Gtk.Separator(),
                        WidgetFactory.create("Switch",
                            label=_('HUD:'),
                            key="unityshell.show_hud",
                            on='<Alt>',
                            off='Disabled',
                            backend="compiz"),
                        WidgetFactory.create("Switch",
                            label=_('Shortcut hits overlay:'),
                            key="unityshell.shortcut_overlay",
                            backend="compiz"),
                        Gtk.Separator(),
                        WidgetFactory.create("Scale",
                            label=_('Launcher icon size:'),
                            key="unityshell.icon_size",
                            min=32,
                            max=64,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("Scale",
                            label=_('Launcher opacity:'),
                            key="unityshell.launcher_opacity",
                            min=0,
                            max=1,
                            digits=2,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("ComboBox",
                            label=_('Launcher hide mode:'),
                            key="unityshell.launcher_hide_mode",
                            texts=(_('Never'), _('Auto Hide')),
                            values=(0, 1),
                            type=int,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("ComboBox",
                            label=_('Launcher icon backlight:'),
                            key="unityshell.backlight_mode",
                            texts=(_('Backlight Always On'),
                                 _('Backlight Toggles'),
                                 _('Backlight Always Off'),
                                 _('Edge Illumination Toggles'),
                                 _('Backlight and Edge Illumination Toggles')),
                            values=(0, 1, 2, 3, 4),
                            type=int,
                            backend="compiz",
                            enable_reset=True),
                        WidgetFactory.create("ComboBox",
                            label=_('Launcher show devices:'),
                            key="unityshell.devices_option",
                            texts=(_('Never'),
                                   _('Only Mounted'),
                                   _('Always')),
                             values=(0, 1, 2),
                             type=int,
                             backend="compiz",
                             enable_reset=True),
                        Gtk.Separator(),
                        WidgetFactory.create("ComboBox",
                             label=_('Dash size:'),
                             key="com.canonical.Unity.form-factor",
                             texts=(_('Automatic'), _('Desktop'), _('Netbook')),
                             values=('Automatic', 'Desktop', 'Netbook'),
                             backend="gsettings",
                             enable_reset=True),
                        WidgetFactory.create("ColorButton",
                             label=_('Dash color:'),
                             key="unityshell.background_color",
                             backend="compiz",
                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                             label=_('Blur type:'),
                             key="unityshell.dash_blur_experimental",
                             texts=(_('No blur'),
                                    _('Static blur'),
                                    _('Active blur')),
                             values=(0, 1, 2),
                             type=int,
                             backend="compiz",
                             enable_reset=True),
                        WidgetFactory.create("Scale",
                             label=_('Panel opacity:'),
                             key="unityshell.panel_opacity",
                             min=0, max=1, digits=2,
                             backend="compiz",
                             enable_reset=True),
                )

            self.add_start(grid_pack, False, False, 0)
        else:
            super_key_button, super_key_reset = WidgetFactory.create("CheckButton",
                                             label=_('Enable the Super key'),
                                             key="com.canonical.Unity2d.Launcher.super-key-enable",
                                             backend="gsettings",
                                             enable_reset=True)
            box = GridPack(
                        WidgetFactory.create("Switch",
                                             label=_('Full screen dash'),
                                             key="com.canonical.Unity2d.Dash.full-screen",
                                             backend="gsettings",
                                             enable_reset=True),
                        (Gtk.Label(_("Launcher")), super_key_button, super_key_reset),
                        WidgetFactory.create("CheckButton",
                                             label=_('Only one launcher when multi-monitor'),
                                             key="com.canonical.Unity2d.Launcher.use-strut",
                                             backend="gsettings",
                                             enable_reset=True),
                        WidgetFactory.create("ComboBox",
                                             label=_('Launcher hide mode'),
                                             key="com.canonical.Unity2d.Launcher.hide-mode",
                                             texts=(_('Never'), _('Auto Hide'),
                                                    _('Intellihide')),
                                             values=(0, 1, 2),
                                             type=int,
                                             backend="gsettings",
                                             enable_reset=True),
                )

            self.add_start(box, False, False, 0)

    def create_edge_setting(self):
        hbox = Gtk.HBox(spacing=12)

        vbox = Gtk.VBox(spacing=6)
        hbox.pack_start(vbox, False, False, 0)

        self.TopLeft = EdgeComboBox("TopLeft")
        vbox.pack_start(self.TopLeft, False, False, 0)

        self.BottomLeft = EdgeComboBox("BottomLeft")
        vbox.pack_end(self.BottomLeft, False, False, 0)

        wallpaper = get_local_path(GSetting('org.gnome.desktop.background.picture-uri').get_value())

        if wallpaper:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper, 160, 100)
            except GObject.GError:
                pixbuf = icon.get_from_name('ubuntu-tweak', size=128)
        else:
            pixbuf = icon.get_from_name('ubuntu-tweak', size=128)

        image = Gtk.Image.new_from_pixbuf(pixbuf)
        hbox.pack_start(image, False, False, 0)

        vbox = Gtk.VBox(spacing=6)
        hbox.pack_start(vbox, False, False, 0)

        self.TopRight = EdgeComboBox("TopRight")
        vbox.pack_start(self.TopRight, False, False, 0)

        self.BottomRight = EdgeComboBox("BottomRight")
        vbox.pack_end(self.BottomRight, False, False, 0)

        for edge in ('TopLeft', 'TopRight', 'BottomLeft', 'BottomRight'):
            getattr(self, edge).connect('edge_changed', self.on_edge_changed)
        return hbox

    def on_edge_changed(self, widget, plugin):
        edges = ['TopLeft', 'TopRight', 'BottomLeft', 'BottomRight']
        edges.remove(widget.edge)

        if plugin:
            for edge in edges:
                edge_combobox = getattr(self, edge)

                if edge_combobox.get_current_plugin() == plugin:
                    edge_combobox.set_to_none()
                    break

            plugin = CompizPlugin(widget.get_current_plugin())
            plugin.set_enabled(True)
            setting = CompizSetting("%s.%s" % (plugin, widget.get_current_key()))
            setting.set_value(widget.edge)
