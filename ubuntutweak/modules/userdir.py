#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
pyGtk.require("2.0")
from gi.repository import Gdk
from gi.repository import Gtk
import os
from gi.repository import GConf
import gettext
import gobject

from ubuntutweak.modules import TweakModule
from ubuntutweak.common.consts import *
from ubuntutweak.common.inifile import IniFile
from ubuntutweak.ui.dialogs import QuestionDialog, InfoDialog
from ubuntutweak.utils import icon

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
        "XDG_DESKTOP_DIR": _("Desktop"),
        "XDG_DOWNLOAD_DIR": _("Download"),
        "XDG_TEMPLATES_DIR": _("Templates"),
        "XDG_PUBLICSHARE_DIR": _("Public"),
        "XDG_DOCUMENTS_DIR": _("Document"),
        "XDG_MUSIC_DIR": _("Music"),
        "XDG_PICTURES_DIR": _("Pictures"),
        "XDG_VIDEOS_DIR": _("Videos")
    }
    XDG_ICONS = {
        "XDG_DESKTOP_DIR": "desktop",
        "XDG_DOWNLOAD_DIR": "folder-download",
        "XDG_TEMPLATES_DIR": "folder-templates",
        "XDG_PUBLICSHARE_DIR": "folder-publicshare",
        "XDG_DOCUMENTS_DIR": "folder-documents",
        "XDG_MUSIC_DIR": "folder-music",
        "XDG_PICTURES_DIR": "folder-pictures",
        "XDG_VIDEOS_DIR": "folder-videos",
    }

    def __init__(self):
        IniFile.__init__(self, self.filename)

        self.data = self.get_items()

    def __getitem__(self, key):
        return self.data[key]

    def get_items(self):
        dict = {}
        for userdir in self.XDG_DIRS.keys():
            prefix = self.get(userdir).strip('"').split("/")[0]
            if prefix:
                path = os.getenv("HOME") + "/"  + "/".join(self.get(userdir).strip('"').split("/")[1:])
            else:
                path = self.get(userdir).strip('"')

            dict[userdir] = path

        return dict

    def items(self):
        dict = {}
        for userdir in self.XDG_DIRS.keys():
            prefix = self.get(userdir).strip('"').split("/")[0]
            if prefix:
                path = os.getenv("HOME") + "/"  + "/".join(self.get(userdir).strip('"').split("/")[1:])
            else:
                path = self.get(userdir).strip('"')

            dict[userdir] = path

        return dict.items()

    def set_userdir(self, userdir, fullpath):
        dirname = '/'.join(fullpath.split('/')[:3])

        if dirname == os.getenv("HOME"):
            folder = '"$HOME/' + "/".join(fullpath.split('/')[3:]) + '"'
        else:
            folder = '"' + fullpath + '"'

        self.set(userdir, folder)
        self.write()

        if dirname == os.getenv("HOME"):
            folder = os.getenv("HOME") + "/" +  "/".join(fullpath.split('/')[3:])
        else:
            folder = folder.strip('"')

        return folder

    def get_display(self, userdir):
        return self.XDG_DIRS[userdir]

    def get_xdg_icon(self, userdir):
        return icon.get_from_name(self.XDG_ICONS[userdir])

    def get_restorename(self, userdir):
        gettext.bindtextdomain('xdg-user-dirs')
        gettext.textdomain('xdg-user-dirs')

        string = userdir.split('_')[1]
        if string.lower() in 'publicshare':
            string = 'public'

        return gettext.gettext(string.title())

class UserdirView(Gtk.TreeView):

    def __init__(self):
        gobject.GObject.__init__(self)

        self.uf = UserdirFile()

        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()

        menu = self.__create_popup_menu()
        menu.show_all()
        self.connect('button_press_event', self.button_press_event, menu)

    def button_press_event(self, widget, event, menu):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu.popup(None, None, None, event.button, event.time)
        return False

    def on_change_directory(self, widget):
        model, iter = self.get_selection().get_selected()
        userdir = model.get_value(iter, COLUMN_DIR)

        dialog = Gtk.FileChooserDialog(_("Choose a folder"), 
                                       action = Gtk.FileChooserAction.SELECT_FOLDER,
                                       buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        dialog.set_current_folder(os.getenv("HOME"))

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            fullpath = dialog.get_filename()
            folder = self.uf.set_userdir(userdir, fullpath)
            model.set_value(iter, COLUMN_PATH, folder)

        dialog.destroy()

    def on_restore_directory(self, widget):
        model, iter = self.get_selection().get_selected()
        userdir = model.get_value(iter, COLUMN_DIR)

        dialog = QuestionDialog(_('Ubuntu Tweak will restore the selected '
            'directory to it\'s default location.\n'
            'However, you must move your files back into place manually.\n'
            'Do you wish to continue?'))

        if dialog.run() == Gtk.ResponseType.YES:
            newdir = os.path.join(os.getenv("HOME"), self.uf.get_restorename(userdir))
            self.uf.set_userdir(userdir, newdir)
            model.set_value(iter, COLUMN_PATH, newdir)

            if not os.path.exists(newdir):
                os.mkdir(newdir)
            elif os.path.isfile(newdir):
                os.remove(newdir)
                os.mkdir(newdir)

        dialog.destroy()

    def __create_model(self):
        model = Gtk.ListStore(
                            GdkPixbuf.Pixbuf,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING)

        for dir, path in self.uf.items():
            pixbuf = self.uf.get_xdg_icon(dir)
            name = self.uf.get_display(dir)

            model.append((pixbuf, name, dir, path))

        return model

    def __add_columns(self):
        column = Gtk.TreeViewColumn(_('Directory'))
        column.set_spacing(5)
        column.set_sort_column_id(COLUMN_NAME)
        self.append_column(column)

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_attributes(renderer, text = COLUMN_NAME)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Path'), renderer, text = COLUMN_PATH)
        column.set_sort_column_id(COLUMN_PATH)
        self.append_column(column)

    def __create_popup_menu(self):
        menu = Gtk.Menu()

        change_item = Gtk.MenuItem(_('Change'))
        menu.append(change_item)
        change_item.connect('activate', self.on_change_directory)

        restore_item = Gtk.MenuItem(_('Restore to default'))
        menu.append(restore_item)
        restore_item.connect('activate', self.on_restore_directory)

        return menu

class UserDir(TweakModule):
    __title__ = _("Default Folder Locations")
    __desc__ = _("You can change the paths of default folders here.\n"
                 "Don't change the location of your desktop folder unless you know what you are doing.")
    __icon__ = ['folder-home', 'gnome-fs-home']
    __category__ = 'personal'

    def __init__(self):
        TweakModule.__init__(self)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add_start(sw, True, True, 0)

        self.dirview = UserdirView()
        self.dirview.get_selection().connect('changed', self.on_selection_changed)
        sw.add(self.dirview)

        hbuttonbox = Gtk.HButtonBox()
        hbuttonbox.set_spacing(12)
        hbuttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        self.add_start(hbuttonbox, False, False, 0)

        self.restore_button = Gtk.Button(_('_Restore'))
        self.restore_button.set_sensitive(False)
        self.restore_button.connect('clicked', self.on_restore_button_clicked)
        hbuttonbox.pack_end(self.restore_button, False, False, 0)

        self.change_button = Gtk.Button(_('_Change'))
        self.change_button.set_sensitive(False)
        self.change_button.connect('clicked', self.on_change_button_clicked)
        hbuttonbox.pack_end(self.change_button, False, False, 0)

    def on_change_button_clicked(self, widget):
        self.dirview.on_change_directory(widget)

    def on_restore_button_clicked(self, widget):
        self.dirview.on_restore_directory(widget)

    def on_selection_changed(self, widget):
        if widget.get_selected():
            self.change_button.set_sensitive(True)
            self.restore_button.set_sensitive(True)
