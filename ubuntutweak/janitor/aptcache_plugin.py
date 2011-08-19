import os
import glob

from gi.repository import GObject, Gtk

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.gui.dialogs import ProcessDialog, ErrorDialog, InfoDialog
from ubuntutweak.policykit.dbusproxy import proxy

from defer import inline_callbacks, return_value

class CacheObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_size_display(self):
        return filesizeformat(self.size)

    def get_icon(self):
        return icon.get_from_name('deb')


class CleanCacheDailog(ProcessDialog):

    def __init__(self, parent, cruft_list):
        super(CleanCacheDailog, self).__init__(parent=parent)
        self.cruft_list = cruft_list

        self.set_dialog_lable(_('Cleaning Package Cache'))
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)

    def run(self):
        GObject.timeout_add(100, self.process_data)
        return super(ProcessDialog, self).run()

    def process_data(self):
        length = len(self.cruft_list)

        for index, cruft in enumerate(self.cruft_list):
            while Gtk.events_pending():
                Gtk.main_iteration()

            self.set_fraction((index + 1.0) / length)
            self.set_progress_text(_('Cleaning...%s') % cruft.get_name())
            result = proxy.delete_apt_cache_file(cruft.get_name())

            if bool(result) == False:
                self.emit('error', cruft.get_name())
                break

        self.destroy()


class AptCachePlugin(JanitorPlugin):
    __title__ = _('Apt Cache')
    __category__ = 'system'

    def __str__(self):
        return 'AptCachePlugin'

    def get_cruft(self):
        cruft_list = glob.glob('/var/cache/apt/archives/*.deb')
        cruft_list.sort()
        size = 0

        for deb in cruft_list:
            current_size = os.path.getsize(deb)
            size += current_size

            self.emit('find_object',
                      CacheObject(os.path.basename(deb), deb, size))

        self.emit('scan_finished', True, len(cruft_list), size)

    def on_dialog_error(self, widget, error_name):
        ErrorDialog(message='%s can not be removed').launch()

    def clean_cruft(self, parent, cruft):
        dialog = CleanCacheDailog(parent, cruft)
        dialog.connect('error', self.on_dialog_error)

        if dialog.run() == Gtk.ResponseType.REJECT:
            dialog.destroy()

        self.emit('cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Apt Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Apt Cache (No cache to be cleaned)')
