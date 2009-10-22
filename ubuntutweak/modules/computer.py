#!/usr/bin/python

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
import gtk
from ubuntutweak.modules import TweakModule
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.common.systeminfo import SystemInfo
from ubuntutweak.widgets import EntryBox, ListPack

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

        box = ListPack(_("System information"),(
                    EntryBox(_("Hostname"), os.uname()[1]),
                    EntryBox(_("Distribution"), SystemInfo.distro),
                    EntryBox(_("Desktop environment"), SystemInfo.gnome),
                    EntryBox(_("Kernel"), os.uname()[0]+" "+os.uname()[2]),
                    EntryBox(_("Platform"), os.uname()[-1]),
                    EntryBox(_("CPU"), cpumodel.strip()),
                    EntryBox(_("Memory"), filesizeformat(str(int(raminfo) * 1024))),
                ))
        self.add_start(box, False, False, 0)

        box = ListPack(_("User information"),(
                    EntryBox(_("Current user"),     os.getenv("USER")),
                    EntryBox(_("Home directory"),     os.getenv("HOME")),
                    EntryBox(_("Shell"),         os.getenv("SHELL")),
                    EntryBox(_("Language"),     os.getenv("LANG")),
                ))
            
        self.add_start(box, False, False, 0)
