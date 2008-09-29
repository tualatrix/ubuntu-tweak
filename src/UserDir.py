#!/usr/bin/env python

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

import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext
import gobject

from common.IniFile import IniFile
from common.Consts import InitLocale
from common.Widgets import TweakPage, EntryBox, QuestionDialog, InfoDialog

(
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DIR,
    COLUMN_PATH,
) = range(4)

class UserdirFile(IniFile):
    """Class to parse userdir file"""
    filename = os.path.join(os.path.expanduser("~"), ".config/user-dirs.dirs")
    XDG_DIRS = {
            "XDG_DESKTOP_DIR": _("Desktop Folder"),
            "XDG_DOWNLOAD_DIR": _("Download Folder"),
            "XDG_TEMPLATES_DIR": _("Templates Folder"),
            "XDG_PUBLICSHARE_DIR": _("Public Folder"),
            "XDG_DOCUMENTS_DIR": _("Document Folder"),
            "XDG_MUSIC_DIR": _("Music Folder"),
            "XDG_PICTURES_DIR": _("Pictures Folder"),
            "XDG_VIDEOS_DIR": _("Videos Folder")
            }
    def __init__(self):
        IniFile.__init__(self, self.filename)

    def items(self):
        dict = {}
        for userdir in self.XDG_DIRS.keys():
            prefix = self.get(userdir).strip('"').split("/")[0]
            if prefix:
                path = os.getenv("HOME") + "/"  + "/".join([dir for dir in self.get(userdir).strip('"').split("/")[1:]])
            else:
                path = self.get(userdir).strip('"')

            dict[userdir] = path

        return dict.items()

    def set_userdir(self, userdir, fullpath):
        dirname = '/'.join([path for path in fullpath.split('/')[:3]])

        if dirname == os.getenv("HOME"):
            folder = '"$HOME/' + "/".join([dir for dir in fullpath.split('/')[3:]]) + '"'
        else:
            folder = '"' + fullpath + '"'

        self.set(userdir, folder)
        self.write()

        if dirname == os.getenv("HOME"):
            folder = os.getenv("HOME") + "/" +  "/".join([dir for dir in fullpath.split('/')[3:]])
        else:
            folder = folder.strip('"')

        return folder

    def get_display(self, userdir):
        return self.XDG_DIRS[userdir]

    def get_restorename(self, userdir):
        gettext.bindtextdomain('xdg-user-dirs')
        gettext.textdomain('xdg-user-dirs')

        string = userdir.split('_')[1]
        if string.lower() in 'publicshare':
            string = 'public'

        return gettext.gettext(string.title())

class UserdirView(gtk.TreeView):
    __gsignals__ = {
            'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
            }
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.uf = UserdirFile()

        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()

        menu = self.__create_popup_menu()
        menu.show_all()
        self.connect('button_press_event', self.button_press_event, menu)

    def button_press_event(self, widget, event, menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu.popup(None, None, None, event.button, event.time)
        return False

    def on_change_directory(self, widget):
        model, iter = self.get_selection().get_selected()
        userdir = model.get_value(iter, COLUMN_DIR)

        dialog = gtk.FileChooserDialog(_("Select a new folder"), 
                                       action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        dialog.set_current_folder(os.getenv("HOME"))

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            fullpath = dialog.get_filename()

            folder = self.uf.set_userdir(userdir, fullpath)

            model.set_value(iter, COLUMN_PATH, folder)

        dialog.destroy()
        self.emit('changed')

    def on_restore_directory(self, widget):
        model, iter = self.get_selection().get_selected()
        userdir = model.get_value(iter, COLUMN_DIR)

        dialog = QuestionDialog(_('<b><big>Please notice</big></b>\n\nUbuntu Tweak will restore the directory to the default setting.\nBut you need to migration your files by yourself.\nGo on?'))

        if dialog.run() == gtk.RESPONSE_YES:
            newdir = os.path.join(os.getenv("HOME"), self.uf.get_restorename(userdir))
            self.uf.set_userdir(userdir, newdir)
            model.set_value(iter, COLUMN_PATH, newdir)

            if not os.path.exists(newdir):
                os.mkdir(newdir)

        dialog.destroy()
        self.emit('changed')

    def __create_model(self):
        model = gtk.ListStore(
                            gtk.gdk.Pixbuf,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING)

        icontheme = gtk.icon_theme_get_default()
        icon = icontheme.lookup_icon('gnome-fs-directory', 24, gtk.ICON_LOOKUP_NO_SVG).load_icon()

        for dir, path in self.uf.items():
            name = self.uf.get_display(dir)

            model.append((icon, name, dir, path))

        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Direcotry name'))
        column.set_spacing(5)
        column.set_sort_column_id(COLUMN_NAME)
        self.append_column(column)

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = COLUMN_NAME)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Path'), renderer, text = COLUMN_PATH)
        column.set_sort_column_id(COLUMN_PATH)
        self.append_column(column)

    def __create_popup_menu(self):
        menu = gtk.Menu()

        change_item = gtk.MenuItem(_('Change Directory'))
        menu.append(change_item)
        change_item.connect('activate', self.on_change_directory)

        restore_item = gtk.MenuItem(_('Restore Directory'))
        menu.append(restore_item)
        restore_item.connect('activate', self.on_restore_directory)

        return menu

class UserDir(TweakPage):
    """Setting the user default dictories"""
    def __init__(self):
        TweakPage.__init__(self, 
                _("Set your document folders"), 
                _("You can change the default document folders.\nDon't change the Desktop folder in normal case."))

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.pack_start(sw, True, True, 5)

        dirview = UserdirView()
        sw.add(dirview)

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, False, False, 5)

        button = gtk.Button(stock = gtk.STOCK_REFRESH)
        button.set_sensitive(False)
        button.connect("clicked", self.on_refresh_clicked)
        hbox.pack_end(button, False, False, 0)

        dirview.connect('changed', self.on_dirview_changed, button)

    def on_refresh_clicked(self, widget):
        os.system('xdg-user-dirs-gtk-update &')
        InfoDialog(_("Update successfully!")).launch()
        widget.set_sensitive(False)

    def on_dirview_changed(self, widget, button):
        button.set_sensitive(True)

if __name__ == "__main__":
    from Utility import Test
    Test(UserDir)
