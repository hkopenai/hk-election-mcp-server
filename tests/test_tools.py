import unittest
from tests.test_tool_gc_registered_electors import TestGCRegisteredElectors

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestGCRegisteredElectors))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    runner.run(test_suite)
