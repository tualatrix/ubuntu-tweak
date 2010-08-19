# Ubuntu Tweak - magic tool to configure Ubuntu
#
# Copyright (C) 2010 TualatriX <tualatrix@gmail.com>
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
import glob
import time
import gobject
import logging

from subprocess import Popen, PIPE

from ubuntutweak.utils import icon
from ubuntutweak.common.consts import CONFIG_ROOT
from ubuntutweak.common.gui import GuiWorker
from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets.dialogs import InfoDialog, QuestionDialog, ErrorDialog

log = logging.getLogger('DesktopRecover')

class CateView(gtk.TreeView):
    (COLUMN_ICON,
     COLUMN_DIR,
     COLUMN_TITLE
    ) = range(3)

    path_dict = {
        '/apps': _('Applications'),
        '/desktop': _('Desktop'),
        '/system': _('System'),
    }

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()
        self.update_model()

        selection = self.get_selection()
        selection.select_iter(self.model.get_iter_first())

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gtk.gdk.Pixbuf,
                    gobject.TYPE_STRING,
                    gobject.TYPE_STRING)

        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Categories'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=self.COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.COLUMN_TITLE)
        column.set_attributes(renderer, text=self.COLUMN_TITLE)

        self.append_column(column)

    def update_model(self):
        for path, title in self.path_dict.items():
            pixbuf = icon.get_from_name('folder', size=24)
            iter = self.model.append(None)
            self.model.set(iter,
                           self.COLUMN_ICON, pixbuf,
                           self.COLUMN_DIR, path,
                           self.COLUMN_TITLE, title)

class KeyDirView(gtk.TreeView):
    (COLUMN_ICON,
     COLUMN_DIR,
     COLUMN_TITLE
    ) = range(3)

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.model = self.__create_model()
        self.set_model(self.model)
        self.__add_columns()

    def __create_model(self):
        ''' The first is for icon, second is for real path, second is for title (if availabel)'''
        model = gtk.ListStore(gtk.gdk.Pixbuf,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('KeyDir'))

        renderer = gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.set_attributes(renderer, pixbuf=self.COLUMN_ICON)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.COLUMN_TITLE)
        column.set_attributes(renderer, text=self.COLUMN_TITLE)

        self.append_column(column)

    def update_model(self, dir):
        self.model.clear()
        
        process = Popen(['gconftool-2', '--all-dirs', dir], stdout=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            log.error(stderr)
            #TODO raise error or others
            return

        dirlist = stdout.split()
        dirlist.sort()
        for dir in dirlist:
            title = dir.split('/')[-1]

            pixbuf = icon.get_from_name(title, alter='folder', size=24)
            iter = self.model.append(None)
            self.model.set(iter,
                           self.COLUMN_ICON, pixbuf,
                           self.COLUMN_DIR, dir,
                           self.COLUMN_TITLE, title)

class DesktopRecover(TweakModule):
    __title__ = _('Desktop Recover')
    __desc__ = _('Backup and recover your desktop and applications setting easily')
    __icon__ = 'gconf-editor'
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self, 'desktoprecover.ui')

        self.setup_backup_model()

        hbox = gtk.HBox(False, 5)
        self.add_start(hbox)

        self.cateview = CateView()
        #FIXME it will cause two callback for cateview changed
        self.cateview.connect('button_press_event', self.on_cateview_button_press_event)
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_cateview_changed)
        hbox.pack_start(self.cateview, False, False, 0)

        vpaned = gtk.VPaned()
        hbox.pack_start(vpaned)

        self.keydirview = KeyDirView()
        self.keydir_selection = self.keydirview.get_selection()
        self.keydir_selection.connect('changed', self.on_keydirview_changed)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.keydirview)
        vpaned.pack1(sw, True, False)

        self.window1.remove(self.recover_box)
        vpaned.pack2(self.recover_box, False, False)

        self.on_cateview_changed(self.cate_selection)
        self.show_all()

    def setup_backup_model(self):
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        self.backup_combobox.set_model(model)

        cell = gtk.CellRendererText()
        self.backup_combobox.pack_start(cell, True)
        self.backup_combobox.add_attribute(cell, 'text', 0)

    def build_backup_prefix(self, dir):
        name_prefix = os.path.join(CONFIG_ROOT, 'desktoprecover', dir[1:]) + '/'

        log.debug("build_backup_prefix: %s" % name_prefix)

        if not os.path.exists(name_prefix):
            os.makedirs(name_prefix)
        return name_prefix

    def build_backup_path(self, dir):
        name_prefix = self.build_backup_prefix(dir)
        timeformat = '%Y-%m-%d-%H-%M.xml'
        return name_prefix + time.strftime(timeformat, time.localtime(time.time()))

    def update_backup_model(self, dir):
        model = self.backup_combobox.get_model()
        model.clear()

        name_prefix = self.build_backup_prefix(dir)

        file_lsit = glob.glob(name_prefix + '*.xml')
        file_lsit.sort(reverse=True)
        log.debug('Use glob to find the name_prefix: %s with result: %s' % (name_prefix, str(file_lsit)))
        if file_lsit:
            first_iter = None
            for file in file_lsit:
                iter = model.append(None)
                if first_iter == None:
                    first_iter = iter
                model.set(iter,
                        0, os.path.basename(file)[:-4],
                          1, file)
            self.backup_combobox.set_active_iter(first_iter)
            self.delete_button.set_sensitive(True)
        else:
            iter = model.append(None)
            model.set(iter, 0, _('No Backup yet'), 1, '')
            self.backup_combobox.set_active_iter(iter)
            self.delete_button.set_sensitive(False)

    def on_cateview_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            dir = model.get_value(iter, self.cateview.COLUMN_DIR)
            self.keydirview.update_model(dir)

            self.dir_label.set_text(dir)
            self.update_backup_model(dir)

    def on_cateview_button_press_event(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.on_cateview_changed(self.cate_selection)

    def on_keydirview_changed(self, widget):
        model, rows = widget.get_selected_rows()
        if len(rows) > 2:
            #TODO
            pass
        elif len(rows) == 1:
            model, iter = widget.get_selected()

            dir = model.get_value(iter, self.keydirview.COLUMN_DIR)
            self.dir_label.set_text(dir)
            self.update_backup_model(dir)
        else:
            #TODO
            pass

    def do_backup_task(self, dir):
        backup_name = self.build_backup_path(dir)
        log.debug("the backup path is %s" % backup_name)
        backup_file = open(backup_name, 'w')
        process = Popen(['gconftool-2', '--dump', dir], stdout=backup_file)
        return process.communicate()

    def do_recover_task(self, path):
        process = Popen(['gconftool-2', '--load', path])
        log.debug('Start recover the setting: %s' % path)
        return process.communicate()

    def do_reset_task(self, dir):
        process = Popen(['gconftool-2', '--recursive-unset', dir])
        log.debug('Start reset the setting: %s' % dir)
        return process.communicate()

    def on_backup_button_clicked(self, widget):
        dir = self.dir_label.get_text()
        log.debug("Start backup the dir: %s" % dir)

        # if 1, then root dir
        if dir.count('/') == 1:
            dialog = QuestionDialog(_('Will start to backup all the settings under <b>%s</b>.\nWould you like to continue?') % dir)
            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_YES:
                process = Popen(['gconftool-2', '--all-dirs', dir], stdout=PIPE)
                stdout, stderr = process.communicate()
                if stderr:
                    log.error(stderr)
                    #TODO raise error or others
                    return

                dirlist = stdout.split()
                dirlist.sort()
                totol_backuped = []

                for subdir in dirlist:
                    stdout, stderr = self.do_backup_task(subdir)
                    if stderr is not None:
                        break
                    else:
                        totol_backuped.append(self.build_backup_path(subdir))

                if stderr is None:
                    backup_name = self.build_backup_path(dir)
                    sum_file = open(backup_name, 'w')
                    sum_file.write('\n'.join(totol_backuped))
                    sum_file.close()

                    InfoDialog("Backuped Successfully").launch()
                    self.update_backup_model(dir)
                else:
                    log.debug("Backup error: %s" % stderr)
        else:
            stdout, stderr = self.do_backup_task(dir)

            if stderr is None:
                InfoDialog("Backuped Successfully").launch()
                self.update_backup_model(dir)
            else:
                log.debug("Backup error: %s" % stderr)

    def on_delete_button_clicked(self, widget):
        def try_remove_record_in_root_backup(dir, path):
            rootpath = self.build_backup_prefix('/'.join(dir.split('/')[:2])) + os.path.basename(path)
            if os.path.exists(rootpath):
                lines = open(rootpath).read().split()
                lines.remove(path)

                if len(lines) == 0:
                    os.remove(rootpath)
                else:
                    new = open(rootpath, 'w')
                    new.write('\n'.join(lines))
                    new.close()

        def try_remove_all_subback(path):
            for line in open(path):
                os.remove(line.strip())

        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()

        dir = self.dir_label.get_text()

        path = model.get_value(iter, 1)
        if dir.count('/') == 2:
            dialog = QuestionDialog(_('Would you like to delete the backup record: %s, %s ?') % (dir, os.path.basename(path)))
        else:
            dialog = QuestionDialog(_('Would you like to delete the backup record set under %s with time %s ?') % (dir, os.path.basename(path)))
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            if dir.count('/') == 2:
                try_remove_record_in_root_backup(dir, path)
            else:
                try_remove_all_subback(path)

            os.remove(path)
            self.update_backup_model(dir)

    def on_recover_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        dir = self.dir_label.get_text()
        path = model.get_value(iter, 1)

        if dir.count('/') == 2:
            message = _('Would you like to recover the backup record: %s, %s ?') % (dir, os.path.basename(path))
        else:
            message = _('Would you like to recover all the backup record set under %s with time %s ?') % (dir, os.path.basename(path))

        addon_message = _('<b>Notes:</b>While recovery, your desktop will enter a short time no-reponse, please be standby')

        dialog = QuestionDialog(message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_YES:
            if dir.count('/') == 1:
                for line in open(path):
                    stdout, stderr = self.do_recover_task(line.strip())
            else:
                stdout, stderr = self.do_recover_task(path)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            InfoDialog(_('Recover successfully!\nYou may need to restart your desktop to take effect')).launch()

    def on_reset_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        dir = self.dir_label.get_text()

        if dir.count('/') == 2:
            message = _('Would you like to reset the setting: %s ?' % dir)
        else:
            message = _('Would you like to reset all the settings under %s?' % dir)

        addon_message = _('<b>Notes:</b>While reset, your desktop will enter a short time no-reponse, please be standby')

        dialog = QuestionDialog(message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_YES:
            if dir.count('/') == 1:
                for line in open(path):
                    stdout, stderr = self.do_reset_task(line.strip())
            else:
                stdout, stderr = self.do_reset_task(dir)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            InfoDialog(_('Reset successfully!\nYou may need to restart your desktop to take effect')).launch()
