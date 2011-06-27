import unittest

from ubuntutweak.janitor.ppapurge_plugin import CleanPpaDialog

class TestPPAFunctions(unittest.TestCase):
    def setUp(self):
        self.string1 = 'Get:6 http://mirrors.163.com/ubuntu/ natty/universe python-dockmanager all 0.1.0-0ubuntu1 [4102 B]'
        self.string2 = 'natty-security/universe python-dockmanager all'
        self.string3 = 'natty--/main python-dockmanager all'
        self.dialog = CleanPpaDialog(None, None, None)

    def test_ppa(self):
        self.assertEqual(self.dialog.search_for_download_package(self.string1), 'python-dockmanager')
        self.assertEqual(self.dialog.search_for_download_package(self.string2), 'python-dockmanager')
        self.assertEqual(self.dialog.search_for_download_package(self.string3), None)

if __name__ == '__main__':
    unittest.main()
