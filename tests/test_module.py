import os
import shutil
import unittest

from ubuntutweak.modules import ModuleLoader
from ubuntutweak.common.debug import enable_debugging
from ubuntutweak.common import consts

class TestModuleFunctions(unittest.TestCase):
    def setUp(self):
        ModuleLoader.default_features = ('module_test',)
        ModuleLoader.search_loaded_table = {}

        self.test_folder = os.path.join(consts.CONFIG_ROOT, 'module_test')
        if os.path.exists(self.test_folder):
            shutil.rmtree(self.test_folder)
        os.makedirs(self.test_folder)
        os.system('touch %s/__init__.py' % self.test_folder)
        os.system('cp ubuntutweak/tweaks/nautilus.py %s/nautilus_test.py' % self.test_folder)

        sub_test_folder = os.path.join(self.test_folder, 'desktoprecovery')
        os.makedirs(sub_test_folder)
        os.system('cp ubuntutweak/admins/desktoprecovery.py %s/__init__.py' % sub_test_folder)

    def test_module(self):
        feature, module = ModuleLoader.search_module_for_name('nautilus_test')
        self.assertEqual(feature, 'overview')
        self.assertEqual(module, None)

        feature, module = ModuleLoader.search_module_for_name('Nautilus')
        self.assertEqual(feature, 'module_test')
        self.assertEqual(module.__name__, 'Nautilus')

        feature, module = ModuleLoader.search_module_for_name('DesktopRecovery')
        self.assertEqual(feature, 'module_test')
        self.assertEqual(module.__name__, 'DesktopRecovery')

    def tearDown(self):
        shutil.rmtree(self.test_folder)
        ModuleLoader.default_features = ('tweaks', 'admins', 'janitor')

if __name__ == '__main__':
    unittest.main()
