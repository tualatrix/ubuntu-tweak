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

from gi.repository import GObject, Gtk, Gdk, GConf, GdkPixbuf

from ubuntutweak.modules  import TweakModule
from ubuntutweak.settings.compizsettings import CompizPlugin
from ubuntutweak.gui.widgets import KeyGrabber, KeyModifier
from ubuntutweak.gui.cellrenderers import CellRendererButton
from ubuntutweak.utils import icon


class Shortcuts(TweakModule):
    __title__  = _("Shortcuts")
    __desc__  = _("By configuring keyboard shortcuts, you can access your favourite applications instantly.\n"
                  "Enter the command to run the application and choose a shortcut key combination.")
    __icon__ = 'preferences-desktop-keyboard-shortcuts'
    __category__ = 'personal'
    __distro__ = ['precise']

    (COLUMN_ID,
     COLUMN_LOGO,
     COLUMN_TITLE,
     COLUMN_ICON,
     COLUMN_COMMAND,
     COLUMN_KEY,
     COLUMN_EDITABLE,
    ) = range(7)

    def __init__(self):
        TweakModule.__init__(self)

        if not CompizPlugin.get_plugin_active('commands'):
            CompizPlugin.set_plugin_active('commands', True)

        sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add_start(sw)

        treeview = self.create_treeview()
        sw.add(treeview)
    
    def create_treeview(self):
        treeview = Gtk.TreeView()

        self.model = self._create_model()

        treeview.set_model(self.model)

        self._add_columns(treeview)

        return treeview

    def _create_model(self):
        model = Gtk.ListStore(GObject.TYPE_INT,
                              GdkPixbuf.Pixbuf,
                              GObject.TYPE_STRING,
                              GdkPixbuf.Pixbuf,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING,
                              GObject.TYPE_BOOLEAN)

        client = GConf.Client.get_default()
        logo = icon.get_from_name('gnome-terminal')

        for id in range(12):
            id = id + 1

            title = _("Command %d") % id
            command = client.get_string("/apps/metacity/keybinding_commands/command_%d" % id)
            key = client.get_string("/apps/metacity/global_keybindings/run_command_%d" % id)

            if not command:
                command = _("None")

            pixbuf = icon.get_from_name(command)

            if key == "disabled":
                key = _("disabled")

            model.append((id, logo, title, pixbuf, command, key, True))

        return model

    def _add_columns(self, treeview):
        model = treeview.get_model()

        column = Gtk.TreeViewColumn(_("ID"))

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.COLUMN_LOGO)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.COLUMN_TITLE)
        treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Command"))

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_cell_edited, model)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.COLUMN_COMMAND)
        column.add_attribute(renderer, 'editable', self.COLUMN_EDITABLE)
        treeview.append_column(column)

        column = Gtk.TreeViewColumn(_("Key"))

        renderer = Gtk.CellRendererText()
        renderer.connect("editing-started", self.on_editing_started)
        renderer.connect("edited", self.on_cell_edited, model)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', self.COLUMN_KEY)
        column.add_attribute(renderer, 'editable', self.COLUMN_EDITABLE)
        column.set_resizable(True)
        treeview.append_column(column)

        #TODO re-enable the clean button
#        renderer = CellRendererButton(_("Clean"))
#        renderer.connect("clicked", self.on_clean_clicked)
#        column.pack_start(renderer, False)

    def on_clean_clicked(self, cell, path):
        iter = self.model.get_iter_from_string(path)
        id = self.model.get_value(iter, self.COLUMN_ID)
        self.model.set_value(iter, self.COLUMN_KEY, _("disabled"))
        client = GConf.Client.get_default()
        client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, "disabled")

    def on_got_key(self, widget, key, mods, cell_data):
        cell, path = cell_data

        new = Gtk.accelerator_name(key, Gdk.ModifierType(mods))
        if new in ('BackSpace', 'Delete', 'Escape', ''):
            self.on_clean_clicked(cell, path)
            return True

        for mod in KeyModifier:
            if "%s_L" % mod in new:
                new = new.replace ("%s_L" % mod, "<%s>" % mod)
            if "%s_R" % mod in new:
                new = new.replace ("%s_R" % mod, "<%s>" % mod)

        widget.destroy()

        client = GConf.Client.get_default()
        column = cell.get_data("id")
        iter = self.model.get_iter_from_string(cell.get_data("path_string"))

        id = self.model.get_value(iter, self.COLUMN_ID)

        client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, new)
        self.model.set_value(iter, self.COLUMN_KEY, new)

    def on_editing_started(self, cell, editable, path):
        grabber = KeyGrabber(self.get_toplevel(), label="Grab key combination")
        cell.set_data("path_string", path)
        grabber.hide()
        grabber.set_no_show_all(True)
        grabber.connect('changed', self.on_got_key, (cell, path))
        grabber.begin_key_grab(None)

    def on_cell_edited(self, cell, path_string, new_text, model):
        iter = model.get_iter_from_string(path_string)

        client = GConf.Client.get_default()
        column = cell.get_data("id")

        id = model.get_value(iter, self.COLUMN_ID)
        old = model.get_value(iter, self.COLUMN_COMMAND)

        if old != new_text:
            client.set_string("/apps/metacity/keybinding_commands/command_%d" % id, new_text)
            if new_text:
                pixbuf = icon.get_from_name(new_text)

                model.set_value(iter, self.COLUMN_ICON, pixbuf)
                model.set_value(iter, self.COLUMN_COMMAND, new_text)
            else:
                model.set_value(iter, self.COLUMN_ICON, None)
                model.set_value(iter, self.COLUMN_COMMAND, _("None"))
