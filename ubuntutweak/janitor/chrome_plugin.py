from ubuntutweak.janitor import JanitorCachePlugin

class ChromeCachePlugin(JanitorCachePlugin):
    __title__ = _('Chrome Cache')
    __category__ = 'application'

    root_path = '~/.cache/google-chrome/Default'
