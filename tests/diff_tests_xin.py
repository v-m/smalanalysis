import unittest

# Unit test for diff metrics script
from tests.TestHelper import TestHelper


class XinBasicMetricTesting(unittest.TestCase):
    ## TESTS START HERE ##

    # Initialize the field
    def test_debug(self):
        TestHelper.run_test_for_two_versions(self, 'vY', 'vX',
                                             {'OUT#C-': 1, 'OUT#C+': 1, 'OUTR': 1, 'OUTMC': 1, 'OUTCC': 1, 'IN#C-': 4,
                                              'IN#C+': 4, 'INMC': 1, 'INR': 1, 'INCA': 1, 'INCD': 1, 'INCC': 1}, True)


if __name__ == '__main__':
    unittest.main()
