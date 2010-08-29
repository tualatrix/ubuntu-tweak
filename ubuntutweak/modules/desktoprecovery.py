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
from ubuntutweak.widgets.dialogs import ProcessDialog

log = logging.getLogger('DesktopRecovery')

def build_backup_prefix(dir):
    name_prefix = os.path.join(CONFIG_ROOT, 'desktoprecovery', dir[1:]) + '/'

    log.debug("build_backup_prefix: %s" % name_prefix)

    if not os.path.exists(name_prefix):
        os.makedirs(name_prefix)
    return name_prefix

def build_backup_path(dir, name):
    name_prefix = build_backup_prefix(dir)
    return name_prefix + name + '.xml'

def do_backup_task(dir, name):
    backup_name = build_backup_path(dir, name)
    log.debug("the backup path is %s" % backup_name)
    backup_file = open(backup_name, 'w')
    process = Popen(['gconftool-2', '--dump', dir], stdout=backup_file)
    return process.communicate()

def do_recover_task(path):
    process = Popen(['gconftool-2', '--load', path])
    log.debug('Start setting recovery: %s' % path)
    return process.communicate()

def do_reset_task(dir):
    process = Popen(['gconftool-2', '--recursive-unset', dir])
    log.debug('Start setting reset: %s' % dir)
    return process.communicate()

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
        column = gtk.TreeViewColumn(_('Category'))

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

class SettingView(gtk.TreeView):
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
        ''' The first is for icon, second is for real path, second is for title (if available)'''
        model = gtk.ListStore(gtk.gdk.Pixbuf,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Setting'))

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

class GetTextDialog(QuestionDialog):
    def __init__(self, title='', message='', text=''):
        super(GetTextDialog, self).__init__(title=title, message=message)

        self.text = text

        vbox = self.vbox

        hbox = gtk.HBox(False, 12)
        label = gtk.Label(_('Backup Name:'))
        hbox.pack_start(label, False, False, 0)

        self.entry = gtk.Entry()
        if text:
            self.entry.set_text(text)
        hbox.pack_start(self.entry)

        vbox.pack_start(hbox)
        vbox.show_all()

    def destroy(self):
        self.text = self.entry.get_text()
        super(GetTextDialog, self).destroy()

    def set_text(self, text):
        self.entry.set_text(text)

    def get_text(self):
        return self.text

class BackupProgressDialog(ProcessDialog):
    def __init__(self, parent, name, dir):
        self.file_name = name
        self.dir = dir
        self.done = False
        self.error = False

        super(BackupProgressDialog, self).__init__(parent=parent)

    def process_data(self):
        dir = self.dir
        name = self.file_name

        process = Popen(['gconftool-2', '--all-dirs', dir], stdout=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            log.error(stderr)
            #TODO raise error or others
            self.error = True
            self.done = True
            return

        dirlist = stdout.split()
        dirlist.sort()
        totol_backuped = []

        for subdir in dirlist:
            self.set_progress_text(_('Backing up...%s') % subdir)
            stdout, stderr = do_backup_task(subdir, name)
            if stderr is not None:
                log.error(stderr)
                self.error = True
                break
            else:
                totol_backuped.append(build_backup_path(subdir, name))

        if stderr is None:
            backup_name = build_backup_path(dir, name)
            sum_file = open(backup_name, 'w')
            sum_file.write('\n'.join(totol_backuped))
            sum_file.close()

        self.done = True

    def on_timeout(self):
        self.pulse()

        if not self.done:
            return True
        else:
            self.destroy()

class DesktopRecovery(TweakModule):
    __title__ = _('Desktop Recovery')
    __desc__ = _('Backup and recover your desktop and application settings with ease.\n'
                 'You can also use "Reset" to reset to the system default settings.')
    __icon__ = 'gnome-control-center'
    __category__ = 'desktop'
    __desktop__ = ['gnome']

    def __init__(self):
        TweakModule.__init__(self, 'desktoprecovery.ui')

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

        self.settingview = SettingView()
        self.setting_selection = self.settingview.get_selection()
        self.setting_selection.connect('changed', self.on_settingview_changed)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.settingview)
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

    def update_backup_model(self, dir):
        model = self.backup_combobox.get_model()
        model.clear()

        name_prefix = build_backup_prefix(dir)

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
            self.edit_button.set_sensitive(True)
            self.recover_button.set_sensitive(True)
        else:
            iter = model.append(None)
            model.set(iter, 0, _('No Backup Yet'), 1, '')
            self.backup_combobox.set_active_iter(iter)
            self.delete_button.set_sensitive(False)
            self.edit_button.set_sensitive(False)
            self.recover_button.set_sensitive(False)

    def on_cateview_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            dir = model.get_value(iter, self.cateview.COLUMN_DIR)
            self.settingview.update_model(dir)

            self.dir_label.set_text(dir)
            self.update_backup_model(dir)

    def on_cateview_button_press_event(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.on_cateview_changed(self.cate_selection)

    def on_settingview_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            dir = model.get_value(iter, self.settingview.COLUMN_DIR)
            self.dir_label.set_text(dir)
            self.update_backup_model(dir)

    def on_backup_button_clicked(self, widget):
        def get_time_stamp():
            return time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))

        dir = self.dir_label.get_text()
        log.debug("Start backing up the dir: %s" % dir)

        # if 1, then root dir
        if dir.count('/') == 1:
            dialog = GetTextDialog(message=_('Backup all settings under: <b>%s</b>\nWould you like to continue?') % dir,
                                   text=get_time_stamp())

            response = dialog.run()
            dialog.destroy()
            name = dialog.get_text()

            if response == gtk.RESPONSE_YES and name:
                dialog = BackupProgressDialog(self.get_toplevel(), name, dir)

                dialog.run()
                dialog.destroy()

                if dialog.error == False:
                    self.show_backup_successful_dialog()
                    self.update_backup_model(dir)
                else:
                    self.show_backup_failed_dialog()
        else:
            dialog = GetTextDialog(message=_('Backup settings under: <b>%s</b>\nWould you like to continue?') % dir,
                                   text=get_time_stamp())
            response = dialog.run()
            dialog.destroy()
            name = dialog.get_text()

            if response == gtk.RESPONSE_YES and name:
                stdout, stderr = do_backup_task(dir, name)

                if stderr is None:
                    self.show_backup_successful_dialog()
                    self.update_backup_model(dir)
                else:
                    self.show_backup_failed_dialog()
                    log.debug("Backup error: %s" % stderr)

    def on_delete_button_clicked(self, widget):
        def try_remove_record_in_root_backup(dir, path):
            rootpath = build_backup_prefix('/'.join(dir.split('/')[:2])) + os.path.basename(path)
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
            dialog = QuestionDialog(_('Would you like to delete the backup: <b>%s/%s</b>?') % (dir, os.path.basename(path)[:-4]))
        else:
            dialog = QuestionDialog(_('Would you like to delete the backup of all <b>%s</b> settings named <b>%s</b>?') % (dir, os.path.basename(path)[:-4]))
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
            message = _('Would you like to recover the backup: <b>%s/%s</b>?') % (dir, os.path.basename(path)[:-4])
        else:
            message = _('Would you like to recover the backup of all <b>%s</b> settings named <b>%s</b>?') % (dir, os.path.basename(path)[:-4])

        addon_message = _('<b>NOTES</b>: While recovering, your desktop may be unresponsive for a moment.')

        dialog = QuestionDialog(message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_YES:
            if dir.count('/') == 1:
                for line in open(path):
                    stdout, stderr = do_recover_task(line.strip())
            else:
                stdout, stderr = do_recover_task(path)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            InfoDialog(_('Recovery Successful!\nYou may need to restart your desktop for changes to take effect')).launch()

    def on_reset_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        dir = self.dir_label.get_text()

        if dir.count('/') == 2:
            message = _('Would you like to reset settings for: <b>%s</b>?') % dir
        else:
            message = _('Would you like to reset all settings under: <b>%s</b>?') % dir

        addon_message = _('<b>NOTES</b>: Whilst resetting, your desktop may be unresponsive for a moment.')

        dialog = QuestionDialog(message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_YES:
            if dir.count('/') == 1:
                for line in open(path):
                    stdout, stderr = do_reset_task(line.strip())
            else:
                stdout, stderr = do_reset_task(dir)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            InfoDialog(_('Reset Successful!\nYou may need to restart your desktop for changes to take effect')).launch()

    def on_edit_button_clicked(self, widget):
        def try_rename_record_in_root_backup(dir, old_path, new_path):
            rootpath = build_backup_prefix('/'.join(dir.split('/')[:2])) + os.path.basename(path)
            if os.path.exists(rootpath):
                lines = open(rootpath).read().split()
                lines.remove(old_path)
                lines.append(new_path)

                new = open(rootpath, 'w')
                new.write('\n'.join(lines))
                new.close()
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        dir = self.dir_label.get_text()
        path = model.get_value(iter, 1)

        dialog = GetTextDialog(message=_('Please enter a new name for your backup:'))

        dialog.set_text(os.path.basename(path)[:-4])
        res = dialog.run()
        dialog.destroy()
        new_name = dialog.get_text()
        log.debug('Get the new backup name: %s' % new_name)

        if res == gtk.RESPONSE_YES and new_name:
            # If is root, try to rename all the subdir, then rename itself
            if dir.count('/') == 1:
                totol_renamed = []
                for line in open(path):
                    line = line.strip()
                    dirname = os.path.dirname(line)
                    new_path = os.path.join(dirname, new_name + '.xml')
                    log.debug('Rename backup file from "%s" to "%s"' % (line, new_path))
                    os.rename(line, new_path)
                    totol_renamed.append(new_path)
                sum_file = open(path, 'w')
                sum_file.write('\n'.join(totol_renamed))
                sum_file.close()

            dirname = os.path.dirname(path)
            new_path = os.path.join(dirname, new_name + '.xml')
            log.debug('Rename backup file from "%s" to "%s"' % (path, new_path))
            os.rename(path, new_path)
            try_rename_record_in_root_backup(dir, path, new_path)

        self.update_backup_model(dir)

    def show_backup_successful_dialog(self):
        InfoDialog(_("Backup Successful!")).launch()

    def show_backup_failed_dialog(self):
        ErrorDialog(_("Backup Failed!")).launch()
