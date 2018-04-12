import unittest
import tests.diff_tests

# Unit test for diff metrics script


class XinBasicMetricTesting(tests.diff_tests.BasicMetricTesting):

    ## TESTS START HERE ##

    #Initialize the field
    def test_field_init(self):
        pass
        #self.runTestForTwoVersions('v2', 'v3', {'#C-': 1, '#C+': 1, 'R': 1, 'MC': 1, 'CC': 1})



if __name__ == '__main__':
    unittest.main()
