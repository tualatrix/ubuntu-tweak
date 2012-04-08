from ubuntutweak.janitor import JanitorCachePlugin

class OperaCachePlugin(JanitorCachePlugin):
    __title__ = _('Opera Cache')
    __category__ = 'application'

    root_path = '~/.opera/cache'
