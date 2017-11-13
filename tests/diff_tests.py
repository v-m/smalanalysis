import unittest
import metrics
import os
import subprocess

# Unit test for diff metrics script
# Date: November 6, 2017
# Author: Vincenzo Musco (http://www.vmusco.com)

class BasicMetricTesting(unittest.TestCase):

    @staticmethod
    def getTestFolder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            subprocess.run(['bash', 'src/extractsmali.sh', 'src/%s'%v1], stdout=subprocess.PIPE, cwd=BasicMetricTesting.getTestFolder())

    def runTestForTwoVersions(self, v1, v2, oldclasses=0,newclasses=0,E=0,R=0,C=0,CA=0,CD=0,CC=0,MA=0,MD=0,MC=0,MR=0,FA=0,FD=0,FC=0,FR=0):
        BasicMetricTesting.prepare(v1)
        BasicMetricTesting.prepare(v2)
        oldclasses_alg, newclasses_alg, E_alg, R_alg, C_alg, CA_alg, CD_alg, CC_alg, MA_alg, MD_alg, MC_alg, MR_alg, FA_alg, FD_alg, FC_alg, FR_alg = \
            metrics.computeMetrics('%s/src/%s' % (BasicMetricTesting.getTestFolder(), v1),
                               '%s/src/%s' % (BasicMetricTesting.getTestFolder(), v2),
                               None)

        self.assertEqual(oldclasses, oldclasses_alg)
        self.assertEqual(newclasses, newclasses_alg)

        self.assertEqual(E, E_alg)
        self.assertEqual(R, R_alg)
        self.assertEqual(C, C_alg)
        self.assertEqual(CA, CA_alg)
        self.assertEqual(CD,CD_alg)
        self.assertEqual(CC,CC_alg)
        self.assertEqual(MA,MA_alg)
        self.assertEqual(MD,MD_alg)
        self.assertEqual(MC,MC_alg)
        self.assertEqual(MR,MR_alg)
        self.assertEqual(FA,FA_alg)
        self.assertEqual(FD,FD_alg)
        self.assertEqual(FC,FC_alg)
        self.assertEqual(FR,FR_alg)


    ## TESTS START HERE ##

    #Add a field
    def test_add_field(self):
        self.runTestForTwoVersions('v1', 'v2', 1, 1, E = 1, FA = 1, CC = 1)

    #Initialize the field
    def test_field_init(self):
        self.runTestForTwoVersions('v2', 'v3', 1, 1, R = 1, MC = 1, CC = 1)

    #Change the field type
    def test_chg_field_type(self):
        self.runTestForTwoVersions('v2', 'v4', 1, 1, C = 1, FC = 1, CC = 1)

    #Change the field visibility
    def test_chg_field_visibility(self):
        self.runTestForTwoVersions('v2', 'v5', 1, 1, C = 1, FC = 1, CC = 1)

    #Add a static field
    def test_add_static_field(self):
        self.runTestForTwoVersions('v1', 'v6', 1, 1, E = 1, FA = 1, CC = 1)

    #Initialize the field
    def test_static_field_init(self):
        self.runTestForTwoVersions('v6', 'v7', 1, 1, E = 1, MA = 1, CC = 1)

    #Change the field type
    def test_static_field_chg_type(self):
        self.runTestForTwoVersions('v6', 'v8', 1, 1, C = 1, FC = 1, CC = 1)

    #Change the field visibility
    def test_static_field_chg_visibility(self):
        self.runTestForTwoVersions('v6', 'v9', 1, 1, C = 1, FC = 1, CC = 1)

    #Method rename
    def test_method_rename(self):
        self.runTestForTwoVersions('v1', 'v10', 1, 1, C = 1, MD = 1, MA = 1, CC = 1)

    #Field rename
    def test_field_rename(self):
        self.runTestForTwoVersions('v2', 'v11', 1, 1, C = 1, FD = 1, FA = 1, CC = 1)

    #Field rename when used at one location
    def test_field_rename_used_1_loc(self):
        self.runTestForTwoVersions('v12', 'v13', 1, 1, C = 1, MC = 0, FR = 1, CC = 1)

    #Method rename when used  at one locations (empty body)
    def test_method_rename_used_1_loc_no_body(self):
        self.runTestForTwoVersions('v14', 'v15', 1, 1, C = 1, MC = 0, MD = 1, MA = 1, CC = 1)

    #Field rename when used at two locations
    def test_field_rename_used_2_loc(self):
        self.runTestForTwoVersions('v16', 'v17', 1, 1, C = 1, MC = 0, FR = 1, CC = 1)

    #Method rename when used  at two locations (empty body)
    def test_method_rename_used_2_loc_no_body(self):
        self.runTestForTwoVersions('v18', 'v19', 1, 1, C = 1, MC = 0, MD = 1, MA = 1, CC = 1)

    #Method rename when not ussed (5 lines body)
    def test_method_rename_not_used_5_lines_body(self):
        self.runTestForTwoVersions('v20', 'v21', 1, 1, C = 1, MR = 1, CC = 1)

    #Change a reg field to a static field
    def test_field_to_static_field(self):
        self.runTestForTwoVersions('v2', 'v6', 1, 1, C = 1, FD = 1, FA = 1, CC = 1)

    #Delete all parameters, as well as adding and removing a method
    def test_delete_all_params_add_del_1m(self):
        self.runTestForTwoVersions('v22', 'v23', 1, 1, C = 1, MC = 2, MD = 1, MA = 1, CC = 1)

    #Delete 2 method, 1 field. Add 2 method, 1 field. Change field type on a third method.
    def test_add_del_2m_1f_change_1p(self):
        self.runTestForTwoVersions('v24', 'v25', 1, 1, C = 1, MC = 1, MD = 2, MA = 2, FD = 1, FA = 1, CC = 1)

    #Add a new class
    def test_add_1_class(self):
        self.runTestForTwoVersions('v1', 'v26', 1, 2, E = 0, CA = 1)

    #Delete a class
    def test_drop_1_class(self):
        self.runTestForTwoVersions('v26', 'v1', 2, 1, C = 0, CD = 1)

    #Add body lines in a method
    def test_R_extend_1_function(self):
        self.runTestForTwoVersions('v1', 'v27', 1, 1, R = 1, MC = 1, CC = 1)

    #Remove body lines in a method
    def test_R_shrink_1_function(self):
        self.runTestForTwoVersions('v27', 'v1', 1, 1, R = 1, MC = 1, CC = 1)

    #Add a method
    def test_E_add_method(self):
        self.runTestForTwoVersions('v1', 'v28', 1, 1, E = 1, MA = 1, CC = 1)

    #ECR = 1 with three classes
    def test_ECR_1(self):
        self.runTestForTwoVersions('v29', 'v30', 3, 3, E = 1, C = 1, R = 1, MC = 1, MD = 1, MA = 2, CC = 3)

    #All 1 with 4 classes
    def test_all_metrics_one(self):
        self.runTestForTwoVersions('v31', 'v32', 4, 4, E = 1, C = 1, R = 1, MC = 1, MD = 1, MR = 1, MA = 1, FC = 1, FD = 1, FR = 1, FA = 1, CC = 3, CD = 1, CA = 1)

    #Rename a field used in a renamed method
    def test_and_field_renaming(self):
        self.runTestForTwoVersions('v33', 'v34', 1, 1, C = 1, MR = 1, FR = 1, CC = 1)

    #Add an inner class
    def test_inner_class_added(self):
        self.runTestForTwoVersions('v1', 'v35', 1, 2, CA = 1)

    #Add a method on an inner class
    def test_inner_vlass_method_added(self):
        self.runTestForTwoVersions('v35', 'v36', 2, 2, E = 1, MA = 1, CC = 1)

    #Add a method parameter
    def test_add_method_parameter(self):
        self.runTestForTwoVersions('v1', 'v37', 1, 1, C = 1, MC = 1, CC = 1)

    #Change method return value
    def test_change_method_return_type(self):
        self.runTestForTwoVersions('v1', 'v38', 1, 1, C = 1, MC = 1, CC = 1)

    #Change method return and add parameter
    def test_change_method_return_type_add_parameter(self):
        self.runTestForTwoVersions('v1', 'v39', 1, 1, C = 1, MC = 1, CC = 1)

    #Change method return and add parameter overriding the identity always there
    def test_change_method_return_type_add_parameter_overriding(self):
        self.runTestForTwoVersions('v1', 'v40', 1, 1, E = 1, MA = 1, CC = 1)

    #Method overridding - changing one method only parameters
    def test_method_overriding_add_param(self):
        self.runTestForTwoVersions('v41', 'v42', 1, 1, C = 1, MC = 1, CC = 1)

    #Changing static final init value
    def test_change_init_static_final_field(self):
        self.runTestForTwoVersions('v44', 'v45', 1, 1, C = 1, FC = 1, CC = 1)

    #Changing the ressId on an android standard method
    def test_change_ress_id(self):
        self.runTestForTwoVersions('v46', 'v47', 3, 3, R = 0, MC = 0, CC = 0)

    #Changing another int which is not ressid related in a filtered method
    def test_change_non_ress_id(self):
        self.runTestForTwoVersions('v46', 'v48', 3, 3, R = 1, MC = 1, CC = 1)