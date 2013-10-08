# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
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
import glob
import time
import logging
from subprocess import Popen, PIPE

import dbus
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf

from ubuntutweak.modules import TweakModule
from ubuntutweak.utils import icon
from ubuntutweak.gui.dialogs import InfoDialog, QuestionDialog, ErrorDialog
from ubuntutweak.gui.dialogs import ProcessDialog
from ubuntutweak.gui.gtk import post_ui
from ubuntutweak.common.consts import CONFIG_ROOT

log = logging.getLogger('DesktopRecovery')

def build_backup_prefix(directory):
    name_prefix = os.path.join(CONFIG_ROOT, 'desktoprecovery', directory[1:]) + '/'

    log.debug("build_backup_prefix: %s" % name_prefix)

    if not os.path.exists(name_prefix):
        os.makedirs(name_prefix)
    return name_prefix


def build_backup_path(directory, name):
    name_prefix = build_backup_prefix(directory)
    return name_prefix + name + '.xml'


def do_backup_task(directory, name):
    backup_name = build_backup_path(directory, name)
    log.debug("the backup path is %s" % backup_name)
    backup_file = open(backup_name, 'w')
    process = Popen(['gconftool-2', '--dump', directory], stdout=backup_file)
    return process.communicate()


def do_recover_task(path):
    process = Popen(['gconftool-2', '--load', path])
    log.debug('Start setting recovery: %s' % path)
    return process.communicate()


def do_reset_task(directory):
    process = Popen(['gconftool-2', '--recursive-unset', directory])
    log.debug('Start setting reset: %s' % directory)
    return process.communicate()


class CateView(Gtk.TreeView):
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
        GObject.GObject.__init__(self)

        self.set_rules_hint(True)
        self.model = self._create_model()
        self.set_model(self.model)
        self._add_columns()
        self.update_model()

        selection = self.get_selection()
        selection.select_iter(self.model.get_iter_first())

    def _create_model(self):
        '''The model is icon, title and the list reference'''
        model = Gtk.ListStore(
                    GdkPixbuf.Pixbuf,
                    GObject.TYPE_STRING,
                    GObject.TYPE_STRING)

        return model

    def _add_columns(self):
        column = Gtk.TreeViewColumn(_('Category'))

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.COLUMN_TITLE)
        column.add_attribute(renderer, 'text', self.COLUMN_TITLE)

        self.append_column(column)

    def update_model(self):
        for path, title in self.path_dict.items():
            pixbuf = icon.get_from_name('folder')
            self.model.append((pixbuf, path, title))


class SettingView(Gtk.TreeView):
    (COLUMN_ICON,
     COLUMN_DIR,
     COLUMN_TITLE
    ) = range(3)

    def __init__(self):
        GObject.GObject.__init__(self)

        self.model = self._create_model()
        self.set_model(self.model)
        self._add_columns()

    def _create_model(self):
        ''' The first is for icon, second is for real path, second is for title (if available)'''
        model = Gtk.ListStore(GdkPixbuf.Pixbuf,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)

        return model

    def _add_columns(self):
        column = Gtk.TreeViewColumn(_('Setting'))

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'pixbuf', self.COLUMN_ICON)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.set_sort_column_id(self.COLUMN_TITLE)
        column.add_attribute(renderer, 'text', self.COLUMN_TITLE)

        self.append_column(column)

    def update_model(self, directory):
        self.model.clear()

        process = Popen(['gconftool-2', '--all-dirs', directory], stdout=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            log.error(stderr)
            #TODO raise error or others
            return

        dirlist = stdout.split()
        dirlist.sort()
        for directory in dirlist:
            title = directory.split('/')[-1]

            pixbuf = icon.get_from_name(title, alter='folder')
            self.model.append((pixbuf, directory, title))


class GetTextDialog(QuestionDialog):
    def __init__(self, title='', message='', text=''):
        super(GetTextDialog, self).__init__(title=title, message=message)

        self.text = text

        vbox = self.get_content_area()

        hbox = Gtk.HBox(spacing=12)
        label = Gtk.Label(label=_('Backup Name:'))
        hbox.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        if text:
            self.entry.set_text(text)
        hbox.pack_start(self.entry, True, True, 0)

        vbox.pack_start(hbox, True, True, 0)
        vbox.show_all()

    def destroy(self):
        self.text = self.entry.get_text()
        super(GetTextDialog, self).destroy()

    def set_text(self, text):
        self.entry.set_text(text)

    def get_text(self):
        return self.text


class BackupProgressDialog(ProcessDialog):
    def __init__(self, parent, name, directory):
        self.file_name = name
        self.directory = directory
        self.error = False

        super(BackupProgressDialog, self).__init__(parent=parent)
        self.set_progress_text(_('Backing up...'))

    def run(self):
        GObject.timeout_add(100, self.process_data)
        return super(ProcessDialog, self).run()

    @post_ui
    def process_data(self):
        directory = self.directory
        name = self.file_name

        process = Popen(['gconftool-2', '--all-dirs', directory], stdout=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            log.error(stderr)
            #TODO raise error or others
            self.error = True
            return

        dirlist = stdout.split()
        dirlist.sort()
        totol_backuped = []

        length = len(dirlist)
        for index, subdir in enumerate(dirlist):
            self.set_progress_text(_('Backing up...%s') % subdir)
            self.set_fraction((index + 1.0) / length)

            while Gtk.events_pending():
                Gtk.main_iteration()

            stdout, stderr = do_backup_task(subdir, name)
            if stderr is not None:
                log.error(stderr)
                self.error = True
                break
            else:
                totol_backuped.append(build_backup_path(subdir, name))

        if stderr is None:
            backup_name = build_backup_path(directory, name)
            sum_file = open(backup_name, 'w')
            sum_file.write('\n'.join(totol_backuped))
            sum_file.close()

        self.destroy()


class DesktopRecovery(TweakModule):
    __title__ = _('Desktop Recovery')
    __desc__ = _('Backup and recover your desktop and application settings with ease.\n'
                 'You can also use "Reset" to reset to the system default settings.')
    __icon__ = 'gnome-control-center'
    __category__ = 'desktop'
    __distro__ = ['precise']

    def __init__(self):
        TweakModule.__init__(self, 'desktoprecovery.ui')

        self.setup_backup_model()

        hbox = Gtk.HBox(spacing=12)
        self.add_start(hbox)

        self.cateview = CateView()
        sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.cateview)

        #FIXME it will cause two callback for cateview changed
        self.cateview.connect('button_press_event',
                              self.on_cateview_button_press_event)
        self.cate_selection = self.cateview.get_selection()
        self.cate_selection.connect('changed', self.on_cateview_changed)
        hbox.pack_start(sw, False, False, 0)

        vpaned = Gtk.VPaned()
        hbox.pack_start(vpaned, True, True, 0)

        self.settingview = SettingView()
        self.setting_selection = self.settingview.get_selection()
        self.setting_selection.connect('changed', self.on_settingview_changed)
        sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.settingview)
        vpaned.pack1(sw, True, False)

        vpaned.pack2(self.recover_box, False, False)

        self.on_cateview_changed(self.cate_selection)
        self.show_all()

    def setup_backup_model(self):
        model = Gtk.ListStore(GObject.TYPE_STRING,
                              GObject.TYPE_STRING)

        self.backup_combobox.set_model(model)

        cell = Gtk.CellRendererText()
        self.backup_combobox.pack_start(cell, True)
        self.backup_combobox.add_attribute(cell, 'text', 0)

    def update_backup_model(self, directory):
        def file_cmp(f1, f2):
            return cmp(os.stat(f1).st_ctime, os.stat(f2).st_ctime)

        model = self.backup_combobox.get_model()
        model.clear()

        name_prefix = build_backup_prefix(directory)

        file_lsit = glob.glob(name_prefix + '*.xml')
        file_lsit.sort(cmp=file_cmp, reverse=True)

        log.debug('Use glob to find the name_prefix: %s with result: %s' % (name_prefix,
                                                                            str(file_lsit)))

        if file_lsit:
            first_iter = None
            for file_path in file_lsit:
                iter = model.append((os.path.basename(file_path)[:-4],
                                     file_path))

                if first_iter == None:
                    first_iter = iter

            self.backup_combobox.set_active_iter(first_iter)
            self.delete_button.set_sensitive(True)
            self.edit_button.set_sensitive(True)
            self.recover_button.set_sensitive(True)
        else:
            iter = model.append((_('No Backup Yet'), ''))
            self.backup_combobox.set_active_iter(iter)
            self.delete_button.set_sensitive(False)
            self.edit_button.set_sensitive(False)
            self.recover_button.set_sensitive(False)

    def on_cateview_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            directory = model.get_value(iter, self.cateview.COLUMN_DIR)
            self.settingview.update_model(directory)

            self.dir_label.set_text(directory)
            self.update_backup_model(directory)

    def on_cateview_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.on_cateview_changed(self.cate_selection)

    def on_settingview_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            directory = model.get_value(iter, self.settingview.COLUMN_DIR)
            self.dir_label.set_text(directory)
            self.update_backup_model(directory)

    def on_backup_button_clicked(self, widget):
        def get_time_stamp():
            return time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))

        directory = self.dir_label.get_text()
        log.debug("Start backing up the dir: %s" % directory)

        # if 1, then root directory
        if directory.count('/') == 1:
            dialog = GetTextDialog(message=_('Backup all settings under "<b>%s</b>"\n'
                                             'Would you like to continue?') % directory,
                                   text=get_time_stamp())

            response = dialog.run()
            dialog.destroy()
            name = dialog.get_text()

            if response == Gtk.ResponseType.YES and name:
                log.debug("Start BackupProgressDialog")
                dialog = BackupProgressDialog(self.get_toplevel(), name, directory)

                dialog.run()
                dialog.destroy()

                if dialog.error == False:
                    self.show_backup_successful_dialog()
                    self.update_backup_model(directory)
                else:
                    self.show_backup_failed_dialog()
        else:
            dialog = GetTextDialog(message=_('Backup settings under "<b>%s</b>"\n'
                                             'Would you like to continue?') % directory,
                                   text=get_time_stamp())
            response = dialog.run()
            dialog.destroy()
            name = dialog.get_text()

            if response == Gtk.ResponseType.YES and name:
                stdout, stderr = do_backup_task(directory, name)

                if stderr is None:
                    self.show_backup_successful_dialog()
                    self.update_backup_model(directory)
                else:
                    self.show_backup_failed_dialog()
                    log.debug("Backup error: %s" % stderr)

    def on_delete_button_clicked(self, widget):
        def try_remove_record_in_root_backup(directory, path):
            rootpath = build_backup_prefix('/'.join(directory.split('/')[:2])) + \
                                           os.path.basename(path)
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

        directory = self.dir_label.get_text()

        path = model.get_value(iter, 1)
        if directory.count('/') == 2:
            dialog = QuestionDialog(message=_('Would you like to delete the backup '
                                      '"<b>%s/%s</b>"?') %
                                      (directory, os.path.basename(path)[:-4]))
        else:
            dialog = QuestionDialog(message=_('Would you like to delete the backup of'
                                      ' all "<b>%(setting_name)s</b>" settings named "<b>%(backup_name)s</b>"?') % \
                                      {'setting_name': directory,
                                       'backup_name': os.path.basename(path)[:-4]})
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            if directory.count('/') == 2:
                try_remove_record_in_root_backup(directory, path)
            else:
                try_remove_all_subback(path)

            os.remove(path)
            self.update_backup_model(directory)

    def on_recover_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        directory = self.dir_label.get_text()
        path = model.get_value(iter, 1)

        if directory.count('/') == 2:
            message = _('Would you like to recover the backup "<b>%s/%s</b>"?') % (
                        directory, os.path.basename(path)[:-4])
        else:
            message = _('Would you like to recover the backup of all '
                        '"<b>%(setting_name)s</b>" settings named "<b>%(backup_name)s</b>"?') % \
                        {'setting_name': directory,
                         'backup_name': os.path.basename(path)[:-4]}

        addon_message = _('<b>NOTES</b>: While recovering, your desktop may be unresponsive for a moment.')

        dialog = QuestionDialog(message=message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            if directory.count('/') == 1:
                for line in open(path):
                    stdout, stderr = do_recover_task(line.strip())
            else:
                stdout, stderr = do_recover_task(path)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            self._show_successful_dialog(title=_('Recovery Successful!'),
                 message=_('You may need to restart your desktop for changes to take effect'))

    def _show_successful_dialog(self, title, message):
        dialog = InfoDialog(title=title, message=message)

        button = Gtk.Button(_('_Logout'))
        button.set_use_underline(True)
        button.connect('clicked', self.on_logout_button_clicked, dialog)
        dialog.add_option_button(button)

        dialog.launch()

    def on_reset_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        directory = self.dir_label.get_text()

        if directory.count('/') == 2:
            message = _('Would you like to reset settings for "<b>%s</b>"?') % directory
        else:
            message = _('Would you like to reset all settings under "<b>%s</b>"?') % directory

        addon_message = _('<b>NOTES</b>: Whilst resetting, your desktop may be unresponsive for a moment.')

        dialog = QuestionDialog(message=message + '\n\n' + addon_message)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            stdout, stderr = do_reset_task(directory)

            if stderr:
                log.error(stderr)
                #TODO raise error or others
                return
            self._show_successful_dialog(title=_('Reset Successful!'),
                 message=_('You may need to restart your desktop for changes to take effect'))

    def on_logout_button_clicked(self, widget, dialog):
        bus = dbus.SessionBus()
        object = bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
        object.get_dbus_method('Logout', 'org.gnome.SessionManager')(True)
        dialog.destroy()
        self.emit('call', 'mainwindow', 'destroy', {})

    def on_edit_button_clicked(self, widget):
        def try_rename_record_in_root_backup(directory, old_path, new_path):
            rootpath = build_backup_prefix('/'.join(directory.split('/')[:2])) + \
                                           os.path.basename(path)

            if os.path.exists(rootpath):
                lines = open(rootpath).read().split()
                lines.remove(old_path)
                lines.append(new_path)

                new = open(rootpath, 'w')
                new.write('\n'.join(lines))
                new.close()

        iter = self.backup_combobox.get_active_iter()
        model = self.backup_combobox.get_model()
        directory = self.dir_label.get_text()
        path = model.get_value(iter, 1)

        dialog = GetTextDialog(message=_('Please enter a new name for your backup:'))

        dialog.set_text(os.path.basename(path)[:-4])
        res = dialog.run()
        dialog.destroy()
        new_name = dialog.get_text()
        log.debug('Get the new backup name: %s' % new_name)

        if res == Gtk.ResponseType.YES and new_name:
            # If is root, try to rename all the subdir, then rename itself
            if directory.count('/') == 1:
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
            try_rename_record_in_root_backup(directory, path, new_path)

        self.update_backup_model(directory)

    def show_backup_successful_dialog(self):
        InfoDialog(title=_("Backup Successful!")).launch()

    def show_backup_failed_dialog(self):
        ErrorDialog(title=_("Backup Failed!")).launch()
