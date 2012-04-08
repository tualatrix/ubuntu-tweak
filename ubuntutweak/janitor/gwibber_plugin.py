from ubuntutweak.janitor import JanitorCachePlugin

class GwibberCachePlugin(JanitorCachePlugin):
    __title__ = _('Gwibber Cache')
    __category__ = 'application'

    root_path = '~/.cache/gwibber'
