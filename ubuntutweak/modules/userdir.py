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
import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext
import gobject

from ubuntutweak.modules import TweakModule
from ubuntutweak.common.consts import *
from ubuntutweak.common.inifile import IniFile
from ubuntutweak.widgets.dialogs import QuestionDialog, InfoDialog
from ubuntutweak.common.utils import get_icon_with_name

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
        return get_icon_with_name(self.XDG_ICONS[userdir])

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

        dialog = gtk.FileChooserDialog(_("Choose a folder"), 
                                       action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        dialog.set_current_folder(os.getenv("HOME"))

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            fullpath = dialog.get_filename()
            folder = self.uf.set_userdir(userdir, fullpath)
            model.set_value(iter, COLUMN_PATH, folder)
            self.emit('changed')

        dialog.destroy()

    def on_restore_directory(self, widget):
        model, iter = self.get_selection().get_selected()
        userdir = model.get_value(iter, COLUMN_DIR)

        dialog = QuestionDialog(_('Ubuntu Tweak will restore the chosen '
            'directory to the default location.\n'
            'However, you must move your files back into place by yourself.\n'
            'Do you wish to continue?'))

        if dialog.run() == gtk.RESPONSE_YES:
            newdir = os.path.join(os.getenv("HOME"), self.uf.get_restorename(userdir))
            self.uf.set_userdir(userdir, newdir)
            model.set_value(iter, COLUMN_PATH, newdir)

            if not os.path.exists(newdir):
                os.mkdir(newdir)
            elif os.path.isfile(newdir):
                os.remove(newdir)
                os.mkdir(newdir)

            self.emit('changed')

        dialog.destroy()

    def __create_model(self):
        model = gtk.ListStore(
                            gtk.gdk.Pixbuf,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING,
                            gobject.TYPE_STRING)

        for dir, path in self.uf.items():
            pixbuf = self.uf.get_xdg_icon(dir)
            name = self.uf.get_display(dir)

            model.append((pixbuf, name, dir, path))

        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Directory'))
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

        change_item = gtk.MenuItem(_('Change'))
        menu.append(change_item)
        change_item.connect('activate', self.on_change_directory)

        restore_item = gtk.MenuItem(_('Restore to default'))
        menu.append(restore_item)
        restore_item.connect('activate', self.on_restore_directory)

        return menu

class UserDir(TweakModule):
    __title__ = _("Default Folder Locations")
    __desc__ = _("You can change the paths of the default folders here.\n"
                 "Don't change the location of your desktop folder unless you know what you are doing.")
    __icon__ = ['folder-home', 'gnome-fs-home']
    __category__ = 'personal'

    def __init__(self):
        TweakModule.__init__(self)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add_start(sw, True, True, 0)

        dirview = UserdirView()
        sw.add(dirview)

        hbox = gtk.HBox(False, 0)
        self.add_start(hbox, False, False, 0)

        button = gtk.Button(stock = gtk.STOCK_REFRESH)
        button.set_sensitive(False)
        button.connect("clicked", self.on_refresh_clicked)
        hbox.pack_end(button, False, False, 0)

        dirview.connect('changed', self.on_dirview_changed, button)

    def on_refresh_clicked(self, widget):
        os.system('xdg-user-dirs-gtk-update &')
        InfoDialog(_("Update successful!")).launch()
        widget.set_sensitive(False)

    def on_dirview_changed(self, widget, button):
        button.set_sensitive(True)
