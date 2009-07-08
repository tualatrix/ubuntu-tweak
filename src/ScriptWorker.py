#!/usr/bin/python
# coding: utf-8

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
import sys
import gtk
try:
    import gio
except:
    pass
import gobject
import gnomevfs
import gettext
import shutil
import subprocess

from userdir import UserdirFile
from common.consts import *
from common.debug import run_traceback
from common.widgets import ErrorDialog
from common.utils import get_command_for_type
from common.gui import GuiWorker
from common.misc import filesizeformat
from common.systeminfo import module_check

class FileChooserDialog(gtk.FileChooserDialog):
    """Show a dialog to select a folder, or to do more thing
    The default operation is select folder"""
    def __init__(self,
            title = None,
            parent = None,
            action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            ):
        gtk.FileChooserDialog.__init__(self, title, parent, action, buttons)

class FileOperationDialog:
    def __init__(self, source, destination, operation):
        self.source = gio.File(source)
        self.destination = gio.File(destination)

        worker = GuiWorker('fileoperations.glade')

        win = worker.get_object('window')
        win.connect('destroy', gtk.main_quit)

        self.pb = worker.get_object('file_progress')
        self.file_info_label = worker.get_object('file_info_label')
        self.status_label = worker.get_object('status_label')
        self.cancel_button = worker.get_object('cancel_button')
        self.cancel_button.connect('clicked', self.on_cancel)

        win.show_all()
        getattr(self, 'start_%s' % operation)()

    def progress(self, current, total):
        self.pb.set_fraction(float(current)/total)
        self.status_label.set_label(_('%s of %s') % (filesizeformat(current), filesizeformat(total)))
        while gtk.events_pending():
            gtk.main_iteration()

    def copied(self, source, result):
        try:
            source.copy_finish(result)
        except:
            gtk.main_quit()
        finally:
            gtk.main_quit()

    def start_copy(self):
        canc = gio.Cancellable()
        self.file_info_label.set_label(_('Copying "%s" to "%s"') % (self.source.get_basename(), self.destination.get_parent().get_basename()))
        self.source.copy_async(self.destination, self.copied, progress_callback=self.progress, cancellable=canc)

        gtk.main()

    def start_move(self):
        canc = gio.Cancellable()
        self.file_info_label.set_label(_('Moving "%s" to "%s"') % (self.source.get_basename(), self.destination.get_parent().get_basename()))
        self.source.move(self.destination, progress_callback=self.progress, cancellable=canc)

    def on_cancel(self, widget):
        cancel = gio.cancellable_get_current()
        os.system("echo %s>/tmp/gio" % cancel)
        if cancel:
            self.file_info_label('wow!!! cancel')
            cancel.cancel()

class FileOperation:
    """Do the real operation"""
    @classmethod
    def do_copy(cls, source, dest):
        if os.path.isfile(source):
            if not os.path.exists(dest):
                if module_check.has_gio():
                    FileOperationDialog(source, dest, 'copy')
                else:
                    shutil.copy(source, dest)
            else:
                ErrorDialog(_('The file "%s" already exists!') % dest).launch()
        elif os.path.isdir(source):
            if not os.path.exists(dest):
                shutil.copytree(source, dest)
            else:
                ErrorDialog(_('The folder "%s" already exists!') % dest).launch()

    @classmethod
    def do_move(cls, source, dest):
        if os.path.isfile(source):
            if not os.path.exists(dest):
                if module_check.has_gio():
                    FileOperationDialog(source, dest, 'move')
                else:
                    shutil.move(source, dest)
            else:
                ErrorDialog(_('The target "%s" already exists!') % dest).launch()
        elif os.path.isdir(source):
            if not os.path.exists(dest):
                shutil.move(source, dest)
            else:
                ErrorDialog(_('The target "%s" already exists!') % dest).launch()

    @classmethod
    def do_link(cls, source, dest):
        if not os.path.exists(dest):
            os.symlink(source, dest)
        else:
            ErrorDialog(_('The target "%s" already exists!') % dest).launch()

    @classmethod
    def copy(cls, source, dest):
        """Copy the file or folder with necessary notice"""
        dest = os.path.join(dest, os.path.basename(source))
        cls.do_copy(source, dest)

    @classmethod
    def copy_to_xdg(cls, source, xdg):
        if xdg == 'HOME':
            dest = os.path.join(os.path.expanduser('~'), os.path.basename(source))
        else:
            dest = os.path.join(UserdirFile()[xdg], os.path.basename(source))
        cls.do_copy(source, dest)

    @classmethod
    def move(cls, source, dest):
        """Move the file or folder with necessary notice"""
        dest = os.path.join(dest, os.path.basename(source))
        cls.do_move(source, dest)

    @classmethod
    def move_to_xdg(cls, source, xdg):
        if xdg == 'HOME':
            dest = os.path.join(os.path.expanduser('~'), os.path.basename(source))
        else:
            dest = os.path.join(UserdirFile()[xdg], os.path.basename(source))
        cls.do_move(source, dest)

    @classmethod
    def link(cls, source, dest):
        """Link the file or folder with necessary notice"""
        dest = os.path.join(dest, os.path.basename(source))
        cls.do_link(source, dest)

    @classmethod
    def link_to_xdg(cls, source, xdg):
        if xdg == 'HOME':
            dest = os.path.join(os.path.expanduser('~'), os.path.basename(source))
        else:
            dest = os.path.join(UserdirFile()[xdg], os.path.basename(source))
        cls.do_link(source, dest)

    @classmethod
    def open(cls, source):
        """Open the file with gedit"""
        exe = get_command_for_type('text/plain')
        if exe:
            if source[-1] == "root":
                cmd = ["gksu", "-m", _("Enter your password to perform the administrative tasks") , exe]
                cmd.extend(source[:-1])
            else:
                cmd = [exe]
                cmd.extend(source)
            subprocess.call(cmd)
        else:
            ErrorDialog(_("Coudn't find any text editor in your system!")).launch()

    @classmethod
    def browse(cls, source):
        """Browser the folder as root"""
        if source[-1] == "root":
            cmd = ["gksu", "-m", _("Enter your password to perform the administrative tasks") , "nautilus"]
            cmd.extend(source[:-1])
            subprocess.call(cmd)
        else:
            cmd = ["nautilus"]
            cmd.extend(source)
            subprocess.call(cmd)

    @classmethod
    def get_local_path(cls, uri):
        """Convert the URI to local path"""
        return gnomevfs.get_local_path_from_uri(uri)

class Worker:
    """The worker to do the real operation, with getattr to instrospect the operation"""
    def __init__(self, argv):
        try:
            command = argv[1]
            paras = argv[2:]

            if command in ('copy', 'move', 'link'):
                dialog = FileChooserDialog(_("Select a folder"))
                dialog.set_current_folder(os.path.expanduser('~'))
                if dialog.run() == gtk.RESPONSE_ACCEPT:
                    folder = dialog.get_filename()

                    dialog.destroy()

                    work = getattr(FileOperation, command)
                    for file in paras:
                        if file.startswith('file'):
                            file = FileOperation.get_local_path(file)
                        work(file, folder)
            elif command in ('copy_to_xdg', 'move_to_xdg', 'link_to_xdg'):
                xdg = paras[-1]
                paras = paras[:-1]

                work = getattr(FileOperation, command)

                for file in paras:
                    if file.startswith('file'):
                        file = FileOperation.get_local_path(file)
                    work(file, xdg)
            else:
                getattr(FileOperation, command)(paras)
        except:
            run_traceback('fatal')

if __name__ == "__main__":
#    ErrorDialog(`sys.argv`).launch()
    if len(sys.argv) <= 2:
        ErrorDialog(_("Please select a target (files or folders).")).launch()
    if len(sys.argv) > 2:
        Worker(sys.argv)
