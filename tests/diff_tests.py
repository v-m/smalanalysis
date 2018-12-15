import unittest

# Unit test for diff metrics script
# Date: November 6, 2017
# Author: Vincenzo Musco (http://www.vmusco.com)
import smalanalysis.smali.project
from tests.TestHelper import TestHelper


class BasicMetricTesting(unittest.TestCase):

    ## TESTS START HERE ##

    # Add a field
    def test_add_field(self):
        TestHelper.run_test_for_two_versions(self, 'v1', 'v2', {'#C-': 1, '#C+': 1, 'E': 1, 'FA': 1, 'CC': 1})

    # Initialize the field
    def test_field_init(self):
        TestHelper.run_test_for_two_versions(self, 'v2', 'v3', {'#C-': 1, '#C+': 1, 'R': 1, 'MC': 1, 'CC': 1})

    # Change the field type
    def test_chg_field_type(self):
        TestHelper.run_test_for_two_versions(self, 'v2', 'v4', {'#C-': 1, '#C+': 1, 'C': 1, 'FC': 1, 'CC': 1})

    # Change the field visibility
    def test_chg_field_visibility(self):
        TestHelper.run_test_for_two_versions(self, 'v2', 'v5', {'#C-': 1, '#C+': 1, 'C': 1, 'FC': 1, 'CC': 1})

    # Add a static field
    def test_add_static_field(self):
        TestHelper.run_test_for_two_versions(self, 'v1', 'v6', {'#C-': 1, '#C+': 1, 'E': 1, 'FA': 1, 'CC': 1})

    # Initialize the field
    def test_static_field_init(self):
        TestHelper.run_test_for_two_versions(self, 'v6', 'v7', {'#C-': 1, '#C+': 1, 'E': 1, 'MA': 1, 'CC': 1})

    # Change the field type
    def test_static_field_chg_type(self):
        TestHelper.run_test_for_two_versions(self, 'v6', 'v8', {'#C-': 1, '#C+': 1, 'C': 1, 'FC': 1, 'CC': 1})

    # Change the field visibility
    def test_static_field_chg_visibility(self):
        TestHelper.run_test_for_two_versions(self, 'v6', 'v9', {'#C-': 1, '#C+': 1, 'C': 1, 'FC': 1, 'CC': 1})

    # Method rename
    def test_method_rename(self):
        TestHelper.run_test_for_two_versions(self, 'v1', 'v10', {'#C-': 1, '#C+': 1, 'C': 1, 'MD': 1, 'MA': 1, 'CC': 1})

    # Field rename
    def test_field_rename(self):
        TestHelper.run_test_for_two_versions(self, 'v2', 'v11', {'#C-': 1, '#C+': 1, 'C': 1, 'FD': 1, 'FA': 1, 'CC': 1})

    # Field rename when used at one location
    def test_field_rename_used_1_loc(self):
        TestHelper.run_test_for_two_versions(self, 'v12', 'v13', {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 0, 'FR': 1, 'CC': 1})

    # Method rename when used  at one locations (empty body)
    def test_method_rename_used_1_loc_no_body(self):
        TestHelper.run_test_for_two_versions(self, 'v14', 'v15',
                                             {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 0, 'MD': 1, 'MA': 1, 'CC': 1})

    # Field rename when used at two locations
    def test_field_rename_used_2_loc(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 0, 'FR': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v16', 'v17', p)

    # Method rename when used  at two locations (empty body)
    def test_method_rename_used_2_loc_no_body(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 0, 'MD': 1, 'MA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v18', 'v19', p)

    # Method rename when not ussed (5 lines body)
    def test_method_rename_not_used_5_lines_body(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MR': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v20', 'v21', p)

    # Change a reg field to a static field
    def test_field_to_static_field(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'FD': 1, 'FA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v2', 'v6', p)

    # Delete all parameters, as well as adding and removing a method
    def test_delete_all_params_add_del_1m(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 2, 'MD': 1, 'MA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v22', 'v23', p)

    # Delete 2 method, 1 field. Add 2 method, 1 field. Change field type on a third method.
    def test_add_del_2m_1f_change_1p(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 1, 'MD': 2, 'MA': 2, 'FD': 1, 'FA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v24', 'v25', p)

    # Add a new class
    def test_add_1_class(self):
        p = {'#C-': 1, '#C+': 2, 'CA': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v26', p)

    # Delete a class
    def test_drop_1_class(self):
        p = {'#C-': 2, '#C+': 1, 'CD': 1}
        TestHelper.run_test_for_two_versions(self, 'v26', 'v1', p)

    # Add body lines in a method
    def test_R_extend_1_function(self):
        p = {'#C-': 1, '#C+': 1, 'R': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v27', p)

    # Remove body lines in a method
    def test_R_shrink_1_function(self):
        p = {'#C-': 1, '#C+': 1, 'R': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v27', 'v1', p)

    # Add a method
    def test_E_add_method(self):
        p = {'#C-': 1, '#C+': 1, 'E': 1, 'MA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v28', p)

    # ECR = 1 with three classes
    def test_ECR_1(self):
        p = {'#C-': 3, '#C+': 3, 'E': 1, 'C': 1, 'R': 1, 'MC': 1, 'MD': 1, 'MA': 2, 'CC': 3}
        TestHelper.run_test_for_two_versions(self, 'v29', 'v30', p)

    # All 1 with 4 classes
    def test_all_metrics_one(self):
        p = {'#C-': 4, '#C+': 4, 'E': 1, 'C': 1, 'R': 1, 'MC': 1, 'MD': 1, 'MR': 1, 'MA': 1, 'FC': 1, 'FD': 1, 'FR': 1,
             'FA': 1, 'CC': 3, 'CD': 1, 'CA': 1}
        TestHelper.run_test_for_two_versions(self, 'v31', 'v32', p)

    # Rename a field used in a renamed method
    def test_and_field_renaming(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MR': 1, 'FR': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v33', 'v34', p)

    # Add an inner class
    def test_inner_class_added(self):
        p = {'OUT#C-': 1, 'OUT#C+': 1, 'IN#C+': 1, 'INCA': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v35', p, True)

    # Add a method on an inner class
    def test_inner_class_method_added(self):
        p = {'OUT#C-': 1, 'OUT#C+': 1, 'IN#C-': 1, 'IN#C+': 1, 'INE': 1, 'INMA': 1, 'INCC': 1}
        TestHelper.run_test_for_two_versions(self, 'v35', 'v36', p, True)
        p = {'#C-': 2, '#C+': 2, 'E': 1, 'MA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v35', 'v36', p, False)

    # Add a method parameter
    def test_add_method_parameter(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v37', p)

    # Change method return value
    def test_change_method_return_type(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v38', p)

    # Change method return and add parameter
    def test_change_method_return_type_add_parameter(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v39', p)

    # Change method return and add parameter overriding the identity always there
    def test_change_method_return_type_add_parameter_overriding(self):
        p = {'#C-': 1, '#C+': 1, 'E': 1, 'MA': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v1', 'v40', p)

    # Method overridding - changing one method only parameters
    def test_method_overriding_add_param(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v41', 'v42', p)

    # Changing static final init value
    def test_change_init_static_final_field(self):
        p = {'#C-': 1, '#C+': 1, 'C': 1, 'FC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v44', 'v45', p)

    # Changing the ressId on an android standard method (5+ length int)
    def test_change_ress_id(self):
        p = {'#C-': 3, '#C+': 3}
        TestHelper.run_test_for_two_versions(self, 'v46', 'v48', p)

    # Changing int which is not ressid related (<5 length int)
    def test_change_non_ress_id(self):
        p = {'#C-': 3, '#C+': 3, 'R': 1, 'MC': 1, 'CC': 1}
        TestHelper.run_test_for_two_versions(self, 'v46', 'v47', p)


if __name__ == '__main__':
    unittest.main()
