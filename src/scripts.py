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
import stat
import shutil
import gobject
import gettext
import gnomevfs
from gnome import ui
from common.consts import *
from common.utils import get_icon_with_type
from common.widgets import TweakPage, DirView, FlatView
from common.widgets.dialogs import WarningDialog


(
    COLUMN_ICON,
    COLUMN_TITLE,
    COLUMN_PATH,
    COLUMN_EDITABLE,
) = range(4)

class AbstractScripts:
    systemdir = os.path.join(os.path.expanduser("~"), ".ubuntu-tweak/scripts")
    userdir = os.path.join(os.getenv("HOME"), ".gnome2", "nautilus-scripts")

class DefaultScripts(AbstractScripts):
    """This class use to create the default scripts"""
    scripts = {
            "copy-to": _("Copy to ..."),
            "move-to": _("Move to ..."),
            "link-to": _("Link to ..."),
            "open-with-gedit": _("Open with gedit"),
            "open-with-gedit-as-root": _("Open with gedit(as root)"),
            "browse-as-root": _("Browse as root"),
            "search-in-current": _("Search in current folder"),
            }

    def create(self):
        if not os.path.exists(self.systemdir):
            os.makedirs(self.systemdir)
        for file, des in self.scripts.items():
            realname = "%s" % des
            if not os.path.exists(os.path.join(self.systemdir,realname)):
                shutil.copy(os.path.join(DATA_DIR, "scripts/%s" % file), os.path.join(self.systemdir,realname))

    def remove(self):
        if not os.path.exists(self.systemdir):
            return 
        if os.path.isdir(self.systemdir): 
            for root, dirs, files in os.walk(self.systemdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    os.rmdir(self.systemdir)
        else:
            os.unlink(self.systemdir)
        return

class EnableScripts(DirView, AbstractScripts):
    """The treeview to display the enable scripts"""
    type = _("Enabled Scripts")

    def __init__(self):
        DirView.__init__(self, self.userdir)

    def do_update_model(self, dir, iter):
        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            pixbuf = get_icon_with_type(fullname, 24)

            child_iter = self.model.append(iter)
            self.model.set(child_iter,
                              COLUMN_ICON, pixbuf,
                              COLUMN_TITLE, os.path.basename(fullname),
                              COLUMN_PATH, fullname, 
                              COLUMN_EDITABLE, False)

            if os.path.isdir(fullname):
                self.do_update_model(fullname, child_iter)
            else:
                if not os.access(fullname, os.X_OK):
                    os.chmod(fullname, stat.S_IRWXU)

class DisableScripts(FlatView, AbstractScripts):
    """The treeview to display the system template"""
    type = _("Disabled Scripts")

    def __init__(self):
        FlatView.__init__(self, self.systemdir, self.userdir)

class Scripts(TweakPage, AbstractScripts):
    """Freedom added your docmuent scripts"""
    def __init__(self):
        TweakPage.__init__(self, 
                _("Manage Scripts"),
                _('You can do all kinds of tasks with scripts.\nYou can drag and drop from File Manager.\n"Scripts" will be added to the context menu.\n'))

        self.default = DefaultScripts()
        self.config_test()

        hbox = gtk.HBox(False, 10)
        self.pack_start(hbox)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.enable_scripts = EnableScripts()
        sw.add(self.enable_scripts)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.disable_scripts = DisableScripts()
        sw.add(self.disable_scripts)

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, False, False, 10)

        button = gtk.Button(_("Rebuild System Scripts"))
        button.connect("clicked", self.on_rebuild_clicked)
        hbox.pack_end(button, False, False, 5)
        
        self.enable_scripts.connect('drag_data_received', self.on_enable_drag_data_received)
        self.enable_scripts.connect('deleted', self.on_enable_deleted)
        self.disable_scripts.connect('drag_data_received', self.on_disable_drag_data_received)

    def on_enable_deleted(self, widget):
        self.disable_scripts.update_model()

    def on_enable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.disable_scripts.update_model()

    def on_disable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.enable_scripts.update_model()

    def on_rebuild_clicked(self, widget):
        dialog = WarningDialog(_('This will delete all disabled scripts.\nDo you wish to continue?'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.default.remove()
            self.default.create()
            self.disable_scripts.update_model()
        dialog.destroy()

    def config_test(self):
        if not os.path.exists(self.systemdir):
            self.default.create()

if __name__ == "__main__":
    from utility import Test
    Test(Scripts)
