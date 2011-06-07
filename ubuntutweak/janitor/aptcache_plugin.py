from ubuntutweak.janitor import JanitorPlugin


class AptCachePlugin(JanitorPlugin):
    __title__ = _('Apt Cache')
    __category__ = 'system'

    def get_cruft_objects(self):
        pass

