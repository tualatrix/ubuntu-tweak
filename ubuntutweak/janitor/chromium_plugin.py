from ubuntutweak.janitor import JanitorCachePlugin

class ChromiumCachePlugin(JanitorCachePlugin):
    __title__ = _('Chromium Cache')
    __category__ = 'application'

    root_path = '~/.cache/chromium/Default'
