import os
import logging

from ubuntutweak.janitor import JanitorCachePlugin
from ubuntutweak.settings.configsettings import RawConfigSetting

log = logging.getLogger('MozillaCachePlugin')

class MozillaCachePlugin(JanitorCachePlugin):
    __category__ = 'application'

    targets = ['Cache',
               'safebrowsing',
               'startupCache',
               'thumbnails',
               'cache2',
               'OfflineCache']
    app_path = ''

    @classmethod
    def get_path(cls):
        profiles_path = os.path.expanduser('%s/profiles.ini' % cls.app_path)
        if os.path.exists(profiles_path):
            config = RawConfigSetting(profiles_path)
            try:
                profile_id = config.get_value('General', 'StartWithLastProfile')
                for section in config.sections():
                    if section.startswith('Profile'):
                        relative_id = config.get_value(section, 'IsRelative')
                        if relative_id == profile_id:
                            return os.path.expanduser('%s/%s' % (cls.cache_path, config.get_value(section, 'Path')))
            except Exception, e:
                log.error(e)
                path = config.get_value('Profile0', 'Path')
                if path:
                    return os.path.expanduser('%s/%s' % (cls.cache_path, path))
        return cls.root_path


class FirefoxCachePlugin(MozillaCachePlugin):
    __title__ = _('Firefox Cache')

    app_path = '~/.mozilla/firefox'
    cache_path = '~/.cache/mozilla/firefox'


class ThunderbirdCachePlugin(MozillaCachePlugin):
    __title__ = _('Thunderbird Cache')

    app_path = '~/.thunderbird'
    cache_path = '~/.cache/thunderbird'
