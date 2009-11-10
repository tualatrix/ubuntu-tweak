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

import gtk
import StringIO
import traceback
import webbrowser

from ubuntutweak.common.gui import GuiWorker

def run_traceback(level):
        output = StringIO.StringIO()
        exc = traceback.print_exc(file = output)

        worker = GuiWorker('traceback.ui')
        dialog = worker.get_object('%sDialog' % level.capitalize())
        textview = worker.get_object('%s_view' % level)
        buffer = textview.get_buffer()

        buffer.set_text(output.getvalue())
        if dialog.run() == gtk.RESPONSE_YES:
            webbrowser.open('https://bugs.launchpad.net/ubuntu-tweak/+filebug')
        dialog.destroy()
        output.close()
