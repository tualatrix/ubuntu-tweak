#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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

from ubuntutweak0.modules import TweakModule
from ubuntutweak0.ui import CellRendererButton
from ubuntutweak0.ui.dialogs import QuestionDialog, InfoDialog, WarningDialog
from ubuntutweak0.modules.sourcecenter import UpdateView
from ubuntutweak0.common.package import PACKAGE_WORKER, PackageInfo

TASKS = {
    'server': (_('Basic Ubuntu server'), _('This task provides the Ubuntu server environment.')),
    'eucalyptus-simple-cluster': (_('Cloud computing cluster'), _('Combined Eucalyptus cloud and cluster controllers.')),
    'eucalyptus-node': (_('Cloud computing node'), _('Eucalyptus node controller.')),
    'dns-server': (_('DNS server'), _('Selects the BIND DNS server and its documentation.')),
    'edubuntu-server': (_('Edubuntu server'), _('This task provides the Edubuntu classroom server.')),
    'lamp-server': (_('LAMP server'), _('Selects a ready-made Linux/Apache/MySQL/PHP server.')),
    'mail-server': (_('Mail server'), _('This task selects a variety of package useful for a general purpose mail server system.')),
    'openssh-server': (_('OpenSSH server'), _('Selects packages needed for an OpenSSH server.')),
    'postgresql-server': (_('PostgreSQL database'), _('This task selects client and server packages for the PostgreSQL database. . PostgreSQL is an SQL relational database, offering increasing SQL92 compliance and some SQL3 features.  It is suitable for use with multi-user database access, through its facilities for transactions and fine-grained locking.')),
    'print-server': (_('Print server'), _('This task sets up your system to be a print server.')),
    'samba-server': (_('Samba file server'), _('This task sets up your system to be a Samba file server, which is  especially suitable in networks with both Windows and Linux systems.')),
    'tomcat-server': (_('Tomcat Java server'), _('Selects a ready-made Java Application server.')),
    'uec': (_('Ubuntu Enterprise Cloud (instance)'), _('Packages included in UEC images.')),
    'virt-host': (_('Virtual Machine host'), _('Packages necessary to host virtual machines')),
    'ubuntustudio-graphics': (_('2D/3D creation and editing suite'), _('2D/3D creation and editing suite')),
    'ubuntustudio-audio': (_('Audio creation and editing suite'), _('Audio creation and editing suite')),
    'edubuntu-desktop-kde': (_('Edubuntu KDE desktop'), _('This task provides the Edubuntu desktop environment (KDE variant).')),
    'edubuntu-desktop-gnome': (_('Edubuntu desktop'), _('This task provides the Edubuntu desktop environment.')),
    'kubuntu-desktop': (_('Kubuntu desktop'), _('This task provides the Kubuntu desktop environment.')),
    'kubuntu-netbook': (_('Kubuntu netbook'), _('This task provides the Kubuntu desktop environment optimized for netbooks.')),
    'ubuntustudio-audio-plugins': (_('LADSPA and DSSI audio plugins'), _('LADSPA and DSSI audio plugins')),
    'ubuntustudio-font-meta': (_('Large selection of font packages'), _('Large selection of font packages')),
    'mythbuntu-desktop': (_('Mythbuntu additional roles'), _('This task provides Mythbuntu roles for an existing system.')),
    'mythbuntu-frontend': (_('Mythbuntu frontend'), _('This task installs a MythTV frontend. It needs an existing master backend somewhere on your network.')),
    'mythbuntu-backend-master': (_('Mythbuntu master backend'), _('This task installs a MythTV master backend and a mysql server server system.')),
    'mythbuntu-backend-slave': (_('Mythbuntu slave backend'), _('This task installs a MythTV slave backend. It needs an existing master backend somewhere on your network.')),
    'mobile-mid': (_('Ubuntu MID edition'), _('This task provides the Ubuntu MID environment.')),
    'ubuntu-netbook-remix': (_('Ubuntu Netbook Remix'), _('This task provides the Ubuntu Netbook Remix environment.')),
    'ubuntu-desktop': (_('Ubuntu desktop'), _('This task provides the Ubuntu desktop environment.')),
    'ubuntustudio-video': (_('Video creation and editing suite'), _('Video creation and editing suite')),
    'xubuntu-desktop': (_('Xubuntu desktop'), _('This task provides the Xubuntu desktop environment.')),
    'edubuntu-dvd-live': (_('Edubuntu live DVD'), _('This task provides the extra packages installed on the Ubuntu live DVD, above and beyond those included on the Ubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'kubuntu-netbook-live': (_('Kubuntu Netbook Edition live CD'), _('This task provides the extra packages installed on the Kubuntu Netbook live CD. It is neither useful nor recommended to install this task in other environments.')),
    'kubuntu-live': (_('Kubuntu live CD'), _('This task provides the extra packages installed on the Kubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'kubuntu-dvd-live': (_('Kubuntu live DVD'), _('This task provides the extra packages installed on the Kubuntu live DVD, above and beyond those included on the Kubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'mythbuntu-live': (_('Mythbuntu live CD'), _('This task provides the extra packages installed on the Mythbuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'mobile-live': (_('Ubuntu MID live environment'), _('This task provides the extra packages installed in the Ubuntu MID live environment. It is neither useful nor recommended to install this task in other environments.')),
    'unr-live': (_('Ubuntu Netbook Remix live environment'), _('This task provides the extra packages installed in the Ubuntu Netbook Remix live environment. It is neither useful nor recommended to install this task in other environments.')),
    'ubuntu-live': (_('Ubuntu live CD'), _('This task provides the extra packages installed on the Ubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'ubuntu-dvd-live': (_('Ubuntu live DVD'), _('This task provides the extra packages installed on the Ubuntu live DVD, above and beyond those included on the Ubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
    'xubuntu-live': (_('Xubuntu live CD'), _('This task provides the extra packages installed on the Xubuntu live CD. It is neither useful nor recommended to install this task in other environments.')),
}

class TaskView(gtk.TreeView):
    (COLUMN_ACTION,
     COLUMN_TASK,
     COLUMN_NAME,
     COLUMN_DESC,
    ) = range(4)

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
        column.set_sort_column_id(self.COLUMN_NAME)
        column.set_attributes(renderer, markup=self.COLUMN_DESC)
        column.set_resizable(True)
        self.append_column(column)

        renderer = CellRendererButton()
        renderer.connect("clicked", self.on_action_clicked)
        column.pack_end(renderer, False)
        column.set_attributes(renderer, text=self.COLUMN_ACTION)

    def create_task_dialog(self, title, desc, updateview):
        dialog = QuestionDialog(desc, title=title)
        vbox = dialog.vbox
        swindow = gtk.ScrolledWindow()
        swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swindow.set_size_request(-1, 200)
        vbox.pack_start(swindow, False, False, 0)
        swindow.add(updateview)
        swindow.show_all()

        return dialog

    def filter_remove_packages(self, string):
        pkgs_list = [pkg.strip('-') for pkg in string.split() if pkg.endswith('-') and pkg != '--']

        new_list = []
        for pkg in pkgs_list:
            if PackageInfo(pkg).check_installed():
                new_list.append(pkg)

        return new_list

    def on_action_clicked(self, cell, path):
        iter = self.model.get_iter_from_string(path)
        installed = self.model.get_value(iter, self.COLUMN_ACTION)
        task = self.model.get_value(iter, self.COLUMN_TASK)
        name = self.model.get_value(iter, self.COLUMN_NAME)

        self.set_busy()
        updateview = UpdateView()
        updateview.set_headers_visible(False)

        if installed == 'Installed':
            dialog = InfoDialog(_('You\'ve installed the <b>"%s"</b> task.' % name))
            dialog.add_button(_('Remove'), gtk.RESPONSE_YES)
            res = dialog.run()
            dialog.destroy()
            if res == gtk.RESPONSE_YES:
                dialog = WarningDialog(_('It is dangerous to remove a task, it may remove the desktop related packages.\nPlease only continue when you know what you are doing.'),
                         title=_("Dangerous!"))
                res = dialog.run()
                dialog.destroy()

                if res == gtk.RESPONSE_YES:
                    data = os.popen('tasksel -t remove %s' % task).read()
                    pkgs = self.filter_remove_packages(data)
                    updateview.update_updates(pkgs)
                    updateview.select_all_action(True)

                    dialog = self.create_task_dialog(title=_('Packages will be removed'),
                            desc = _('You are going to remove the <b>"%s"</b> task.\nThe following packages will be remove.' % name),
                            updateview=updateview)

                    res = dialog.run()
                    dialog.destroy()

                    if res == gtk.RESPONSE_YES:
                        PACKAGE_WORKER.perform_action(self.get_toplevel(), [], updateview.to_add)
                        PACKAGE_WORKER.update_apt_cache(True)
                        self.update_model()
        else:
            list = os.popen('tasksel --task-packages %s' % task).read().split('\n')
            list = [pkg for pkg in list if pkg.strip() and not PackageInfo(pkg).check_installed()]

            updateview.update_updates(list)
            updateview.select_all_action(True)

            dialog = self.create_task_dialog(title=_('New packages will be installed'),
                    desc = _('You are going to install the <b>"%s"</b> task.\nThe following packager will be installed.' % name),
                    updateview=updateview)

            res = dialog.run()
            dialog.destroy()

            if res == gtk.RESPONSE_YES:
                PACKAGE_WORKER.perform_action(self.get_toplevel(), updateview.to_add, [])
                PACKAGE_WORKER.update_apt_cache(True)
                self.update_model()

        print self.model.get_value(iter, self.COLUMN_ACTION)

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

            name, desc = TASKS[task]
            iter = self.model.append()
            self.model.set(iter, 
                    self.COLUMN_ACTION, installed,
                    self.COLUMN_TASK, task,
                    self.COLUMN_NAME, name,
                    self.COLUMN_DESC, '<b>%s</b>\n%s' % (name, desc))

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
    __desc__ = _('Setup a full-function environment with just one-click\n'
                 'If you want to remove a task, click the "Installed" button')
    __icon__ = ['application-x-deb']
    __category__ = 'system'
    #TODO Maybe set active again
    __utactive__ = False

    def __init__(self):
        TweakModule.__init__(self)

        taskview = TaskView()

        self.add_start(taskview)
