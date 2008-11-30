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
import shutil
import gobject
from xdg.DesktopEntry import DesktopEntry
from common.widgets import TweakPage
from common.widgets.dialogs import ErrorDialog
from common.utils import *

(
    COLUMN_ACTIVE,
    COLUMN_ICON,
    COLUMN_PROGRAM,
    COLUMN_PATH,
) = range(4)

class AutoStartDialog(gtk.Dialog):
    """The dialog used to add or edit the autostart program"""
    def __init__(self, desktopentry = None, parent = None):
        """Init the dialog, if use to edit, pass the desktopentry parameter"""
        gtk.Dialog.__init__(self, parent = parent)
        self.set_default_size(400, -1)

        lbl1 = gtk.Label()
        lbl1.set_text_with_mnemonic(_("_Name:"))
        lbl1.set_alignment(0, 0)
        lbl2 = gtk.Label()
        lbl2.set_text_with_mnemonic(_("Co_mmand:"))
        lbl2.set_alignment(0, 0)
        lbl3 = gtk.Label()
        lbl3.set_text_with_mnemonic(_("Comm_ent:"))
        lbl3.set_alignment(0, 0)

        self.pm_name = gtk.Entry ();
        self.pm_name.connect("activate", self.on_entry_activate)
        self.pm_cmd = gtk.Entry ();
        self.pm_cmd.connect("activate", self.on_entry_activate)
        self.pm_comment = gtk.Entry ();
        self.pm_comment.connect("activate", self.on_entry_activate)

        if desktopentry:
            self.set_title(_("Edit Startup Program"))
            self.pm_name.set_text(desktopentry.getName())
            self.pm_cmd.set_text(desktopentry.getExec())
            self.pm_comment.set_text(desktopentry.getComment())
        else:
            self.set_title(_("New Startup Program"))

        button = gtk.Button(_("_Browse..."))
        button.connect("clicked", self.on_choose_program)
        
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(self.pm_cmd)
        hbox.pack_start(button, False, False, 0)

        table = gtk.Table(3, 2)
        table.attach(lbl1, 0, 1, 0, 1, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(lbl2, 0, 1, 1, 2, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(lbl3, 0, 1, 2, 3, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(self.pm_name, 1, 2, 0, 1)
        table.attach(hbox, 1, 2, 1, 2, yoptions = gtk.EXPAND)
        table.attach(self.pm_comment, 1, 2, 2, 3)

        self.vbox.pack_start(table)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_OK)

        self.set_default_response(gtk.RESPONSE_OK)

        self.show_all()

    def on_entry_activate(self, widget, data = None):
        self.response(gtk.RESPONSE_OK)

    def on_choose_program(self, widget, data = None):
        """The action taken by clicked the browse button"""
        dialog = gtk.FileChooserDialog(_("Choose a Program"), 
                            action = gtk.FILE_CHOOSER_ACTION_OPEN, 
                            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            self.pm_cmd.set_text(dialog.get_filename())
        dialog.destroy()

class AutoStartItem(gtk.TreeView):
    """The autostart program list, loading from userdir and systemdir"""
    userdir = os.path.join(os.path.expanduser("~"), ".config/autostart")
    etc_dir = "/etc/xdg/autostart"
    gnome_dir = "/usr/share/gnome/autostart"

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.refresh_items()

        model = gtk.ListStore(
                    gobject.TYPE_BOOLEAN,
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING,
                    gobject.TYPE_STRING)

        self.set_model(model)
        self.__create_model()

        self.__add_columns()
        self.set_rules_hint(True)

        selection = self.get_selection()
        selection.connect("changed", self.selection_cb)

        menu = self.create_popup_menu()
        menu.show_all()
        self.connect("button_press_event", self.button_press_event, menu)    

    def refresh_items(self):
        if not os.path.exists(self.userdir): os.mkdir(self.userdir)

        #get the item with full-path from the dirs
        self.useritems = map(lambda path: "%s/%s" % (self.userdir, path), 
                                                    os.listdir(self.userdir))

        etc_items = map(lambda path: "%s/%s" % (self.etc_dir, path),
                        filter(lambda i: i not in os.listdir(self.userdir), 
                                                    os.listdir(self.etc_dir)))

        gnome_items = map(lambda path: "%s/%s" % (self.gnome_dir, path),
                        filter(lambda i: i not in os.listdir(self.userdir), 
                                                    os.listdir(self.gnome_dir)))

        self.systemitems = etc_items + gnome_items

        for item in self.useritems:
            if os.path.isdir(item): 
                self.useritems.remove(item)
        for item in self.systemitems:
            if os.path.isdir(item): 
                self.systemitems.remove(item)

    def selection_cb(self, widget, data = None):
        """If selected an item, it should set the sensitive of the remove and edit button"""
        model, iter = widget.get_selected()
        remove = self.get_data("remove")
        edit = self.get_data("edit")
        if iter:
            remove.set_sensitive(True)
            edit.set_sensitive(True)
        else:
            remove.set_sensitive(False)
            edit.set_sensitive(False)

    def button_press_event(self, widget, event, menu):
        """If right-click taken, show the popup menu"""
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu.popup(None, None, None, event.button, event.time)
        return False

    def create_popup_menu(self):
        menu = gtk.Menu()

        remove = gtk.MenuItem(_("Delete from Disk"))
        remove.connect("activate", self.on_delete_from_disk)
        
        menu.append(remove)
        menu.attach_to_widget(self, None)

        return menu

    def on_delete_from_disk(self, widget, data = None):
        model, iter = self.get_selection().get_selected()

        if iter:
            path = model.get_value(iter, COLUMN_PATH)
            if self.is_defaultitem(path):
                ErrorDialog(_("Can't delete the system item from disk.")).launch()
            else:
                os.remove(path)

        self.update_items()

    def update_items(self, all = False, comment = False):
        """'all' parameter used to show the hide item,
        'comment' parameter used to show the comment of program"""
        self.refresh_items()
        self.__create_model(all, comment)

    def __create_model(self, all = False, comment = False):
        model = self.get_model()
        model.clear()

        allitems = []
        allitems.extend(self.useritems)
        allitems.extend(self.systemitems)

        for item in allitems:
            desktopentry = DesktopEntry(item)

            if desktopentry.get("Hidden"):
                if not all:
                    continue
            iter = model.append()
            enable = desktopentry.get("X-GNOME-Autostart-enabled")
            if enable == "false":
                enable = False
            else:
                enable = True
            
            iconname = desktopentry.get('Icon', locale = False)
            if not iconname:
               iconname = desktopentry.get('Name', locale = False)
               if not iconname:
                   iconname = desktopentry.getName()

            icon = get_icon_with_name(iconname, 32)

            name = desktopentry.getName()
            if comment:
                comment = desktopentry.getComment()
                if not comment:
                    comment = _("None description")
                description = "<b>%s</b>\n%s" % (name, comment)
            else:
                description = "<b>%s</b>" % name

            model.set(iter,
                      COLUMN_ACTIVE, enable,
                      COLUMN_ICON, icon,
                      COLUMN_PROGRAM, description,
                      COLUMN_PATH, item)

    def __add_columns(self):
        model = self.get_model()

        renderer = gtk.CellRendererToggle()
        renderer.connect("toggled", self.enabled_toggled, model)
        column = gtk.TreeViewColumn("", renderer, active = COLUMN_ACTIVE)
        column.set_sort_column_id(COLUMN_ACTIVE)
        self.append_column(column)

        column = gtk.TreeViewColumn(_("Program"))
        column.set_spacing(3)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, markup = COLUMN_PROGRAM)
        column.set_sort_column_id(COLUMN_ACTIVE)
        self.append_column(column)

    def enabled_toggled(self, cell, path, model):
        iter = model.get_iter((int(path),))
        active = model.get_value(iter, COLUMN_ACTIVE)
        path = model.get_value(iter, COLUMN_PATH)

        if self.is_defaultitem(path):
            shutil.copy(path, self.userdir)
            path = os.path.join(self.userdir, os.path.basename(path))
            desktopentry = DesktopEntry(path)
            desktopentry.set("X-GNOME-Autostart-enabled", "false")
            desktopentry.write()
            model.set(iter, COLUMN_PATH, path)
        else:
            if active:
                desktopentry = DesktopEntry(path)
                desktopentry.set("X-GNOME-Autostart-enabled", "false")
                desktopentry.write()
            else:
                if self.is_in_systemdir(path):
                    os.remove(path)
                    path = os.path.join(self.get_systemdir(path), os.path.basename(path))
                    model.set(iter, COLUMN_PATH, path)
                else:
                    desktopentry = DesktopEntry(path)
                    desktopentry.set("X-GNOME-Autostart-enabled", "true")
                    desktopentry.set("Hidden", "false")
                    desktopentry.write()

        active =  not active

        model.set(iter, COLUMN_ACTIVE, active)

    def is_in_systemdir(self, path):
        return os.path.basename(path) in os.listdir(self.etc_dir) or \
                os.path.basename(path) in os.listdir(self.gnome_dir)

    def is_defaultitem(self, path):
        return os.path.dirname(path) in [self.etc_dir, self.gnome_dir]

    def get_systemdir(self, path):
        if os.path.basename(path) in os.listdir(self.etc_dir):
            return self.etc_dir
        elif os.path.basename(path) in os.listdir(self.gnome_dir):
            return self.gnome_dir

class AutoStart(TweakPage):
    """The box pack the autostart list"""
    def __init__(self):
        TweakPage.__init__(self,
                _('Session Programs'),
                _('Here you can manage what programs get started upon login.\n'
                'You can hide items from view by selecting and clicking "Remove"\n'
                'To permanently delete it, right-click and press "Delete".'))

        hbox = gtk.HBox(False, 10)
        self.pack_start(hbox, True, True, 10)

        #create the two checkbutton for extra options of auto run list
        self.show_comment_button = gtk.CheckButton(_("Show comments"))
        self.pack_start(self.show_comment_button, False, False, 0)
        self.show_all_button = gtk.CheckButton(_("Show all runnable programs"))
        self.pack_start(self.show_all_button, False, False, 0)

        self.show_all_button.connect("toggled", self.on_show_all, self.show_comment_button)
        self.show_comment_button.connect("toggled", self.on_show_comment, self.show_all_button)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.treeview = AutoStartItem()
        sw.add(self.treeview)
        
        vbox = gtk.VBox(False, 5)
        hbox.pack_start(vbox, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_ADD)
        button.connect("clicked", self.on_add_item, self.treeview)
        vbox.pack_start(button, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_REMOVE)
        button.set_sensitive(False)
        button.connect("clicked", self.on_remove_item, self.treeview)
        vbox.pack_start(button, False, False, 0)
        self.treeview.set_data("remove", button)

        button = gtk.Button(stock = gtk.STOCK_EDIT)
        button.set_sensitive(False)
        button.connect("clicked", self.on_edit_item, self.treeview)
        vbox.pack_start(button, False, False, 0)
        self.treeview.set_data("edit", button)

    def on_show_all(self, widget, another):
        if widget.get_active():
            if another.get_active():
                self.treeview.update_items(all = True, comment = True)
            else:
                self.treeview.update_items(all = True)
        else:
            if another.get_active():
                self.treeview.update_items(comment = True)
            else:
                self.treeview.update_items()

    def on_show_comment(self, widget, another):
        if widget.get_active():
            if another.get_active():
                self.treeview.update_items(all = True, comment = True)
            else:
                self.treeview.update_items(comment = True)
        else:
            if another.get_active():
                self.treeview.update_items(all = True)
            else:
                self.treeview.update_items()

    def on_add_item(self, widget, treeview):
        dialog = AutoStartDialog(parent = widget.get_toplevel())
        if dialog.run() == gtk.RESPONSE_OK:
            name = dialog.pm_name.get_text()
            cmd = dialog.pm_cmd.get_text()
            if not name:
                ErrorDialog(_("The name of the startup program cannot be empty")).launch()
            elif not cmd:
                ErrorDialog(_("Text was empty (or contained only whitespace)")).launch()
            else:
                path = os.path.join(treeview.userdir, os.path.basename(cmd) + ".desktop")
                desktopentry = DesktopEntry(path)
                desktopentry.set("Name", dialog.pm_name.get_text())
                desktopentry.set("Exec", dialog.pm_cmd.get_text())
                desktopentry.set("Comment", dialog.pm_comment.get_text())
                desktopentry.set("Type", "Application")
                desktopentry.set("Version", "1.0")
                desktopentry.set("X-GNOME-Autostart-enabled", "true")
                desktopentry.write()
                treeview.update_items(all = self.show_all_button.get_active(), comment = self.show_comment_button.get_active())
                dialog.destroy()
                return
        dialog.destroy()

    def on_remove_item(self, widget, treeview):
        model, iter = treeview.get_selection().get_selected()

        if iter:
            path = model.get_value(iter, COLUMN_PATH)
            if path[1:4] == "etc":
                shutil.copy(path, treeview.userdir)
                desktopentry = DesktopEntry(os.path.join(treeview.userdir, os.path.basename(path)))
            else:
                desktopentry = DesktopEntry(path)
            desktopentry.set("Hidden", "true")
            desktopentry.set("X-GNOME-Autostart-enabled", "false")
            desktopentry.write()

            treeview.update_items(all = self.show_all_button.get_active(), comment = self.show_comment_button.get_active())

    def on_edit_item(self, widget, treeview):
        model, iter = treeview.get_selection().get_selected()

        if iter:
            path = model.get_value(iter, COLUMN_PATH)
            if path[1:4] == "etc":
                shutil.copy(path, treeview.userdir)
                path = os.path.join(treeview.userdir, os.path.basename(path))
            dialog = AutoStartDialog(DesktopEntry(path), widget.get_toplevel())
            if dialog.run() == gtk.RESPONSE_OK:
                name = dialog.pm_name.get_text()
                cmd = dialog.pm_cmd.get_text()
                if not name:
                    ErrorDialog(_("The name of the startup program cannot be empty")).launch()
                elif not cmd:
                    ErrorDialog(_("Text was empty (or contained only whitespace)")).launch()
                else:
                    desktopentry = DesktopEntry(path)
                    desktopentry.set("Name", name, locale = True)
                    desktopentry.set("Exec", cmd)
                    desktopentry.set("Comment", dialog.pm_comment.get_text(), locale = True)
                    desktopentry.write()
                    treeview.update_items(all = self.show_all_button.get_active(), comment = self.show_comment_button.get_active())
                    dialog.destroy()
                    return
            dialog.destroy()

if __name__ == "__main__":
    from utility import Test
    Test(AutoStart)
