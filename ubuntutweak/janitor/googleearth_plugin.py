from ubuntutweak.janitor import JanitorCachePlugin


class GoogleearthCachePlugin(JanitorCachePlugin):
    __title__ = _('Google Earth Cache')
    __category__ = 'application'

    root_path = '~/.googleearth'
