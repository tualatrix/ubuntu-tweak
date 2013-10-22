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
import stat
import shutil
import logging
import platform

from gi.repository import Gtk, GObject

from ubuntutweak.modules  import TweakModule
from ubuntutweak.utils import icon
from ubuntutweak import system
from ubuntutweak.common.consts import DATA_DIR, CONFIG_ROOT
from ubuntutweak.gui.treeviews import DirView, FlatView
from ubuntutweak.gui.dialogs import QuestionDialog

log = logging.getLogger('Script')


class AbstractScripts(object):
    system_dir = os.path.join(CONFIG_ROOT, 'scripts')

    if int(platform.dist()[1][0:2]) >= 13:
        user_dir = os.path.expanduser('~/.local/share/nautilus/scripts')
    else:
        user_dir = os.path.join(os.getenv('HOME'), '.gnome2', 'nautilus-scripts')


class DefaultScripts(AbstractScripts):
    '''This class use to create the default scripts'''
    scripts = {
            'create-launcher': _('Create Launcher ...'),
            'copy-to': _('Copy to ...'),
            'copy-to-desktop': _('Copy to Desktop'),
            'copy-to-download': _('Copy to Download'),
            'copy-to-home': _('Copy to Home'),
            'check-md5-sum': _('Check md5 sum'),
            'compress-pdf': _('Compress PDF'),
            'move-to': _('Move to ...'),
            'move-to-desktop': _('Move to Desktop'),
            'move-to-download': _('Move to Download'),
            'move-to-home': _('Move to Home'),
            'hardlink-to': _('Create hardlink to ...'),
            'link-to': _('Link to ...'),
            'link-to-desktop': _('Link to Desktop'),
            'link-to-download': _('Link to Download'),
            'link-to-home': _('Link to Home'),
            'open-with-your-favourite-text-editor': _('Open with your favourite text editor'),
            'open-with-your-favourite-text-editor-as-root': _('Open with your favourite text editor (as root)'),
            'browse-as-root': _('Browse as root'),
            'search-in-current': _('Search in current folder'),
            'convert-image-to-jpg': _('Convert image to JPG'),
            'convert-image-to-png': _('Convert image to PNG'),
            'convert-image-to-gif': _('Convert image to GIF'),
            'set-image-as-wallpaper': _('Set image as wallpaper'),
            'make-hard-shadow-to-image': _('Make hard shadow to image'),
            }

    def create(self):
        if not os.path.exists(self.system_dir):
            os.makedirs(self.system_dir)
        for file, des in self.scripts.items():
            realname = '%s' % des
            if not os.path.exists(os.path.join(self.system_dir,realname)):
                shutil.copy(os.path.join(DATA_DIR, 'scripts/%s' % file), os.path.join(self.system_dir,realname))

    def remove(self):
        if not os.path.exists(self.system_dir):
            return
        if os.path.isdir(self.system_dir):
            for root, dirs, files in os.walk(self.system_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    os.rmdir(self.system_dir)
        else:
            os.unlink(self.system_dir)
        return


class EnableScripts(DirView, AbstractScripts):
    '''The treeview to display the enable scripts'''
    type = _('Enabled Scripts')

    (COLUMN_ICON,
     COLUMN_TITLE,
     COLUMN_PATH,
     COLUMN_EDITABLE) = range(4)

    def __init__(self):
        DirView.__init__(self, self.user_dir)

    def do_update_model(self, dir, iter):
        for item in os.listdir(dir):
            fullname = os.path.join(dir, item)
            pixbuf = icon.guess_from_path(fullname)

            child_iter = self.model.append(iter,
                                           (pixbuf, os.path.basename(fullname),
                                            fullname, False))

            if os.path.isdir(fullname):
                self.do_update_model(fullname, child_iter)
            else:
                if not os.access(fullname, os.X_OK):
                    try:
                        os.chmod(fullname, stat.S_IRWXU)
                    except:
                        pass


class DisableScripts(FlatView, AbstractScripts):
    '''The treeview to display the system template'''
    type = _('Disabled Scripts')

    def __init__(self):
        FlatView.__init__(self, self.system_dir, self.user_dir)


class Scripts(TweakModule, AbstractScripts):
    __title__  = _('Scripts')
    __desc__  = _("Scripts can be used to complete all kinds of tasks.\n"
                  "You can drag and drop scripts here from File Manager.\n"
                  "'Scripts' will then be added to the context menu.")
    __icon__ = 'text-x-script'
    __utactive__ = True
    __category__ = 'personal'

    def __init__(self):
        TweakModule.__init__(self, 'templates.ui')

        self.default = DefaultScripts()
        self.config_test()

        self.enable_scripts = EnableScripts()
        self.sw1.add(self.enable_scripts)

        self.disable_scripts = DisableScripts()
        self.sw2.add(self.disable_scripts)

        self.enable_scripts.connect('drag_data_received', self.on_enable_drag_data_received)
        self.enable_scripts.connect('deleted', self.on_enable_deleted)
        self.disable_scripts.connect('drag_data_received', self.on_disable_drag_data_received)

        self.add_start(self.hbox1)

        hbox = Gtk.HBox(spacing=0)
        self.add_start(hbox, False, False, 0)

        button = Gtk.Button(_('Rebuild System Scripts'))
        button.connect('clicked', self.on_rebuild_clicked)
        hbox.pack_end(button, False, False, 5)

    def on_enable_deleted(self, widget):
        self.disable_scripts.update_model()

    def on_enable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.disable_scripts.update_model()

    def on_disable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.enable_scripts.update_model()

    def on_rebuild_clicked(self, widget):
        dialog = QuestionDialog(message=_('This will delete all disabled scripts.\nDo you wish to continue?'))
        if dialog.run() == Gtk.ResponseType.YES:
            self.default.remove()
            self.default.create()
            self.disable_scripts.update_model()
        dialog.destroy()

    def config_test(self):
        if not os.path.exists(self.system_dir):
            self.default.create()
