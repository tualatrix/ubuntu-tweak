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
import logging

import compizconfig
from gi.repository import GObject, Gtk, GdkPixbuf

from ubuntutweak.modules import TweakModule
from ubuntutweak.tweaks import ccm
from ubuntutweak.common.consts import DATA_DIR
from ubuntutweak.gui.treeviews import get_local_path
from ubuntutweak.gui.containers import ListPack, SinglePack
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.utils import icon

log = logging.getLogger('compiz')


class CompizPlugin:
    context = compizconfig.Context()

    def __init__(self, name):
        self._plugin = self.context.Plugins[name]

    @classmethod
    def set_plugin_active(cls, name, active):
        try:
            plugin = cls.context.Plugins[name]
            plugin.Enabled = int(active)
            cls.context.Write()
        except:
            pass

    @classmethod
    def get_plugin_active(cls, name):
        try:
            plugin = cls.context.Plugins[name]
            return bool(plugin.Enabled)
        except:
            return False

    def set_enabled(self, bool):
        self._plugin.Enabled = int(bool)
        self.save()

    def get_enabled(self):
        return self._plugin.Enabled

    def save(self):
        self.context.Write()

    def resolve_conflict(self):
        conflicts = self.get_enabled() and self._plugin.DisableConflicts or \
                                           self._plugin.EnableConflicts
        conflict = ccm.PluginConflict(self._plugin, conflicts)
        return conflict.Resolve()

    @classmethod
    def is_available(cls, name, setting):
        return cls.context.Plugins.has_key(name) and \
               cls.context.Plugins[name].Screen.has_key(setting)

    def create_setting(self, key, target):
        settings = self._plugin.Screen

        if type(settings) == list:
            return settings[0][key]
        else:
            return settings[key]


class CompizSetting:
    def __init__(self, plugin, key, target=''):
        self._plugin = plugin
        self._setting = self._plugin.create_setting(key, target)

    def set_value(self, value):
        self._setting.Value = value
        self._plugin.save()

    def get_value(self):
        return self._setting.Value

    def is_default_and_enabled(self):
        return self._setting.Value == self._setting.DefaultValue and \
                self._plugin.get_enabled()

    def reset(self):
        self._setting.Reset()
        self._plugin.save()


class OpacityMenu(Gtk.CheckButton):
    menu_match = 'Tooltip | Menu | PopupMenu | DropdownMenu'

    def __init__(self, label):
        GObject.GObject.__init__(self, label=label)

        try:
            self.plugin = CompizPlugin('obs')
        except KeyError, e:
            log.error(e)
            self.set_sensitive(False)
        else:
            if not self.plugin.get_enabled():
                self.plugin.set_enabled(True)
            self.setting_matches = CompizSetting(self.plugin, 'opacity_matches', target='Screens')
            self.setting_values = CompizSetting(self.plugin, 'opacity_values', target='Screens')

            if self.menu_match in self.setting_matches.get_value():
                self.set_active(True)

            self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            self.setting_matches.set_value([self.menu_match])
            self.setting_values.set_value([90])
        else:
            self.setting_matches.set_value([])
            self.setting_values.set_value([])


class WobblyMenu(Gtk.CheckButton):
    def __init__(self, label, mediator):
        GObject.GObject.__init__(self, label=label)

        self.mediator = mediator
        try:
            self.plugin = CompizPlugin('wobbly')
        except KeyError, e:
            log.error(e)
            self.set_sensitive(False)
        else:
            self.map_window_setting = CompizSetting(self.plugin, 'map_window_match', target='Screens')
            self.map_effect_setting = CompizSetting(self.plugin, 'map_effect', target='Screens')

            if self.map_window_setting.is_default_and_enabled() and self.map_effect_setting.get_value() == 1:
                self.set_active(True)

            self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.mediator.snap.set_active(False)
                self.plugin.set_enabled(True)
                self.map_window_setting.reset()
                self.map_effect_setting.set_value(1)
        else:
            self.map_window_setting.set_value("")
            self.map_effect_setting.set_value(0)

        if self.map_window_setting.is_default_and_enabled():
            self.set_active(True)
        else:
            self.set_active(False)


class WobblyWindow(Gtk.CheckButton):
    def __init__(self, label, mediator):
        GObject.GObject.__init__(self, label=label)

        self.mediator = mediator
        try:
            self.plugin = CompizPlugin('wobbly')
        except KeyError, e:
            log.error(e)
            self.set_sensitive(False)
        else:
            self.setting = CompizSetting(self.plugin, 'move_window_match', target='Screens')

            if self.setting.is_default_and_enabled():
                self.set_active(True)

            self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.mediator.snap.set_active(False)
                self.plugin.set_enabled(True)
                self.setting.reset()
        else:
            self.setting.set_value("")

        if self.setting.is_default_and_enabled():
            self.set_active(True)
        else:
            self.set_active(False)


class SnapWindow(Gtk.CheckButton):
    def __init__(self, label, mediator):
        GObject.GObject.__init__(self, label=label)

        self.mediator = mediator
        try:
            self.plugin = CompizPlugin('snap')
        except KeyError, e:
            log.error(e)
            self.set_sensitive(False)
        else:
            self.set_active(self.plugin.get_enabled())
            self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.plugin.set_enabled(True)
                self.mediator.wobbly_w.set_active(False)
                self.mediator.wobbly_m.set_active(False)
        else:
            self.plugin.set_enabled(False)


class ViewpointSwitcher(Gtk.CheckButton):
    def __init__(self, label):
        GObject.GObject.__init__(self, label=label)

        try:
            self.plugin = CompizPlugin('vpswitch')
        except KeyError, e:
            log.error(e)
            self.set_sensitive(False)
        else:
            self.left_button_setting = CompizSetting(self.plugin, 'left_button')
            self.right_button_setting = CompizSetting(self.plugin, 'right_button')

            self.set_active(self._get_setting_enabled())
            self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            log.debug("The viewport button is enabled")
            if self.plugin.resolve_conflict():
                self.plugin.set_enabled(True)
                self.left_button_setting.set_value('Button4')
                self.right_button_setting.set_value('Button5')
        else:
            log.debug("The viewport button is disabled")
            self.plugin.set_enabled(False)

    def _get_setting_enabled(self):
        if self.plugin.get_enabled() and self.left_button_setting.get_value() == 'Button4' \
                and self.right_button_setting.get_value() == 'Button5':
                    return True
        else:
            return False


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

                setting = CompizSetting(CompizPlugin(name), key)

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

        self.emit('edge_changed', plugin)
        log.debug('%s changed to "%s"' % (widget.edge, plugin))
        if self.old_plugin:
            for name, key, text in self.edge_settings:
                if name == self.old_plugin:
                    log.debug('%s has to unset (%s)' % (name, key))
                    setting = CompizSetting(CompizPlugin(name), key)
                    setting.set_value('')
                    break
            self.old_plugin = plugin
            self.old_key = key

    def set_to_none(self):
        self.handler_block_by_func(self.on_changed)
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


class Compiz(TweakModule):
    __title__ = _('Compiz Settings')
    __desc__ = _('Settings for some amazing desktop eye-candy')
    __icon__ = 'ccsm'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu']

    def __init__(self):
        TweakModule.__init__(self)

        self.create_interface()

    def create_interface(self):
        hbox = Gtk.HBox(spacing=12)
        hbox.pack_start(self.create_edge_setting(), True, False, 0)
        edge_setting = SinglePack(_(' Workspace Edge Settings'), hbox)
        self.add_start(edge_setting, False, False, 0)

        self.snap = SnapWindow(_("Enable snapping windows"), self)
        self.wobbly_w = WobblyWindow(_("Enable wobbly windows"), self);
        self.viewport = ViewpointSwitcher(_('Enable workspace switching with mouse wheel'))

        box = ListPack(_("Desktop Effects"), (self.snap,
                                              self.wobbly_w,
                                              self.viewport))
        self.add_start(box, False, False, 0)

        button1 = OpacityMenu(_("Enable transparent menus"))
        self.wobbly_m = WobblyMenu(_("Enable wobbly menus"), self)

        box = ListPack(_("Menu Effects"), (button1, self.wobbly_m))
        self.add_start(box, False, False, 0)

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
            setting = CompizSetting(plugin, widget.get_current_key())
            setting.set_value(widget.edge)
        else:
            plugin = CompizPlugin(widget.old_plugin)
            plugin.set_enabled(True)
            setting = CompizSetting(plugin, widget.old_key)
            setting.set_value('')

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
