#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2009 TualatriX <tualatrix@gmail.com>
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
import pango
import gobject

from ubuntutweak.modules import TweakModule
from ubuntutweak.widgets import CellRendererButton
from ubuntutweak.widgets.dialogs import QuestionDialog, InfoDialog
from ubuntutweak.modules.thirdsoft import UpdateView

#TODO
from ubuntutweak.common.package import package_worker

(
    COLUMN_ACTION,
    COLUMN_TASK,
    COLUMN_NAME,
    COLUMN_DESC,
) = range(4)

class TaskView(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_headers_visible(False)
        self.set_rules_hint(True)
        self.model = self.__create_model()
        self.set_model(self.model)
        self.update_model()
        self.__add_columns()

        selection = self.get_selection()
        selection.select_iter(self.model.get_iter_first())

    def __create_model(self):
        '''The model is icon, title and the list reference'''
        model = gtk.ListStore(
                    gobject.TYPE_STRING, #Install status
                    gobject.TYPE_STRING,  #package name
                    gobject.TYPE_STRING,  #task name
                    gobject.TYPE_STRING,  #task description
                    )
        
        return model

    def __add_columns(self):
        column = gtk.TreeViewColumn(_('Categories'))

        renderer = gtk.CellRendererText()
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        renderer.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)
        column.pack_start(renderer, True)
        column.set_sort_column_id(COLUMN_NAME)
        column.set_attributes(renderer, markup=COLUMN_DESC)
        column.set_resizable(True)
        self.append_column(column)

        renderer = CellRendererButton()
        renderer.connect("clicked", self.on_action_clicked)
        column.pack_end(renderer, False)
        column.set_attributes(renderer, text=COLUMN_ACTION)

    def on_action_clicked(self, cell, path):
        iter = self.model.get_iter_from_string(path)
        installed = self.model.get_value(iter, COLUMN_ACTION)
        task = self.model.get_value(iter, COLUMN_TASK)
        name = self.model.get_value(iter, COLUMN_NAME)

        self.set_busy()

        if installed == 'Installed':
            #TODO install if not complete, and remove options
            dialog = InfoDialog(_('You\'ve installed the "%s" task.\n' % name))
            dialog.launch()
        else:
            updateview = UpdateView()
            updateview.set_headers_visible(False)

            list = os.popen('tasksel --task-packages %s' % task).read().split('\n')
            list = [i for i in list if i.strip()]

            updateview.update_updates(list)

            dialog = QuestionDialog(_('You are going to install the "%s" task.\nThe following packagers will be installed.' % name),
                title = _('New packages will be installed'))

            vbox = dialog.vbox
            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            sw.set_size_request(-1, 200)
            vbox.pack_start(sw, False, False, 0)
            sw.add(updateview)
            sw.show_all()

            res = dialog.run()
            dialog.destroy()

            if res == gtk.RESPONSE_YES:
                package_worker.perform_action(self.get_toplevel(), [task+'~'], [])
                package_worker.update_apt_cache(True)
                self.update_model()

        self.unset_busy()

    def update_model(self):
        self.model.clear()
        data = os.popen('tasksel --list').read().strip()

        for line in data.split('\n'):
            installed = line[0] == 'i'
            task, name = line[2:].split('\t')

            if task == 'manual':
                continue

            if installed:
                installed = _('Installed')
            else:
                installed = _('Install')

            desc = os.popen('tasksel --task-desc %s' % task).read().strip()

            iter = self.model.append()
            self.model.set(iter, 
                    COLUMN_ACTION, installed,
                    COLUMN_TASK, task,
                    COLUMN_NAME, name,
                    COLUMN_DESC, '<b>%s</b>\n%s' % (name, desc))

    def set_busy(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

    def unset_busy(self):
        window = self.get_toplevel().window
        if window:
            window.set_cursor(None)

class TaskInstall(TweakModule):
    __title__ = _('Task Install')
    __desc__ = _('Setup a full-function environment in just one-click')
    __icon__ = ['application-x-deb']
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        taskview = TaskView()

        self.add_start(taskview)
