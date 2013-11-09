# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2012 Tualatrix Chou <tualatrix@gmail.com>
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

from gi.repository import GObject, Gtk, GdkPixbuf

from ubuntutweak.utils import icon
from ubuntutweak.gui.treeviews import get_local_path
from ubuntutweak.modules  import TweakModule
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.gui.containers import GridPack
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.compizsettings import CompizPlugin, CompizSetting

log = logging.getLogger('Workspace')


class EdgeComboBox(Gtk.ComboBox):
    edge_settings = (
        ('expo', 'expo_edge', _('Show Workspaces')),
        ('scale', 'initiate_all_edge', _('Show Windows')),
        ('core', 'show_desktop_edge', _('Show Desktop')),
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


class Workspace(TweakModule):
    __title__ = _('Workspace')
    __desc__ = _('Workspace size and screen edge action settings')
    __icon__ = 'workspace-switcher'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu']

    utext_edge_delay = _('Edge trigger delay (ms):')
    utext_hsize = _('Horizontal workspace:')
    utext_vsize = _('Vertical workspace:')

    def __init__(self):
        TweakModule.__init__(self)

        self.is_arabic = os.getenv('LANG').startswith('ar')

        hbox = Gtk.HBox(spacing=12)
        hbox.pack_start(self.create_edge_setting(), True, False, 0)
        self.add_start(hbox, False, False, 0)

        self.add_start(Gtk.Separator(), False, False, 6)

        grid_pack = GridPack(
                WidgetFactory.create("Scale",
                             label=self.utext_edge_delay,
                             key="core.edge_delay",
                             backend="compiz",
                             min=0,
                             max=1000,
                             step=50,
                             enable_reset=True),
                WidgetFactory.create("Scale",
                             label=self.utext_hsize,
                             key="core.hsize",
                             backend="compiz",
                             min=1,
                             max=16,
                             step=1,
                             enable_reset=True),
                WidgetFactory.create("Scale",
                             label=self.utext_vsize,
                             key="core.vsize",
                             backend="compiz",
                             min=1,
                             max=16,
                             step=1,
                             enable_reset=True),
                )

        self.add_start(grid_pack, False, False, 0)

    def create_edge_setting(self):
        hbox = Gtk.HBox(spacing=12)

        left_vbox = Gtk.VBox(spacing=6)

        self.TopLeft = EdgeComboBox("TopLeft")
        left_vbox.pack_start(self.TopLeft, False, False, 0)

        self.BottomLeft = EdgeComboBox("BottomLeft")
        left_vbox.pack_end(self.BottomLeft, False, False, 0)

        wallpaper = get_local_path(GSetting('org.gnome.desktop.background.picture-uri').get_value())

        if wallpaper:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper, 160, 100)
            except GObject.GError:
                pixbuf = icon.get_from_name('ubuntu-tweak', size=128)
        else:
            pixbuf = icon.get_from_name('ubuntu-tweak', size=128)

        image = Gtk.Image.new_from_pixbuf(pixbuf)

        right_vbox = Gtk.VBox(spacing=6)

        self.TopRight = EdgeComboBox("TopRight")
        right_vbox.pack_start(self.TopRight, False, False, 0)

        self.BottomRight = EdgeComboBox("BottomRight")
        right_vbox.pack_end(self.BottomRight, False, False, 0)

        if self.is_arabic:
            hbox.pack_start(right_vbox, False, False, 0)
            hbox.pack_start(image, False, False, 0)
            hbox.pack_start(left_vbox, False, False, 0)
        else:
            hbox.pack_start(left_vbox, False, False, 0)
            hbox.pack_start(image, False, False, 0)
            hbox.pack_start(right_vbox, False, False, 0)

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

            setting = CompizSetting("%s.%s" % (widget.get_current_plugin(),
                widget.get_current_key()))
            setting.set_value(widget.edge)
