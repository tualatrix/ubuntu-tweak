#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
import gtk
from ubuntutweak.modules import TweakModule
from ubuntutweak.widgets import TablePack
from ubuntutweak.widgets.dialogs import QuestionDialog
from ubuntutweak.policykit import proxy

#TODO
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.common.systeminfo import SystemInfo

class Computer(TweakModule):
    __title__ = _('Computer Details')
    __desc__ = _('Some useful information about your computer')
    __icon__ = 'computer'
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        cpumodel = _('Unknown')

        if os.uname()[4][0:3] == "ppc":
            for element in file("/proc/cpuinfo"):
                if element.split(":")[0][0:3] == "cpu":
                    cpumodel = element.split(":")[1]
        else:
            for element in file("/proc/cpuinfo"):
                if element.split(":")[0] == "model name\t":
                    cpumodel = element.split(":")[1]

        for element in file("/proc/meminfo"):
            if element.split(" ")[0] == "MemTotal:":
                raminfo = element.split(" ")[-2]

        hostname_label = gtk.Label(os.uname()[1])
        hostname_button = gtk.Button(_('Change Hostname'))
        hostname_button.connect('clicked', self.on_hostname_button_clicked, hostname_label)

        box = TablePack(_("System information"),(
                    (gtk.Label(_("Hostname")), hostname_label, hostname_button),
                    (gtk.Label(_("Distribution")), gtk.Label(SystemInfo.distro)),
                    (gtk.Label(_("Desktop environment")), gtk.Label(SystemInfo.gnome)),
                    (gtk.Label(_("Kernel")), gtk.Label(os.uname()[0]+" "+os.uname()[2])),
                    (gtk.Label(_("Platform")), gtk.Label(os.uname()[-1])),
                    (gtk.Label(_("CPU")), gtk.Label(cpumodel.strip())),
                    (gtk.Label(_("Memory")), gtk.Label(filesizeformat(str(int(raminfo) * 1024)))),
                ))
        self.add_start(box, False, False, 0)

        box = TablePack(_("User information"),(
                    (gtk.Label(_("Current user")),     gtk.Label(os.getenv("USER"))),
                    (gtk.Label(_("Home directory")),     gtk.Label(os.getenv("HOME"))),
                    (gtk.Label(_("Shell")),         gtk.Label(os.getenv("SHELL"))),
                    (gtk.Label(_("Language")),     gtk.Label(os.getenv("LANG"))),
                ))
            
        self.add_start(box, False, False, 0)

    def on_hostname_button_clicked(self, widget, label):
        dialog = QuestionDialog(_('Please enter your new hostname. It should be non-blank characters.'),
            title = _('New hostname'))

        vbox = dialog.vbox
        entry = gtk.Entry()
        vbox.pack_start(entry, False, False, 0)
        vbox.show_all()

        res = dialog.run()
        dialog.destroy()

        if res == gtk.RESPONSE_YES:
            new_name = entry.get_text()
            proxy.exec_command('hostname %s' % new_name)
            if os.popen('hostname').read().strip() == new_name:
                label.set_label(new_name)
