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
import time
import logging
import shutil

from gi.repository import GObject, Gtk
from xdg.DesktopEntry import DesktopEntry

from ubuntutweak.common.debug import log_func
from ubuntutweak.modules  import TweakModule
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.gui.dialogs import QuestionDialog
from ubuntutweak.utils import icon

log = logging.getLogger('QuickLists')

LAUNCHER_SETTING = GSetting('com.canonical.Unity.Launcher.favorites')


def save_to_user(func):
    def func_wrapper(self, *args, **kwargs):
        is_user_desktop_file = self.is_user_desktop_file()
        if not is_user_desktop_file:
            log.debug("Copy %s to user folder, then write it" % self.filename)
            shutil.copy(self.get_system_desktop_file(),
                        self.get_user_desktop_file())
            self.filename = self.get_user_desktop_file()
            self.parse(self.filename)

        func(self, *args, **kwargs)

        if not is_user_desktop_file:
            current_list = LAUNCHER_SETTING.get_value()
            try:
                index = current_list.index(self.get_system_desktop_file())
            except Exception, e:
                log.debug(e)
                index = current_list.index(os.path.basename(self.get_system_desktop_file()))

            current_list[index] = self.filename

            LAUNCHER_SETTING.set_value(current_list)
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

    def get_action_full_name(self, action):
        if self.mode == self.shortcuts_key:
            return u'%s Shortcut Group' % action
        else:
            return u'Desktop Action %s' % action

    @log_func(log)
    def get_name_by_action(self, action):
        return self.get('Name', self.get_action_full_name(action))

    @log_func(log)
    def get_exec_by_action(self, action):
        return self.get('Exec', self.get_action_full_name(action))

    @log_func(log)
    def get_env_by_action(self, action):
        return self.get('TargetEnvironment', self.get_action_full_name(action))

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
            self.parse(self.filename)


class QuickLists(TweakModule):
    __title__ = _('QuickLists Editor')
    __desc__ = _('Unity Launcher QuickLists Editor')
    __icon__ = 'plugin-unityshell'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d']
    __utactive__ = False

    (DESKTOP_FILE,
     DESKTOP_ICON,
     DESKTOP_NAME,
     DESKTOP_ENTRY) = range(4)

    (ACTION_NAME,
     ACTION_FULLNAME,
     ACTION_EXEC,
     ACTION_ENABLED,
     ACTION_ENTRY) = range(5)

    def __init__(self):
        TweakModule.__init__(self, 'quicklists.ui')

        LAUNCHER_SETTING.connect_notify(self.update_launch_icon_model)

        self.action_view.get_selection().connect('changed', self.on_action_selection_changed)
        
        self.update_launch_icon_model()

        self.add_start(self.main_paned)

    @log_func(log)
    def update_launch_icon_model(self, *args):
        self.icon_model.clear()

        for desktop_file in LAUNCHER_SETTING.get_value():
            if desktop_file.startswith('/') and os.path.exists(desktop_file):
                path = desktop_file
            else:
                if os.path.exists('/usr/share/applications/%s' % desktop_file):
                    path = '/usr/share/applications/%s' % desktop_file
                else:
                    log.debug("No desktop file avaialbe in for %s" % desktop_file)
                    continue
            entry = NewDesktopEntry(path)

            self.icon_model.append((path,\
                                    icon.get_from_name(entry.getIcon(), size=32),\
                                    entry.getName(),
                                    entry))

    def on_action_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            action = model[iter][self.ACTION_NAME]
            entry = model[iter][self.ACTION_ENTRY]
            log.debug("Select the action: %s\n"
                      "\t\t\tName: %s\n"
                      "\t\t\tExec: %s\n"
                      "\t\t\tVisiable: %s" % (action,
                                          entry.get_name_by_action(action),
                                          entry.get_exec_by_action(action),
                                          entry.is_action_visiable(action)))
            self.remove_action_button.set_sensitive(True)
        else:
            self.remove_action_button.set_sensitive(False)
            self.redo_action_button.set_sensitive(False)

    def on_icon_view_selection_changed(self, widget):
        model, iter = widget.get_selected()
        if iter:
            self.action_model.clear()

            entry = model[iter][self.DESKTOP_ENTRY]
            for action in entry.get_actions():
                self.action_model.append((action,
                            entry.get_name_by_action(action),
                            entry.get_exec_by_action(action),
                            entry.is_action_visiable(action),
                            entry))
            self.redo_action_button.set_sensitive(True)
            self.action_view.columns_autosize()
        else:
            self.redo_action_button.set_sensitive(False)

    def on_remove_action_button_clicked(self, widget):
        model, iter = self.action_view.get_selection().get_selected()
        if iter:
            action_name = model[iter][self.ACTION_NAME]
            entry = model[iter][self.ACTION_ENTRY]
            log.debug("Try to remove action: %s" % action_name)
            entry.remove_action(action_name)
            log.debug('Remove: %s succcessfully' % action_name)
            model.remove(iter)

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

            dialog = QuestionDialog(title=_("Would you like to reset %s?") % name,
                                    message=_('If you continue, the actions of %s will be set to default.') % name)
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                entry = model[iter][self.DESKTOP_ENTRY]
                entry.reset()
                self.on_icon_view_selection_changed(self.icon_view.get_selection())

    @log_func(log)
    def on_icon_reset_button_clicked(self, widget):
        dialog = QuestionDialog(title=_("Would you like to reset the launcher items?"),
                                message=_('If you continue, launcher will be set to default and all your current items will be lost.'))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            LAUNCHER_SETTING.set_value(LAUNCHER_SETTING.get_schema_value())

    @log_func(log)
    def on_add_action_button_clicked(self, widget):
        pass

    def on_icon_reordered(self, model, path, iter):
        GObject.idle_add(self._do_icon_reorder)

    def on_action_reordered(self, model, path, iter):
        GObject.idle_add(self._do_action_reorder)

    def _do_icon_reorder(self):
        new_order = []
        for row in self.icon_model:
            new_order.append(row[self.DESKTOP_FILE])

        if new_order != LAUNCHER_SETTING.get_value():
            log.debug("Order changed")
            LAUNCHER_SETTING.set_value(new_order)
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
