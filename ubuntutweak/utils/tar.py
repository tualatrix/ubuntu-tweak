import logging
import tarfile

log = logging.getLogger("tar")

class TarFile:
    def __init__(self, path):
        if path.endswith('tar.gz'):
            mode = 'r:gz'
        elif path.endswith('tar.bz2'):
            mode = 'r:bz2'
        try:
            self._tarfile = tarfile.open(path, mode)
            self._error = ''
        except Exception, e:
            self._error = e
            log.error(e)

    def is_valid(self):
        return not bool(self._error)

    def extract(self, target):
        self._tarfile.extractall(target)

    def get_root_name(self):
        names = self._tarfile.getnames()
        for name in names:
            if '/' not in name:
                return name
        return ''
