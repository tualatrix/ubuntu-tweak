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
            self.__tarfile = tarfile.open(path, mode)
            self.__error = ''
        except Exception, e:
            self.__error = e
            log.error(e)

    def is_valid(self):
        return not bool(self.__error) 

    def extract(self, target):
        self.__tarfile.extractall(target)
