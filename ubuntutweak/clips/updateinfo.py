import os
import time
import stat
from gettext import ngettext

from gi.repository import Gtk

from ubuntutweak.clips import Clip
from ubuntutweak.utils import icon

class UpdateInfo(Clip):
    NO_UPDATE_WARNING_DAYS = 7

    def __init__(self):
        Clip.__init__(self)

        self.set_image_from_pixbuf(icon.get_from_name('system-software-update',
                                                      size=48))
        self.set_title(_('Your system is up-to-date'))

        label = Gtk.Label(label=self._get_last_apt_get_update_text())
        label.set_alignment(0, 0.5)

        self.set_content(label)

    # The following two function are copyed from UpdateManager/UpdateManager.py
    def _get_last_apt_get_update_hours(self):
        """
        Return the number of hours since the last successful apt-get update
      
        If the date is unknown, return "None"
        """
        if not os.path.exists("/var/lib/apt/periodic/update-success-stamp"):
            return None
        # calculate when the last apt-get update (or similar operation)
        # was performed
        mtime = os.stat("/var/lib/apt/periodic/update-success-stamp")[stat.ST_MTIME]
        ago_hours = int((time.time() - mtime) / (60*60) )
        return ago_hours

    def _get_last_apt_get_update_text(self):
        """
        return a human readable string with the information when
        the last apt-get update was run
        """
        ago_hours = self._get_last_apt_get_update_hours()
        if ago_hours is None:
            return _("It is unknown when the package information was "
                     "updated last. Please try clicking on the 'Check' "
                     "button to update the information.")
        ago_days = int( ago_hours / 24 )
        if ago_days > self.NO_UPDATE_WARNING_DAYS:
            return _("The package information was last updated %(days_ago)s "
                     "days ago.\n"
                     "Press the 'Check' button below to check for new software "
                     "updates.") % { "days_ago" : ago_days, }
        elif ago_days > 0:
            return ngettext("The package information was last updated %(days_ago)s day ago.",
                            "The package information was last updated %(days_ago)s days ago.",
                            ago_days) % { "days_ago" : ago_days, }
        elif ago_hours > 0:
            return ngettext("The package information was last updated %(hours_ago)s hour ago.",
                            "The package information was last updated %(hours_ago)s hours ago.",
                            ago_hours) % { "hours_ago" : ago_hours, }
        else:
            return _("The package information was last updated less than one hour ago.")
        return None
