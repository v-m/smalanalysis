'''
Unit tests writted by Aakashkumar Patel (aakpat).
Requires    python3.
'''

import unittest
import subprocess
import os
import shutil
import metrics
#from metrics import computeMetrics
import smali.SmaliProject
from tests.diff_tests import BasicMetricTesting


class TestUM(unittest.TestCase):
    @staticmethod
    def computeMetrics(v1, v2, pkg):
        testfold = TestUM.getTestFolder()

        old = smali.SmaliProject.SmaliProject()
        old.parseProject('%s/%s' % (testfold, v1), pkg)
        new = smali.SmaliProject.SmaliProject()
        new.parseProject('%s/%s' % (testfold, v2), pkg)

        malg = {}

        diff = old.differences(new, [])
        metrics.initMetricsDict("", malg)
        metrics.computeMetrics(diff, malg)

        return malg

    @staticmethod
    def getTestFolder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            name = v1.replace('.smali', '.apk')
            subprocess.run(['java', '-jar', '../bin/baksmali-2.2.1.jar', 'disassemble', name, '-o', v1], stdout=subprocess.PIPE, cwd=TestUM.getTestFolder())

    @classmethod
    def tearDownClass(cls):
        for p in os.listdir(TestUM.getTestFolder()):
            fullfile = '%s/%s'%(TestUM.getTestFolder(), p)
            if p.endswith('.smali') and os.path.isdir(fullfile):
                shutil.rmtree(fullfile)

    def test_v1v2_changesinStrings_xml(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app1.smali'
        v2 = 'apks/app2.smali'

        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {})
    
    def test_v2v3_renameingonemethod(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app2.smali'
        v2 = 'apks/app3.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"C": 1, "CC": 1, "MR": 1})

    def test_v3v4_renameingonefield(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app3.smali'
        v2 = 'apks/app4.smali'

        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"C": 1, "CC": 1, "FR": 1})


    def test_v4v5_renameingonefield_String(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app4.smali'
        v2 = 'apks/app5.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)


        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"C": 1, "CC": 1, "FR": 1})

    def test_v5v6_changemethod(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app5.smali'
        v2 = 'apks/app6.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"R": 1, "CC": 1, "MC": 1})

    def test_v6v7_renameingonefield(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app6.smali'
        v2 = 'apks/app7.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"C": 1, "CC": 1, "FR": 1})

 

    def test_v11v12_constructor_method_change(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app11.smali'
        v2 = 'apks/app12.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"R": 1, "CC": 1, "MC": 1})



    def test_v12v13_method_change_and_call_method(self):
        pkg = 'com.example.xinyin.myapplication'
        v1 = 'apks/app12.smali'
        v2 = 'apks/app13.smali'


        TestUM.prepare(v1)
        TestUM.prepare(v2)

        malg = TestUM.computeMetrics(v1, v2, pkg)
        BasicMetricTesting.metricsScoreComparing(self, malg, {"C": 1, "CC": 1, "MC": 2})


if __name__ == '__main__':
    unittest.main()


