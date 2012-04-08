from ubuntutweak.janitor import JanitorCachePlugin

class SoftwareCenterCachePlugin(JanitorCachePlugin):
    __title__ = _('Software Center Cache')
    __category__ = 'application'

    root_path = '~/.cache/software-center'
