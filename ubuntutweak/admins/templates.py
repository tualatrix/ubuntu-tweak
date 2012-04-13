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
import shutil
import logging

from gi.repository import Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.admins.userdir import UserdirFile
from ubuntutweak.common.consts import DATA_DIR, CONFIG_ROOT
from ubuntutweak.gui.treeviews import DirView, FlatView
from ubuntutweak.gui.dialogs import ErrorDialog, QuestionDialog
from ubuntutweak.utils import set_label_for_stock_button


log = logging.getLogger("Templates")


def update_dir():
    system_dir = os.path.join(CONFIG_ROOT, 'templates')


    uf = UserdirFile()
    template_dir = uf['XDG_TEMPLATES_DIR']
    if not template_dir:
        template_dir = os.path.expanduser('~/Templates')
        if not os.path.exists(template_dir):
            os.mkdir(template_dir)
        user_dir = template_dir
    user_dir = template_dir

    return system_dir, user_dir


def is_right_path():
    if (os.path.expanduser('~').strip('/') == USER_DIR.strip('/')) or os.path.isfile(USER_DIR):
        return False
    else:
        return True


SYSTEM_DIR, USER_DIR = update_dir()


class DefaultTemplates:
    """This class use to create the default templates"""
    templates = {
            "html-document.html": _("HTML document"),
            "odb-database.odb": _("ODB Database"),
            "ods-spreadsheet.ods": _("ODS Spreadsheet"),
            "odt-document.odt": _("ODT Document"),
            "plain-text-document.txt": _("Plain text document"),
            "odp-presentation.odp": _("ODP Presentation"),
            "python-script.py": _("Python script"),
            "pygtk-example.py": _("Pygtk Example"),
            "shell-script.sh": _("Shell script")
            }

    def create(self):
        if not os.path.exists(SYSTEM_DIR):
            os.makedirs(SYSTEM_DIR)
        for path, des in self.templates.items():
            realname = "%s.%s" % (des, path.split('.')[1])
            if not os.path.exists(os.path.join(SYSTEM_DIR, realname)):
                shutil.copy(os.path.join(DATA_DIR, 'templates/%s' % path), os.path.join(SYSTEM_DIR, realname))

    def remove(self):
        if not os.path.exists(SYSTEM_DIR):
            return
        if os.path.isdir(SYSTEM_DIR):
            for root, dirs, files in os.walk(SYSTEM_DIR, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    os.rmdir(SYSTEM_DIR)
        else:
            os.unlink(SYSTEM_DIR)
        return


class EnableTemplate(DirView):
    """The treeview to display the enable templates"""
    type = _("Enabled Templates")

    def __init__(self):
        DirView.__init__(self, USER_DIR)


class DisableTemplate(FlatView):
    """The treeview to display the system template"""
    type = _("Disabled Templates")

    def __init__(self):
        FlatView.__init__(self, SYSTEM_DIR, USER_DIR)


class Templates(TweakModule):
    __title__ = _('Templates')
    __desc__ = _('Here you can manage your document templates.\n'
                 'You can add files as templates by dragging them into this window.\n'
                 'You can then create new documents based on these templates from the Nautilus right-click menu.')
    __icon__ = 'x-office-document'
    __utactive__ = True
    __category__ = 'personal'

    def __init__(self):
        TweakModule.__init__(self, 'templates.ui')

        if not is_right_path():
            label = Gtk.Label(label=_('The templates path is incorrect! The current path points to "%s".\nPlease reset it to a location within your Home Folder.') % USER_DIR)

            hbox = Gtk.HBox()
            self.add_start(hbox, False, False, 0)

            hbox.pack_start(label, False, False, 0)

            button = Gtk.Button(stock=Gtk.STOCK_GO_FORWARD)
            button.connect('clicked', self.on_go_button_clicked)
            set_label_for_stock_button(button, _('Go And Set'))
            hbox.pack_end(button, False, False, 0)

            button = Gtk.Button(stock=Gtk.STOCK_EXECUTE)
            button.connect('clicked', self.on_restart_button_clicked)
            set_label_for_stock_button(button, _('Restart This Module'))
            hbox.pack_end(button, False, False, 0)
        else:
            self.create_interface()

    def create_interface(self):
        self.default = DefaultTemplates()
        self.config_test()

        self.add_start(self.hbox1)
        self.show_all()

        self.enable_templates = EnableTemplate()
        self.sw1.add(self.enable_templates)

        self.disable_templates = DisableTemplate()
        self.sw2.add(self.disable_templates)

        hbox = Gtk.HBox(spacing=0)
        self.add_start(hbox, False, False, 0)

        self.enable_templates.connect('drag_data_received', self.on_enable_drag_data_received)
        self.enable_templates.connect('deleted', self.on_enable_deleted)
        self.disable_templates.connect('drag_data_received', self.on_disable_drag_data_received)

        button = Gtk.Button(_("Rebuild System Templates"))
        button.connect("clicked", self.on_rebuild_clicked)
        hbox.pack_end(button, False, False, 5)

    def on_go_button_clicked(self, widget):
        #TODO emit signal to load Userdir
        pass

    def on_restart_button_clicked(self, widget):
        global SYSTEM_DIR, USER_DIR
        SYSTEM_DIR, USER_DIR = update_dir()
        if is_right_path():
            self.remove_all_children()
            self.create_interface()
        else:
            ErrorDialog(message=_('The templates path is still incorrect, please reset it!')).launch()

    def on_enable_deleted(self, widget):
        self.disable_templates.update_model()

    def on_enable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.disable_templates.update_model()

    def on_disable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.enable_templates.update_model()

    def on_rebuild_clicked(self, widget):
        dialog = QuestionDialog(message=_('This will delete all disabled templates.\n'
                                 'Do you wish to continue?'))
        if dialog.run() == Gtk.ResponseType.YES:
            self.default.remove()
            self.default.create()
            self.disable_templates.update_model()
        dialog.destroy()

    def config_test(self):
        #TODO need to test dir with os.R_OK | os.W_OK | os.X_OK
        if not os.path.exists(SYSTEM_DIR):
            self.default.create()
