from ubuntutweak.janitor import JanitorCachePlugin

class ChromeCachePlugin(JanitorCachePlugin):
    __title__ = _('WeCase')
    __category__ = 'application'

    root_path = '~/.cache/wecase'

