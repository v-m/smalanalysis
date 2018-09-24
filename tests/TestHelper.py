# Smali Projects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2018-04-13

import os
import subprocess
import smalanalysis.smali.SmaliProject
from smalanalysis.smali.Metrics import initMetricsDict, splitInnerOuterChanged, computeMetrics

class TestHelper:

    @staticmethod
    def getTestFolder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            subprocess.run(['bash', 'src/extractsmali.sh', 'src/%s'%v1], stdout=subprocess.PIPE, cwd=TestHelper.getTestFolder())


    @staticmethod
    def runTestForTwoVersions(self, v1, v2, notNullValues, splitInnerOuter = False):
        TestHelper.prepare(v1)
        TestHelper.prepare(v2)

        old = smalanalysis.smali.SmaliProject.SmaliProject()
        old.parseProject('%s/src/%s/smali.zip' % (TestHelper.getTestFolder(), v1), None, include_unpackaged=True)
        new = smalanalysis.smali.SmaliProject.SmaliProject()
        new.parseProject('%s/src/%s/smali.zip' % (TestHelper.getTestFolder(), v2), None, include_unpackaged=True)

        diff = old.differences(new, [])

        malg = {}

        if splitInnerOuter:
            innerDiff, outerDiff = splitInnerOuterChanged(diff)
            initMetricsDict("OUT", malg)
            initMetricsDict("IN", malg)
            computeMetrics(outerDiff, malg, "OUT")
            computeMetrics(innerDiff, malg, "IN")
        else:
            initMetricsDict("", malg)
            computeMetrics(diff, malg)

        TestHelper.metricsScoreComparing(self, malg, notNullValues)

    @staticmethod
    def metricsScoreComparing(self, malg, notNullValues, check_zero_defaults = False):
        for k in malg:
            excludes = []
            for k0 in ['', 'OUT', 'IN']:
                excludes.append('{}MRev'.format(k0))
                excludes.append('{}addedLines'.format(k0))
                excludes.append('{}removedLines'.format(k0))

            if k in excludes:
                continue

            if k in notNullValues:
                if notNullValues[k] != malg[k]:
                    self.fail("Bad metric matches for {}: {} != {}".format(k, notNullValues[k], malg[k]))
            elif check_zero_defaults:
                if malg[k] != 0:
                    self.fail("Metric {} is not default zero (={}).".format(k, malg[k]))


