# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2012 Tualatrix Chou <tualatrix@gmail.com>
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
import re
import time
import logging
import shutil

from gi.repository import GObject, Gtk
from xdg.DesktopEntry import DesktopEntry

from ubuntutweak import system
from ubuntutweak.common.debug import log_func, log_traceback
from ubuntutweak.modules  import TweakModule
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.gui.dialogs import QuestionDialog
from ubuntutweak.utils import icon

log = logging.getLogger('QuickLists')



def save_to_user(func):
    def func_wrapper(self, *args, **kwargs):
        launcher_setting = GSetting('com.canonical.Unity.Launcher.favorites')
        is_user_desktop_file = self.is_user_desktop_file()
        if not is_user_desktop_file:
            log.debug("Copy %s to user folder, then write it" % self.filename)
            shutil.copy(self.get_system_desktop_file(),
                        self.get_user_desktop_file())
            self.filename = self.get_user_desktop_file()
            self.parse(self.filename)

        func(self, *args, **kwargs)

        if not is_user_desktop_file:
            current_list = launcher_setting.get_value()
            try:
                index = current_list.index(self.get_system_desktop_file())
            except Exception, e:
                log.debug(e)
                index = current_list.index(os.path.basename(self.get_system_desktop_file()))

            current_list[index] = self.filename

            launcher_setting.set_value(current_list)
            log.debug("current_list: %s" % current_list)
            log.debug("Now set the current list")

    return func_wrapper


class NewDesktopEntry(DesktopEntry):
    shortcuts_key = 'X-Ayatana-Desktop-Shortcuts'
    actions_key = 'Actions'
    user_folder = os.path.expanduser('~/.local/share/applications')
    system_folder = '/usr/share/applications'
    mode = ''

    def __init__(self, filename):
        DesktopEntry.__init__(self, filename)
        log.debug('NewDesktopEntry: %s' % filename)
        if self.get(self.shortcuts_key):
            self.mode = self.shortcuts_key
        else:
            self.mode = self.actions_key

    def get_actions(self):
        enabled_actions = self.get(self.mode, list=True)

        actions = self.groups()
        actions.remove(self.defaultGroup)

        for action in actions: 
            action_name = self.get_action_name(action)
            if action_name not in enabled_actions:
                enabled_actions.append(action_name)

        return enabled_actions

    def get_action_name(self, action):
        if self.mode == self.shortcuts_key:
            return action.split()[0]
        else:
            return action.split()[-1]

    def add_action_group(self, action):
        self.addGroup(self.get_action_full_name(action))

    def get_action_full_name(self, action):
        if self.mode == self.shortcuts_key:
            return u'%s Shortcut Group' % action
        else:
            return u'Desktop Action %s' % action

    @log_func(log)
    def get_name_by_action(self, action):
        return self.get('Name', self.get_action_full_name(action), locale=True)

    @log_func(log)
    def get_exec_by_action(self, action):
        return self.get('Exec', self.get_action_full_name(action))

    @log_func(log)
    @save_to_user
    def set_name_by_action(self, action, name):
        # First there's must be at least one non-locale value
        if not self.get('Name', name):
            self.set('Name', name, group=self.get_action_full_name(action))
        self.set('Name', name, group=self.get_action_full_name(action), locale=True)
        self.write()

    @log_func(log)
    @save_to_user
    def set_exec_by_action(self, action, cmd):
        self.set('Exec', cmd, group=self.get_action_full_name(action))
        self.write()

    @log_func(log)
    def is_action_visiable(self, action):
        enabled_actions = self.get(self.mode, list=True)
        log.debug('All visiable actions: %s' % enabled_actions)
        return action in enabled_actions

    @log_func(log)
    @save_to_user
    def remove_action(self, action):
        actions = self.get(self.mode, list=True)
        log.debug("remove_action %s from %s" % (action, actions))
        #TODO if not local
        if action in actions:
            actions.remove(action)
            self.set(self.mode, ";".join(actions))
        self.removeGroup(self.get_action_full_name(action))
        self.write()

    @log_func(log)
    @save_to_user
    def set_action_enabled(self, action, enabled):
        actions = self.get(self.mode, list=True)

        if action not in actions and enabled:
            log.debug("Group is not in actions and will set it to True")
            actions.append(action)
            self.set(self.mode, ";".join(actions))
            self.write()
        elif action in actions and enabled is False:
            log.debug("Group is in actions and will set it to False")
            actions.remove(action)
            self.set(self.mode, ";".join(actions))
            self.write()

    @log_func(log)
    @save_to_user
    def reorder_actions(self, actions):
        visiable_actions = []
        for action in actions:
            if self.is_action_visiable(action):
                visiable_actions.append(action)

        if visiable_actions:
            self.set(self.mode, ";".join(visiable_actions))
            self.write()

    def is_user_desktop_file(self):
        return self.filename.startswith(self.user_folder)

    def _has_system_desktop_file(self):
        return os.path.exists(os.path.join(self.system_folder, os.path.basename(self.filename)))

    def get_system_desktop_file(self):
        if self._has_system_desktop_file():
            return os.path.join(self.system_folder, os.path.basename(self.filename))
        else:
            return ''

    def get_user_desktop_file(self):
        return os.path.join(self.user_folder, os.path.basename(self.filename))

    @log_func(log)
    def can_reset(self):
        return self.is_user_desktop_file() and self._has_system_desktop_file()

    @log_func(log)
    def reset(self):
        if self.can_reset():
            shutil.copy(self.get_system_desktop_file(),
                        self.get_user_desktop_file())
            # Parse a file will not destroy the old content, so destroy manually
            self.content = dict()
            self.parse(self.filename)


class QuickLists(TweakModule):
    __title__ = _('QuickLists Editor')
    __desc__ = _('Unity Launcher QuickLists Editor')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']
    __utactive__ = True

    (DESKTOP_FILE,
     DESKTOP_ICON,
     DESKTOP_NAME,
     DESKTOP_ENTRY) = range(4)

    (ACTION_NAME,
     ACTION_FULLNAME,
     ACTION_EXEC,
     ACTION_ENABLED,
     ACTION_ENTRY) = range(5)

    QUANTAL_SPECIFIC_ITEMS = {
        'unity://running-apps': _('Running Apps'),
        'unity://expo-icon': _('Workspace Switcher'),
        'unity://devices': _('Devices')
    }

    UNITY_WEBAPPS_ACTION_PATTERN = re.compile('^S\d{1}$')

    def __init__(self):
        TweakModule.__init__(self, 'quicklists.ui')

        self.launcher_setting = GSetting('com.canonical.Unity.Launcher.favorites')
        self.launcher_setting.connect_notify(self.update_launch_icon_model)

        self.action_view.get_selection().connect('changed', self.on_action_selection_changed)

        self.update_launch_icon_model()

        self.add_start(self.main_paned)

    @log_func(log)
    def update_launch_icon_model(self, *args):
        self.icon_model.clear()

        for desktop_file in self.launcher_setting.get_value():
            log.debug('Processing with "%s"...' % desktop_file)
            if desktop_file.startswith('/') and os.path.exists(desktop_file):
                path = desktop_file
            else:
                if desktop_file.startswith('application://'):
                    desktop_file = desktop_file.split('application://')[1]
                    log.debug("Desktop file for quantal: %s" % desktop_file)

                user_path = os.path.join(NewDesktopEntry.user_folder, desktop_file)
                system_path = os.path.join(NewDesktopEntry.system_folder, desktop_file)

                if os.path.exists(user_path):
                    path = user_path
                elif os.path.exists(system_path):
                    path = system_path
                else:
                    path = desktop_file

            try:
                entry = NewDesktopEntry(path)

                self.icon_model.append((path,
                                        icon.get_from_name(entry.getIcon(), size=32),
                                        entry.getName(),
                                        entry))
            except Exception, e:
                log_traceback(log)
                if path in self.QUANTAL_SPECIFIC_ITEMS.keys():
                    self.icon_model.append((path,
                                            icon.get_from_name('plugin-unityshell', size=32),
                                            self.QUANTAL_SPECIFIC_ITEMS[path],
                                            None))

        first_iter = self.icon_model.get_iter_first()
        if first_iter:
            self.icon_view.get_selection().select_iter(first_iter)

    def get_current_action_and_entry(self):
        model, iter = self.action_view.get_selection().get_selected()
        if iter:
            action = model[iter][self.ACTION_NAME]
            entry = model[iter][self.ACTION_ENTRY]
            return action, entry
        else:
            return None, None

    def get_current_entry(self):
        model, iter = self.icon_view.get_selection().get_selected()
        if iter:
            return model[iter][self.DESKTOP_ENTRY]
        else:
            return None

    def on_action_selection_changed(self, widget):
        action, entry = self.get_current_action_and_entry()
        if action and entry:
            log.debug("Select the action: %s\n"
                      "\t\t\tName: %s\n"
                      "\t\t\tExec: %s\n"
                      "\t\t\tVisiable: %s" % (action,
                                          entry.get_name_by_action(action),
                                          entry.get_exec_by_action(action),
                                          entry.is_action_visiable(action)))
            self.remove_action_button.set_sensitive(True)
            self.name_entry.set_text(entry.get_name_by_action(action))
            self.cmd_entry.set_text(entry.get_exec_by_action(action))
            self.name_entry.set_sensitive(True)
            self.cmd_entry.set_sensitive(True)
        else:
            self.remove_action_button.set_sensitive(False)
            self.name_entry.set_text('')
            self.cmd_entry.set_text('')
            self.name_entry.set_sensitive(False)
            self.cmd_entry.set_sensitive(False)

    @log_func(log)
    def on_icon_view_selection_changed(self, widget, path=None):
        model, iter = widget.get_selected()
        if iter:
            self.action_model.clear()
            self.add_action_button.set_sensitive(True)

            entry = model[iter][self.DESKTOP_ENTRY]
            if entry:
                for action in entry.get_actions():
                    if not self.UNITY_WEBAPPS_ACTION_PATTERN.search(action):
                        self.action_model.append((action,
                                    entry.get_name_by_action(action),
                                    entry.get_exec_by_action(action),
                                    entry.is_action_visiable(action),
                                    entry))
                self.redo_action_button.set_sensitive(True)
                self.action_view.columns_autosize()
                if not path:
                    first_iter = self.action_model.get_iter_first()
                    if first_iter:
                        self.action_view.get_selection().select_iter(first_iter)
                else:
                    iter = self.action_model.get_iter(path)
                    if iter:
                        self.action_view.get_selection().select_iter(iter)
            else:
                self.add_action_button.set_sensitive(False)
                self.redo_action_button.set_sensitive(False)
        else:
            self.add_action_button.set_sensitive(False)
            self.redo_action_button.set_sensitive(False)

    @log_func(log)
    def on_add_action_button_clicked(self, widget):
        entry = self.get_current_entry()
        model, icon_iter = self.icon_view.get_selection().get_selected()
        icon_path = self.icon_model.get_path(icon_iter)

        if entry:
            first = not entry.is_user_desktop_file()
            # I think 99 is enough, right?
            action_names = entry.get_actions()
            for i in range(99):
                next_name = 'Action%d' % i
                if next_name in action_names:
                    continue
                else:
                    break

            entry.add_action_group(next_name)
            entry.set_action_enabled(next_name, True)
            # Because it may be not the user desktop file, so need icon_iter to select
            icon_iter = self.icon_model.get_iter(icon_path)
            if icon_iter:
                self.icon_view.get_selection().select_iter(icon_iter)

            self.select_last_action(first=first)
            self.name_entry.grab_focus()

    @log_func(log)
    def on_remove_action_button_clicked(self, widget):
        model, iter = self.action_view.get_selection().get_selected()
        if iter:
            action_name = model[iter][self.ACTION_NAME]
            entry = model[iter][self.ACTION_ENTRY]
            log.debug("Try to remove action: %s" % action_name)
            entry.remove_action(action_name)
            log.debug('Remove: %s succcessfully' % action_name)
            model.remove(iter)
            self.select_last_action(first=True)

    def select_last_action(self, first=False):
        if first:
            last_path = len(self.action_model) - 1
        else:
            last_path = len(self.action_model)

        if last_path >= 0:
            self.on_icon_view_selection_changed(self.icon_view.get_selection(), path=last_path)

    @log_func(log)
    def on_enable_action_render(self, render, path):
        model = self.action_model
        iter = model.get_iter(path)
        entry = model[iter][self.ACTION_ENTRY]
        action = model[iter][self.ACTION_NAME]
        is_enalbed = not model[iter][self.ACTION_ENABLED]
        entry.set_action_enabled(action, is_enalbed)
        model[iter][self.ACTION_ENABLED] = is_enalbed

    @log_func(log)
    def on_redo_action_button_clicked(self, widget):
        model, iter = self.icon_view.get_selection().get_selected()
        if iter:
            name = model[iter][self.DESKTOP_NAME]

            dialog = QuestionDialog(title=_('Would you like to reset "%s"?') % name,
                                    message=_('If you continue, the actions of %s will be set to default.') % name)
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                entry = model[iter][self.DESKTOP_ENTRY]
#                log.debug("Before reset the actions is: %s" % entry.get_actions())
                entry.reset()
                log.debug("After reset the actions is: %s" % entry.get_actions())
                self.on_icon_view_selection_changed(self.icon_view.get_selection())

    @log_func(log)
    def on_icon_reset_button_clicked(self, widget):
        dialog = QuestionDialog(title=_("Would you like to reset the launcher items?"),
                                message=_('If you continue, launcher will be set to default and all your current items will be lost.'))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.launcher_setting.set_value(self.launcher_setting.get_schema_value())

    def on_icon_reordered(self, model, path, iter):
        GObject.idle_add(self._do_icon_reorder)

    def on_action_reordered(self, model, path, iter):
        GObject.idle_add(self._do_action_reorder)

    def _do_icon_reorder(self):
        new_order = []
        for row in self.icon_model:
            if system.CODENAME == 'precise':
                new_order.append(row[self.DESKTOP_FILE])
            else:
                if not row[self.DESKTOP_FILE].startswith('unity://'):
                    new_order.append('application://%s' % os.path.basename(row[self.DESKTOP_FILE]))
                else:
                    new_order.append(row[self.DESKTOP_FILE])

        if new_order != self.launcher_setting.get_value():
            log.debug("Order changed")
            self.launcher_setting.set_value(new_order)
        else:
            log.debug("Order is not changed, pass")

    def _do_action_reorder(self):
        new_order = []
        for row in self.action_model:
            new_order.append(row[self.ACTION_NAME])
            entry = row[self.ACTION_ENTRY]

        if new_order != entry.get_actions():
            log.debug("Action order changed")
            entry.reorder_actions(new_order)
        else:
            log.debug("Action order is not changed, pass")

    def on_name_and_entry_changed(self, widget):
        action, entry = self.get_current_action_and_entry()

        if action and entry:
            self.save_button.set_sensitive(self.name_entry.get_text() != entry.get_name_by_action(action) or \
                    self.cmd_entry.get_text() != entry.get_exec_by_action(action))
        else:
            self.save_button.set_sensitive(self.name_entry.get_text() and self.cmd_entry.get_text())

    def on_save_button_clicked(self, widget):
        action, entry = self.get_current_action_and_entry()
        if action and entry:
            entry.set_name_by_action(action, self.name_entry.get_text())
            entry.set_exec_by_action(action, self.cmd_entry.get_text())
            model, iter = self.action_view.get_selection().get_selected()
            path = self.action_model.get_path(iter)
            self.on_icon_view_selection_changed(self.icon_view.get_selection(), path)
