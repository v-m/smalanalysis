# Smali Projects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2018-04-13

import metrics
import os
import subprocess
import smali.SmaliProject


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

        old = smali.SmaliProject.SmaliProject()
        old.parseProject('%s/src/%s/smali.zip' % (TestHelper.getTestFolder(), v1), None, includeUnpackaged=True)
        new = smali.SmaliProject.SmaliProject()
        new.parseProject('%s/src/%s/smali.zip' % (TestHelper.getTestFolder(), v2), None, includeUnpackaged=True)

        diff = old.differences(new, [])

        malg = {}


        if splitInnerOuter:
            innerDiff, outerDiff = metrics.splitInnerOuterChanged(diff)
            metrics.initMetricsDict("OUT", malg)
            metrics.initMetricsDict("IN", malg)
            metrics.computeMetrics(outerDiff, malg, "OUT")
            metrics.computeMetrics(innerDiff, malg, "IN")
        else:
            metrics.initMetricsDict("", malg)
            metrics.computeMetrics(diff, malg)

        TestHelper.metricsScoreComparing(self, malg, notNullValues)

    @staticmethod
    def metricsScoreComparing(self, malg, notNullValues):
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
            else:
                if malg[k] != 0:
                    self.fail("Metric {} is not default zero (={}).".format(k, malg[k]))


