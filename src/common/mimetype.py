from gettext import gettext as _

ARCHIVE_MIME = [
    'application/x-rpm',
    'application/x-compressed-tar',
    'application/zip',
    'application/x-bzip-compressed-tar',
    'application/x-java-archive',
    'application/x-lzma-compressed-tar',
    'application/x-rar',
    'application/x-deb',
]

IMAGE_MIME = [
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/x-ico',
]

VIDEO_MIME = [
    'video/ogg',
    'video/quicktime',
    'video/x-flv',
    'video/x-matroska',
    'video/x-msvideo',
    'video/x-theora+ogg',
    'application/vnd.rn-realmedia',
]

APP_MIME = [
    'application/x-ms-dos-executable',
]

TEXT_MIME = [
    'text/html',
    'text/plain',
    'text/x-gettext-translation',
    'text/x-tex',
    'text/x-log',
    'text/x-copying',
    'text/x-install',
    'text/x-readme',
    'text/x-python',
    'text/x-sql',
    'application/x-shellscript',
    'application/javascript',
    'application/x-php',
    'application/xml',
    'application/x-m4',
    'text/x-objcsrc',
    'text/x-chdr',
    'application/x-subrip',
    'application/x-cue',
]

DOCUMENT_MIME = [
    'application/vnd.ms-excel',
    'application/vnd.oasis.opendocument.text',
    'application/msword',
    'application/vnd.ms-powerpoint',
    'application/pdf',
    'application/x-dvi',
]

AUDIO_MIME = [
    'audio/mpeg',
    'audio/x-vorbis+ogg',
    'audio/x-wav',
]

MIMETYPE = {
    _('Archive'): (ARCHIVE_MIME, DOCUMENT_MIME[0]),
    _('Audio'): (AUDIO_MIME, 'audio-x-generic'),
    _('Document'): (DOCUMENT_MIME, 'gnome-mime-application-pdf'),
    _('Image'): (IMAGE_MIME, 'image'),
    _('Video'): (VIDEO_MIME, 'video'),
    _('Other'): (APP_MIME, 'binary'),
}

MIMETYPE_LIST = []
for mime in [ARCHIVE_MIME, AUDIO_MIME, DOCUMENT_MIME, IMAGE_MIME, VIDEO_MIME, APP_MIME]:
    MIMETYPE_LIST.extend(mime)
