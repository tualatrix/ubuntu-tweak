from ubuntutweak.janitor import JanitorCachePlugin

class ThumbnailCachePlugin(JanitorCachePlugin):
    __title__ = _('Thumbnail cache')
    __category__ = 'personal'

    root_path = '~/.thumbnails'
