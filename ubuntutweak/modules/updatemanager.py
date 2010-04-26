n#!/usr/bin/python

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

from aptsources.sourceslist import SourcesList

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import GconfCheckButton
from ubuntutweak.widgets.dialogs import InfoDialog
from sourcecenter import UpdateView, refresh_source, UpdateCacheDialog
from ubuntutweak.policykit import proxy

from ubuntutweak.common.package import PACKAGE_WORKER

class UpdateManager(TweakModule):
    __title__ = _('Update Manager')
    __desc__ = _('A simple and easy-to-use update manager')
    __icon__ = 'system-software-update'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'updatemanager.ui')

        self.updateview = UpdateView()
        self.updateview.connect('changed', self.on_update_status_changed)
        self.update_list()
        self.sw1.add(self.updateview)

        button = GconfCheckButton(label=_('Enable auto-start of System Update Manager'), 
                                   key='/apps/update-notifier/auto_launch')
        self.vbox1.pack_start(button, False, False, 0)

        self.ppa_button = GconfCheckButton(
                            label=_('Temporarily disable third-party PPA sources whilst refreshing'),
                            key='/apps/ubuntu-tweak/disable_ppa')
        self.vbox1.pack_start(self.ppa_button, False, False, 0)

        self.reparent(self.main_vbox)

    def update_list(self):
        PACKAGE_WORKER.update_apt_cache(init=True)
        self.updateview.get_model().clear()
        self.updateview.update_updates(list(PACKAGE_WORKER.get_update_package()))

    def on_refresh_button_clicked(self, widget):
        do_ppa_disable = False
        if self.ppa_button.get_active():
            proxy.disable_ppa()
            do_ppa_disable = True

        UpdateCacheDialog(widget.get_toplevel()).run()

        PACKAGE_WORKER.update_apt_cache(True)
        self.select_button.set_active(False)

        new_updates = list(PACKAGE_WORKER.get_update_package())
        if new_updates:
            self.updateview.get_model().clear()
            self.updateview.update_updates(new_updates)
        else:
            dialog = InfoDialog(_("Your system is clean and no updates are available."),
                        title=_('Software information is now up-to-date'))

            dialog.launch()

        if do_ppa_disable:
            proxy.enable_ppa()
        self.emit('call', 'ubuntutweak.modules.sourcecenter', 'update_thirdparty', {})
        self.emit('call', 'ubuntutweak.modules.sourceeditor', 'update_source_combo', {})

    def on_select_button_clicked(self, widget):
        self.updateview.select_all_action(widget.get_active())

    def on_update_status_changed(self, widget, i):
        if i:
            self.install_button.set_sensitive(True)
        else:
            self.install_button.set_sensitive(False)

    def on_install_button_clicked(self, widget):
        PACKAGE_WORKER.perform_action(widget.get_toplevel(), self.updateview.to_add, self.updateview.to_rm)

        PACKAGE_WORKER.update_apt_cache(True)

        PACKAGE_WORKER.show_installed_status(self.updateview.to_add, self.updateview.to_rm)

        self.updateview.get_model().clear()
        self.updateview.update_updates(list(PACKAGE_WORKER.get_update_package()))
        self.select_button.set_active(False)
        self.updateview.select_all_action(False)
