import gobject
from gi.repository import Gtk

from ubuntutweak.gui import GuiBuilder

class ClipPage(Gtk.VBox, GuiBuilder):
    def __init__(self):
        gobject.GObject.__init__(self)
        GuiBuilder.__init__(self, 'clips/clippage.ui')

        #TODO
        from diskspace import DiskSpace
        from updateinfo import UpdateInfo
        from systeminfo import SystemInfo

        self.clipvbox.pack_start(DiskSpace().selfvbox, False, False, 0)
        self.clipvbox.pack_start(UpdateInfo().selfvbox, False, False, 0)
        self.clipvbox.pack_start(SystemInfo().selfvbox, False, False, 0)
