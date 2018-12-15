# Smali Projects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2018-04-13

import os
import subprocess
import smalanalysis.smali.project
from smalanalysis.smali.metrics import init_metrics_dict, split_inner_outer_changed, compute_metrics


class TestHelper:

    @staticmethod
    def get_test_folder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            subprocess.run(['bash', 'src/extractsmali.sh', 'src/%s' % v1], stdout=subprocess.PIPE,
                           cwd=TestHelper.get_test_folder())

    @staticmethod
    def run_test_for_two_versions(self, v1, v2, notNullValues, splitInnerOuter=False):
        TestHelper.prepare(v1)
        TestHelper.prepare(v2)

        old = smalanalysis.smali.project.SmaliProject()
        old._parse_project('%s/src/%s/smali.zip' % (TestHelper.get_test_folder(), v1), None, include_unpackaged=True)
        new = smalanalysis.smali.project.SmaliProject()
        new._parse_project('%s/src/%s/smali.zip' % (TestHelper.get_test_folder(), v2), None, include_unpackaged=True)

        diff = old.differences(new, [])

        malg = {}

        if splitInnerOuter:
            innerDiff, outerDiff = split_inner_outer_changed(diff)
            init_metrics_dict("OUT", malg)
            init_metrics_dict("IN", malg)
            compute_metrics(outerDiff, malg, "OUT")
            compute_metrics(innerDiff, malg, "IN")
        else:
            init_metrics_dict("", malg)
            compute_metrics(diff, malg)

        TestHelper.metrics_score_comparing(self, malg, notNullValues)

    @staticmethod
    def metrics_score_comparing(self, malg, notNullValues, check_zero_defaults=False):
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
