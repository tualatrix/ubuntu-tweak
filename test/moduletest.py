import unittest
from ubuntutweak import modules
from ubuntutweak.modules import ModuleLoader

class TestModuleFunctions(unittest.TestCase):
    def setUp(self):
        self.module_loader = ModuleLoader(modules.__path__[0])

    def testmoduletable(self):
        for k, v in self.module_loader.module_table:
            self.assertEqual(type(k), str)

if __name__ == '__main__':
    unittest.main()
