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
from gi.repository import Gtk
import logging

from ubuntutweak import system
from ubuntutweak.modules import TweakModule
from ubuntutweak.ui import TablePack
from ubuntutweak.ui.dialogs import QuestionDialog
from ubuntutweak.policykit import proxy

#TODO
from ubuntutweak.common.misc import filesizeformat

log = logging.getLogger("AppCenter")

class Computer(TweakModule):
    __title__ = _('Computer Details')
    __desc__ = _('Some useful system information')
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

        hostname_label = Gtk.Label(label=os.uname()[1])
        hostname_button = Gtk.Button(_('Change Hostname'))
        hostname_button.connect('clicked', self.on_hostname_button_clicked, hostname_label)

        box = TablePack(_("System information"),(
                    (Gtk.Label(label=_("Hostname")), hostname_label, hostname_button),
                    (Gtk.Label(label=_("Distribution")), Gtk.Label(label=system.DISTRO)),
                    (Gtk.Label(label=_("Desktop environment")), Gtk.Label(label=system.DESKTOP_FULLNAME)),
                    (Gtk.Label(label=_("Kernel")), Gtk.Label(label=os.uname()[0]+" "+os.uname()[2])),
                    (Gtk.Label(label=_("Platform")), Gtk.Label(label=os.uname()[-1])),
                    (Gtk.Label(label=_("CPU")), Gtk.Label(label=cpumodel.strip())),
                    (Gtk.Label(label=_("Memory")), Gtk.Label(label=filesizeformat(str(int(raminfo) * 1024)))),
                ))
        self.add_start(box, False, False, 0)

        box = TablePack(_("User information"),(
                    (Gtk.Label(label=_("Current user")),     Gtk.Label(label=os.getenv("USER"))),
                    (Gtk.Label(label=_("Home directory")),     Gtk.Label(label=os.getenv("HOME"))),
                    (Gtk.Label(label=_("Shell")),         Gtk.Label(label=os.getenv("SHELL"))),
                    (Gtk.Label(label=_("Language")),     Gtk.Label(label=os.getenv("LANG"))),
                ))
            
        self.add_start(box, False, False, 0)

    def on_hostname_button_clicked(self, widget, label):
        old_name = os.uname()[1]
        dialog = QuestionDialog(_('Please enter your new hostname. Blank characters should not be used.'),
            title = _('New hostname'))

        entry = Gtk.Entry()
        dialog.add_widget(entry)

        res = dialog.run()
        new_name = entry.get_text()
        dialog.destroy()

        if res == Gtk.ResponseType.YES:
            ret = proxy.exec_command('hostname %s' % new_name)
            ret = proxy.exec_command('echo %s > /etc/hostname' % new_name)
            ret = proxy.exec_command("sed -i 's/%s/%s/g' /etc/hosts" % (old_name, new_name))
            log.debug("New name is: %s, The ret is: %s" % (new_name, ret))
            if os.popen('hostname').read().strip() == new_name:
                label.set_label(new_name)
