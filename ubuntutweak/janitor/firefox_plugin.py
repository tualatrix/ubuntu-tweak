import os

from ubuntutweak.janitor import JanitorCachePlugin
from ubuntutweak.settings.configsettings import RawConfigSetting

class FirefoxCachePlugin(JanitorCachePlugin):
    __title__ = _('Firefox Cache')
    __category__ = 'application'

    targets = ['Cache', 'OfflineCache', 'TestPilotErrorLog.log']

    @classmethod
    def get_path(cls):
        profiles_path = os.path.expanduser('~/.mozilla/firefox/profiles.ini')
        if os.path.exists(profiles_path):
            config = RawConfigSetting(profiles_path)
            profile_id = config.get_value('General', 'StartWithLastProfile')
            for section in config.sections():
                if section.startswith('Profile'):
                    relative_id = config.get_value(section, 'IsRelative')
                    if relative_id == profile_id:
                        return os.path.expanduser('~/.mozilla/firefox/%s' %
config.get_value(section, 'Path'))
        return self.root_path
