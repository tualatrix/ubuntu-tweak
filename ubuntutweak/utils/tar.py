import os
import logging
import tarfile

from ubuntutweak.settings.configsettings import ConfigSetting

log = logging.getLogger("tar")

class TarFile:
    def __init__(self, path):
        if path.endswith('tar.gz'):
            mode = 'r:gz'
        elif path.endswith('tar.bz2'):
            mode = 'r:bz2'
        else:
            #TODO support zip
            mode = 'r:gz'

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


class ThemeFile(TarFile):
    def __init__(self, path):
        TarFile.__init__(self, path)

        self._path = path
        self._index_file = ''
        self._to_extract_dir = ''

        self.theme_name = ''
        self.theme_type = ''
        self.install_name = ''

        if not self.is_valid():
            raise Exception('Invalid file')

        self._parse_theme()

        if not self.is_theme():
            raise Exception('Invalid theme file')

    def _parse_theme(self):
        names = self._tarfile.getnames()
        for name in names:
            if 'index.theme' in name:
                #TODO support multi themes, in the future, it's better to only install from deb
                self._index_file = name
                break

        if self._index_file:
            log.debug("the index file is; %s" % self._index_file)
            self._tarfile.extract(self._index_file, '/tmp')
            cs = ConfigSetting('/tmp/%s::Icon Theme#name' % self._index_file)
            self.theme_name = cs.get_value()

            if '/' in self._index_file and not './' in self._index_file:
                self._to_extract_dir = os.path.dirname(self._index_file)
                log.debug("Because of index file: %s, the extra dir will be: %s" % (self._index_file, self._to_extract_dir))
                self.install_name = os.path.basename(os.path.dirname(self._index_file))
            else:
                #TODO improve
                self.install_name = os.path.basename(self._path).split('.')[0]

    def is_theme(self):
        return self.is_valid() and self.install_name != ''

    def is_installed():
        #TODO
        pass

    def install(self):
        #TODO may not be icon
        if self._to_extract_dir:
            self._tarfile.extractall(os.path.expanduser('~/.icons'))
        else:
            new_dir = os.path.expanduser('~/.icons/%s' % self.install_name)
            os.makedirs(new_dir)
            self._tarfile.extractall(new_dir)

        return True
