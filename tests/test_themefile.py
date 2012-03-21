import os
import shutil
import unittest

from ubuntutweak.utils.tar import ThemeFile

class TestThemeFile(unittest.TestCase):
    def setUp(self):
        self.icon_path1 = '/tmp/ubunu-icon.tar.gz'
        os.system('cd /usr/share/icons/ && tar zcf %s ubuntu-mono-dark' % self.icon_path1)
        self.icon_path2 = '/tmp/light.tar.gz'
        os.system('cd /usr/share/icons/ubuntu-mono-light && tar zcf %s .' % self.icon_path2)

    def test_theme_file(self):
        tf1 = ThemeFile(self.icon_path1)
        self.assertEqual(tf1.is_theme(), True)
        self.assertEqual(tf1.theme_name, 'Ubuntu-Mono-Dark')
        self.assertEqual(tf1.install_name, 'ubuntu-mono-dark')

        tf2 = ThemeFile(self.icon_path2)
        self.assertEqual(tf2.is_theme(), True)
        self.assertEqual(tf2.theme_name, 'Ubuntu-Mono-Light')
        self.assertEqual(tf2.install_name, 'light')

    def tearDown(self):
        os.system('rm %s' % self.icon_path1)
        os.system('rm %s' % self.icon_path2)

if __name__ == '__main__':
    unittest.main()
