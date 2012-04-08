from ubuntutweak.janitor import JanitorCachePlugin

class EmpathyCachePlugin(JanitorCachePlugin):
    __title__ = _('Empathy Cache')
    __category__ = 'application'

    root_path = '~/.cache/telepathy'
