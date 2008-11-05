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


import pygtk
pygtk.require("2.0")
import gtk

def show_info(message, title = None, buttons = gtk.BUTTONS_OK, type = gtk.MESSAGE_ERROR, parent = None):
    dialog = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, type, buttons)
    if title:
        dialog.set_title(title)
    dialog.set_markup(message)
    dialog.run()
    dialog.destroy()

class BaseMessageDialog(gtk.MessageDialog):
    def __init__(self, message, type, buttons):
        gtk.MessageDialog.__init__(self, None, 0, type, buttons)

        self.set_markup(message)

    def launch(self):
        self.run()
        self.destroy()

class MessageDialog(gtk.MessageDialog):
    def __init__(self, message, title = None, parent = None, flags = 0, type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_YES_NO):
        gtk.MessageDialog.__init__(self, parent, flags, type, buttons)
        self.set_markup(message)
        if title:
            self.set_title(title)
        self.set_default_response(gtk.RESPONSE_REJECT)

class InfoDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_OK):
        BaseMessageDialog.__init__(self, message, type, buttons)

class QuestionDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO):
        BaseMessageDialog.__init__(self, message, type, buttons)

class ErrorDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK):
        BaseMessageDialog.__init__(self, message, type, buttons)

class WarningDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_YES_NO):
        BaseMessageDialog.__init__(self, message, type, buttons)
