import os
import unittest

from ubuntutweak.janitor.mozilla_plugin import FirefoxCachePlugin

class TestJanitorPlugin(unittest.TestCase):
    def setUp(self):
        self.firefox_plugin = FirefoxCachePlugin()

    def test_firefox_plugin(self):
        self.assertTrue(os.path.expanduser('~/.mozilla/firefox/5tzbwjwa.default'), self.firefox_plugin.get_path())

if __name__ == '__main__':
    unittest.main()
