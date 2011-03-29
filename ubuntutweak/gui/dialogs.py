# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
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

import thread

import gobject
from gi.repository import Gtk, Gdk


class BaseDialog(Gtk.MessageDialog):
    def __init__(self, **kwargs):
        title = kwargs.pop('title', '')
        message = kwargs.pop('message', '')

        gobject.GObject.__init__(self, **kwargs)

        if title:
            self.set_title(title)

        if message:
            self.set_content(message)

    def set_title(self, title):
        self.set_markup('<big><b>%s</b></big>' % title)

    def set_content(self, message):
        if self.get_property('text'):
            self.format_secondary_markup(message)
        else:
            self.set_markup(message)
    
    def launch(self):
        self.run()
        self.destroy()

    def add_option_button(self, button):
        '''Add an option button to the left. It will not grab the default response.'''
        vbox = self.get_child()
        hbuttonbox = vbox.get_children()[-1]

        hbox = Gtk.HBox(spacing=12)
        vbox.pack_start(hbox, False, False, 0)
        vbox.remove(hbuttonbox)

        new_hbuttonbox = Gtk.HButtonBox()
        new_hbuttonbox.set_layout(Gtk.ButtonBoxStyle.START)
        new_hbuttonbox.pack_start(button, True, True, 0)

        hbox.pack_start(new_hbuttonbox, True, True, 0)
        hbox.pack_start(hbuttonbox, True, True, 0)

        hbuttonbox.get_children()[-1].grab_focus()

        vbox.show_all()


class ErrorDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, type=type, buttons=buttons)


class InfoDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, type=type, buttons=buttons)


class QuestionDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, type=type, buttons=buttons)


class BusyDialog(Gtk.Dialog):
    def __init__(self, parent=None):
        gobject.GObject.__init__(self, parent=parent)

        if parent:
            self.parent_window = parent
        else:
            self.parent_window = None

    def set_busy(self):
        if self.parent_window:
            self.parent_window.window.set_cursor(Gdk.Cursor.new(Gdk.WATCH))
            self.parent_window.set_sensitive(False)

    def unset_busy(self):
        if self.parent_window:
            self.parent_window.window.set_cursor(None)
            self.parent_window.set_sensitive(True)

    def run(self):
        self.set_busy()
        return super(BusyDialog, self).run()

    def destroy(self):
        self.unset_busy()
        super(BusyDialog, self).destroy()


class ProcessDialog(BusyDialog):
    def __init__(self, parent):
        super(ProcessDialog, self).__init__(parent=parent)

        vbox = Gtk.VBox(spacing=6)
        self.vbox.add(vbox)
        self.set_border_width(8)
        self.set_title('')
        self.set_has_separator(False)
        self.set_resizable(False)

        self._label = Gtk.Label()
        self._label.set_alignment(0, 0.5)
        vbox.pack_start(self._label, False, False, 0)

        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_ellipsize(Pango.EllipsizeMode.END)
        self._progressbar.set_size_request(320, -1)
        vbox.pack_start(self._progressbar, False, False, 0)

        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.show_all()

    def run(self):
        thread.start_new_thread(self.process_data, ())
        gobject.timeout_add(100, self.on_timeout)
        super(ProcessDialog, self).run()

    def pulse(self):
        self._progressbar.pulse()

    def set_dialog_lable(self, text):
        self._label.set_markup('<b><big>%s</big></b>' % text)

    def set_progress_text(self, text):
        self._progressbar.set_text(text)

    def process_data(self):
        return NotImplemented

    def on_timeout(self):
        return NotImplemented
