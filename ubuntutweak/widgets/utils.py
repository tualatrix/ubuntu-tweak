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

import gtk
import thread
import gobject
import pango

class ProcessDialog(gtk.Dialog):
    def __init__(self, parent):
        super(ProcessDialog, self).__init__(title = '', parent = parent)

        vbox = gtk.VBox(False, 5)
        self.vbox.add(vbox)
        self.set_border_width(8)
        self.set_has_separator(False)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.__label = gtk.Label()
        vbox.pack_start(self.__label, False, False, 0)

        self.__progressbar = gtk.ProgressBar()
        self.__progressbar.set_ellipsize(pango.ELLIPSIZE_END)
        vbox.pack_start(self.__progressbar, False, False, 0)

        self.show_all()
        gobject.timeout_add(100, self.on_timeout)
        thread.start_new_thread(self.process_data, ())

    def pulse(self):
        self.__progressbar.pulse()

    def set_dialog_lable(self, text):
        self.__label.set_markup('<b><big>%s</big></b>' % text)

    def set_progress_text(self, text):
        self.__progressbar.set_text(text)

    def process_data(self):
        return NotImplemented
        
    def on_timeout(self):
        return NotImplemented
