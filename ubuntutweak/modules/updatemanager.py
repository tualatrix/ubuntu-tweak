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

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import GconfCheckButton
from thirdsoft import UpdateView, refresh_source

from ubuntutweak.common.package import package_worker

class SourceEditor(TweakModule):
    __title__ = _('Update Manager')
    __desc__ = _('Freely edit your software sources to fit your needs.\n'
                'Click "Update Sources" if you want to change the sources.\n'
                'Click "Submit Sources" if you want to share your sources with other people.')
    __icon__ = 'system-software-update'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'updatemanager.ui')

        self.updateview = UpdateView()
        self.updateview.update_updates(package_worker.get_update_package())
        self.sw1.add(self.updateview)

        button = GconfCheckButton(label=_('Enable the auto launch of System Update Manager'), 
                                   key='/apps/update-notifier/auto_launch')
        self.vbox1.pack_start(button, False, False, 0)

    def reparent(self):
        self.main_vbox.reparent(self.inner_vbox)

    def on_refresh_button_clicked(self, widget):
        refresh_source(widget.get_toplevel())

        self.emit('update', 'thirdsoft', 'update_thirdparty')

    def on_select_button_clicked(self, widget):
        model = self.updateview.get_model()
        model.foreach(self.__select_foreach, widget.get_active())

    def __select_foreach(self, model, path, iter, check):
        model.set(iter, 0, check)
