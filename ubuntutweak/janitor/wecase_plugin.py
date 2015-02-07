from ubuntutweak.janitor import JanitorCachePlugin

class WeCaseCachePlugin(JanitorCachePlugin):
    __title__ = _('WeCase')
    __category__ = 'application'

    root_path = '~/.cache/wecase'

