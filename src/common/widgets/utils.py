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

import gtk
import gobject
import thread

class ProcessDialog(gtk.Dialog):
    def __init__(self, parent):
        super(ProcessDialog, self).__init__(title = '', parent = parent)

        self.__progressbar = gtk.ProgressBar()
        self.vbox.add(self.__progressbar)

        self.show_all()
        gobject.timeout_add(100, self.on_timeout)
        thread.start_new_thread(self.process_data, ())

    def pulse(self):
        self.__progressbar.pulse()

    def set_progress_text(self, text):
        self.__progressbar.set_text(text)

    def process_data(self):
        pass
        
    def on_timeout(self):
        pass
