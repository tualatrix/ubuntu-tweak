import unittest

from ubuntutweak import modules
from ubuntutweak.utils import ppa

class TestUtilsFunctions(unittest.TestCase):
    def setUp(self):
        self.ppa_home_url = 'https://launchpad.net/~tualatrix/+archive/ppa'
        self.ppa_archive_url = 'http://ppa.launchpad.net/tualatrix/ppa/ubuntu'

    def test_ppa(self):
        self.assertTrue(ppa.is_ppa(self.ppa_archive_url))

        list_name = ppa.get_list_name(self.ppa_archive_url)
        self.failUnless(list_name == '' or list_name.startswith('/var/lib/apt/lists/'))

        self.assertEqual(ppa.get_short_name(self.ppa_archive_url), 'ppa:tualatrix/ppa')

        self.assertEqual(ppa.get_homepage(self.ppa_archive_url), self.ppa_home_url)

if __name__ == '__main__':
    unittest.main()
