"""Smali Objects.
Objects representing parts of smali bytecode
"""

__author__ = "Vincenzo Musco (http://www.vmusco.com)"
__date__ = "2017-09-15"

import re

from smalanalysis.smali.enums import ComparisonIgnores, ChangeTypes, DifferenceType, Identities
import smalanalysis.smali.project

class_name_pattern = re.compile("L(.*?)(\\$.+)*;")
method_call_pattern = re.compile("(.*)->(.*):(.*)")

REFERENCE_PATTERN = re.compile('^const [vp][0-9]{1,2}, (0x[0-9a-f]{5,})$')

class_ref_pattern = re.compile('L(.*?);')
method_access_pattern = re.compile('L(.*?)->(.*?)\\)')
field_access_pattern = re.compile('L(.*?)->(.*?):')
jumps_pattern = re.compile(':[a-zA-Z0-9_\\-]+')
local_registers_pattern = re.compile('v[0-9]+')
param_registers_pattern = re.compile('p[0-9]+')

inner_anonymous_class_reference_matcher = re.compile("\$[0-9$]+;")


def compare_string_sets(m1, m2):
    return len(m1 ^ m2) == 0


def compare_lists_same_position(l1, l2, mappings=None):
    if len(l1) != len(l2):
        return False

    for i in range(len(l1)):
        if type(l1[i]) != type(l2[i]):
            return False

        if type(l1[i]) == str:
            if mappings is not None and l1[i] in mappings:
                if mappings[l1[i]] != l2[i]:
                    return False
            else:
                if l1[i] != l2[i]:
                    return False
        else:
            if not l1[i].equals(l2[i], mappings):
                return False

    return True


def twoway_compare_lists(l1, l2, ignores=None, mappings=None):
    if ignores is None:
        ignores = []

    ret = []

    for m in compare_lists(l1, l2, ignores, mappings):
        ret.append([Identities.SELF, m])

    for m in compare_lists(l2, l1, ignores, mappings):
        ret.append([Identities.OTHER, m])

    return ret


def compare_lists_signature_eq(l1, l2):
    missing_ones = []

    if l1 is None and l2 is None:
        return missing_ones
    elif l1 is not None and l2 is not None:
        for it1 in l1:
            found = False

            for it2 in l2:
                if it1 == it2:
                    found = True
                    break

            if not found:
                missing_ones.append(it1)
    else:
        return None

    return missing_ones


def compare_lists(l1, l2, ignores=None, mappings=None):
    if ignores is None:
        ignores = []

    missing_ones = []

    if l1 is None and l2 is None:
        return missing_ones
    elif l1 is not None and l2 is not None:
        for it1 in l1:
            found = False

            for it2 in l2:
                if type(it1) == str or type(it2) == str:
                    if mappings is not None and compare_with_mapping(it1, it2, mappings):
                        found = True
                        break
                    elif it1 == it2:
                        found = True
                        break
                elif len(it1.differences(it2, ignores, mappings)) == 0:
                    found = True
                    break

            if not found:
                missing_ones.append(it1)
    else:
        return None

    return missing_ones


def compare_lists_boolean(l1, l2, mappings=None):
    return len(compare_lists(l1, l2, mappings)) == 0


class SmaliAnnotableModifiable(object):
    def __init__(self, parent):
        self.annotations = []
        self.modifiers = set()
        self.parent = parent

    def get_parent_project_if_any(self):
        trg = self.parent

        while trg is not None and not isinstance(trg, smalanalysis.smali.project.SmaliProject):
            trg = trg.parent

        return trg

    def add_annotation(self, a):
        self.annotations.append(a)

    def add_modifiers_from_list(self, modifiers):
        if modifiers is None:
            return

        for m in modifiers:
            self.modifiers.add(m.strip())

    def is_field(self):
        return False

    def is_method(self):
        return False

    def equals(self, other, mappings=None):
        if not compare_string_sets(self.modifiers, other.modifiers) or not len(self.annotations) == len(
                other.annotations):  # TODO annotations ?
            return False

        return True

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.ANOT_MOD_MODIFIERS not in ignores:
            if not compare_string_sets(self.modifiers, other.modifiers):
                ret.append(DifferenceType.NOT_SAME_MODIFIERS)

        # if ComparisonIgnores.ANOT_MOD_ANNOTATIONS not in ignores:
        #    if not not len(self.annotations) != len(other.annotations):
        #        ret.append(NOT_SAME_ANNOTATIONS)
        # TODO annotations ?

        return ret

    def get_display_name(self):
        return self.__repr__()


class SmaliWithLines(SmaliAnnotableModifiable):
    def __init__(self, name, modifiers, parent):
        SmaliAnnotableModifiable.__init__(self, parent)
        self.name = name.strip()
        self.lines = list()
        self.add_modifiers_from_list(modifiers)

    def get_name(self):
        return self.name

    def add_line(self, line):
        self.lines.append(line)

    def get_lines(self):
        return list(self.lines)

    def equals(self, other, mappings=None):
        if not compare_with_mapping(self.name, other.name, mappings) or not self.are_source_code_similars(other, mappings):
            return False

        return SmaliAnnotableModifiable.equals(self, other, mappings)

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.WITH_LINES_NAME not in ignores:
            if not compare_with_mapping(self.name, other.name, mappings):
                ret.append(DifferenceType.NOT_SAME_NAME)

        if ComparisonIgnores.WITH_LINES_SOURCECODE not in ignores:
            if not self.are_source_code_similars(other, mappings):
                ret.append(DifferenceType.NOT_SAME_SOURCECODE_LINES)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    def get_identity_lines(self):
        ret = list()

        for l in self.get_clean_lines():
            l = class_ref_pattern.sub('L', l)
            l = method_access_pattern.sub('m', l)
            l = field_access_pattern.sub('f', l)
            l = jumps_pattern.sub('JMP', l)
            l = local_registers_pattern.sub('vr', l)
            l = param_registers_pattern.sub('pr', l)
            ret.append(l)

        return ret

    @staticmethod
    def clean_lines(lines):
        slines = list()
        for line in lines:
            if SmaliWithLines.keep_this_line(line):
                slines.append(line)
        return slines

    @staticmethod
    def clean_identity_lines(lines):
        slines = list()
        for line in lines:
            if SmaliWithLines.keep_this_line(line):
                line = field_access_pattern.sub(r'\1->///FIELD///:', line)
                line = method_access_pattern.sub(r'\1->///METHOD///:', line)
                slines.append(line)
        return slines

    def get_clean_identity_lines(self):
        return SmaliWithLines.clean_identity_lines(self.lines)

    def get_clean_lines(self):
        return SmaliWithLines.clean_lines(self.lines)

    def more_than_n_instruction(self, n):
        return len(self.get_clean_lines()) > n

    def are_source_code_similars(self, other, consider_r_references=False, drop_anonymous_class_content=True, mappings=None):
        """
        Compare the smali lines
        :param other:
        :param consider_r_references:
        :param drop_anonymous_class_content: Do not compare the $X references in source lines.
                                            This option may induce some inacurracy but better match changes between
                                            two versions.
        :param mappings:
        :return:
        """
        slines = self.get_clean_identity_lines()
        olines = other.get_clean_identity_lines()

        if not consider_r_references:
            slines = SmaliMethod.clear_r_references(slines)
            olines = SmaliMethod.clear_r_references(olines)

        if drop_anonymous_class_content:
            slines = SmaliMethod.clear_inner_classes_references(slines)
            olines = SmaliMethod.clear_inner_classes_references(olines)

        if mappings is not None:
            slines = SmaliWithLines.transpose_with_new_references(slines, mappings)

        return compare_lists_same_position(slines, olines)

    @staticmethod
    def transpose_with_new_references(old, mappings):
        ret = []

        for line in old:
            thisline = line
            for m in mappings:
                thisline = thisline.replace(m.replace(";", ""), mappings[m].replace(";", ""))

            ret.append(thisline)

        return ret

    @staticmethod
    def clear_r_references(lines):
        ret = list()

        for line in lines:
            mtch = REFERENCE_PATTERN.search(line)

            if mtch is not None:
                ret.append(line.replace(mtch.group(1), '<R_REF>'))
            else:
                ret.append(line)

        return ret

    @staticmethod
    def clear_inner_classes_references(lines):
        ret = list()

        for line in lines:
            ret.append(inner_anonymous_class_reference_matcher.sub("$?", line))

        return ret

    @staticmethod
    def keep_this_line(line):
        lline = line.strip()
        return len(lline) > 0 and lline[0] != '.' and lline[0] != ':' and lline[0] != '#'


class SmaliField(SmaliAnnotableModifiable):
    def __init__(self, name, field_type, modifiers, init, clazz):
        super(SmaliField, self).__init__(clazz)
        self.name = name
        self.type = field_type
        self.init = init
        self.add_modifiers_from_list(modifiers)

    def equals(self, other, mappings=None):
        if self.name == other.name and compare_with_mapping(self.type, other.type, mappings) and self.init == other.init:
            return SmaliAnnotableModifiable.equals(self, other)

        return False

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.FIELD_NAME not in ignores:
            if not compare_with_mapping(self.name, other.name, mappings):
                ret.append(DifferenceType.NOT_SAME_NAME)

        if ComparisonIgnores.FIELD_TYPE not in ignores:
            if not compare_with_mapping(self.type, other.type, mappings):
                ret.append(DifferenceType.NOT_SAME_TYPE)

        if ComparisonIgnores.FIELD_INIT not in ignores:
            if self.init != other.init:
                ret.append(DifferenceType.NOT_SAME_INIT_VALUE)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    def is_field(self):
        return True


class SmaliMethod(SmaliWithLines):
    def __init__(self, name, params, ret, modifiers, clazz):
        SmaliWithLines.__init__(self, name, modifiers, clazz)
        self.params = params
        self.ret = ret

    def equals(self, other, mappings=None):
        if not isinstance(other, SmaliMethod) or not isinstance(self, SmaliMethod):
            return False

        if self.ret != other.ret or not compare_lists_same_position(self.params, other.params, mappings):
            return False

        return SmaliWithLines.equals(self, other)

    def get_light_params(self):
        ret = []

        for p in self.params:
            ret.append(p[0:1])

        return ret

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.METHOD_RETURN not in ignores:
            if not compare_with_mapping(self.ret, other.ret, mappings):
                ret.append(DifferenceType.NOT_SAME_RETURN_TYPE)

        if ComparisonIgnores.METHOD_PARAMS not in ignores:
            if not compare_lists_same_position(self.params, other.params):
                ret.append(DifferenceType.NOT_SAME_PARAMETERS)

        ret.extend(SmaliWithLines.differences(self, other, ignores))
        return ret

    def is_method(self):
        return True

    def get_signature(self):
        return ('%s(%s)%s' % (self.name, ''.join(self.params), self.ret)).strip()

    def get_full_signature(self):
        return '%s.%s' % (
        '?' if self.parent is None else self.parent.get_base_name().replace('/', '.'), self.get_signature())


class SmaliAnnotation(SmaliWithLines):
    pass


def compare_with_mapping(old, new, mappings):
    oldres = old

    if mappings is not None and "$" in old:
        oldres = "L{};".format(re.match("(\[*?)L(.*?)(\$(.*))?;", old).group(2))

    if mappings is not None and oldres in mappings:
        if mappings[oldres] == new:
            return True

        oold = inner_anonymous_class_reference_matcher.sub("$?;", old)
        onew = inner_anonymous_class_reference_matcher.sub("$?;", new)

        for m in mappings:
            if m.replace(";", "") in oold:
                oold = oold.replace(m.replace(";", ""), mappings[m].replace(";", ""))
                break

        return oold == onew
    else:
        return old == new


class SmaliClass(SmaliAnnotableModifiable):
    def __init__(self, project):
        super(SmaliClass, self).__init__(project)
        self.name = None
        self.innername = None
        self.zuper = None
        self.source = None
        self.implements = set()
        self.innerclasses = {}
        self.methods = []
        self.fields = []

    def get_name(self):
        return self.name

    def has_inner_classes(self):
        return len(self.innerclasses) > 0

    def get_anonymous_inner_classes(self):
        return filter(lambda x: re.match("^[0-9]+$", x), self.innerclasses)

    def get_non_anonymous_inner_classes(self):
        return filter(lambda x: not re.match("^[0-9]+$", x), self.innerclasses)

    def determine_parent_class(self):
        if self.parent is not None:
            if self.zuper is not None:
                return self.parent.search_class(self.zuper)

        return None

    def determine_parent_class_hierarchy(self):
        ret = []

        parent = self.determine_parent_class()

        while parent is not None:
            ret.append(parent)
            parent = parent.determineParentClass()

        return ret

    def determine_parent_class_hierarchy_names(self):
        ret = self.determine_parent_class_hierarchy()

        if len(ret) == 0:
            return [self.zuper]

        last_parent = ret[-1].zuper
        ret = list(map(lambda x: x.name, ret))
        ret.append(last_parent)
        return ret

    def get_display_name(self):
        return SmaliClass._get_display_name(self.name)

    @staticmethod
    def _get_display_name(class_name):
        mt = class_name_pattern.match(class_name)

        if mt is not None:
            return class_name[1:-1].strip().replace('/', '.')
        else:
            return class_name

    def get_base_name(self):
        mt = class_name_pattern.match(self.name)

        if mt is None:
            return self.name[1:-1]
        else:
            return mt.group(1)

    def add_method(self, m):
        self.methods.append(m)

    def add_field(self, f):
        self.fields.append(f)

    def set_name(self, name):
        self.name = name

    def set_super(self, zuper):
        self.zuper = zuper

    def get_super(self):
        return self.zuper[1:-1]

    def add_mplemented_nterface(self, ifce):
        self.implements.add(ifce)

    # def __eq__(self, other):
    # FIXIT Do not use __eq__ directly !
    #    assert (False)

    def equals(self, other, mappings=None):
        if not compare_with_mapping(self.name, other.name, mappings) or \
                not compare_with_mapping(self.zuper, other.zuper, mappings) or \
                not compare_lists_boolean(self.implements, other.implements, mappings) or \
                not compare_lists_boolean(self.methods, other.methods, mappings) or \
                not compare_lists_boolean(self.fields, other.fields, mappings) or \
                not compare_lists_boolean(other.implements, self.implements, mappings) or \
                not compare_lists_boolean(other.methods, self.methods, mappings) or \
                not compare_lists_boolean(other.fields, self.fields, mappings):
            return False

        return SmaliAnnotableModifiable.equals(self, other)

    def differences(self, other, ignores, mappings=None):
        fret = []

        if ComparisonIgnores.CLASS_NAME not in ignores:
            if not compare_with_mapping(self.name, other.name, mappings):
                fret.append([self, other, DifferenceType.NOT_SAME_NAME])

        if ComparisonIgnores.CLASS_SUPER not in ignores:
            if not compare_with_mapping(self.zuper, other.zuper, mappings):
                fret.append([self, other, DifferenceType.NOT_SAME_PARENT])

        if ComparisonIgnores.CLASS_IMPLEMENTS not in ignores:
            ret = twoway_compare_lists(self.implements, other.implements, mappings)
            if len(ret) > 0:
                fret.append([self, other, DifferenceType.NOT_SAME_INTERFACES, ret])

        if ComparisonIgnores.CLASS_METHODS not in ignores:
            ret = self.methods_comparison(other, ignores, mappings)

            for diff in ret[1]:
                fret.append(diff)

        if ComparisonIgnores.CLASS_FIELDS not in ignores:
            ret = self.fields_comparison(other, ignores, fret, mappings)

            for diff in ret[1]:
                fret.append(diff)

        return fret

    def is_revision_of(self, other):  # No change in anything else than code !
        df = self.differences(other, [])
        return len(df) == 1 and df[0] == DifferenceType.NOT_SAME_SOURCECODE_LINES

    def set_source(self, param):
        self.source = param

    def methods_comparison(self, other, ignores, mappings=None):
        method_self = list(self.methods)
        method_other = list(other.methods)
        methods_temp = list()

        sames = list()
        diffs = list()

        while len(method_self) > 0:
            method = method_self.pop()

            found = False

            for m in method_other:
                if method.equals(m, mappings):
                    found = True
                    sames.append([method, m])
                    method_other.remove(m)
                    break

            if not found:
                methods_temp.append(method)

        method_self = methods_temp
        methods_temp = list()

        while len(method_self) > 0:
            method = method_self.pop()

            op = None
            found = False

            for m in method_other:
                diff = method.differences(m, ignores, mappings)

                if len(diff) == 1:
                    if diff[0] == DifferenceType.NOT_SAME_SOURCECODE_LINES:
                        op = [m, ChangeTypes.REVISED_METHOD]
                    elif diff[0] == DifferenceType.NOT_SAME_NAME and method.more_than_n_instruction(1):
                        op = [m, ChangeTypes.RENAMED_METHOD]
                if op is None and method.name == m.name:
                    # More than one change but they have the same source code,
                    # so we can suppose they are the same changed methods...
                    op = [m, ChangeTypes.SAME_NAME]

                if op is not None:
                    found = True
                    diffs.append([method, op[0], op[1]])
                    method_other.remove(m)
                    break

            if not found:
                methods_temp.append(method)

        method_self = methods_temp
        methods_temp = list()

        while len(method_self) > 0:
            method = method_self.pop()

            op = None

            for m in method_other:
                if method.are_source_code_similars(m, mappings) and method.more_than_n_instruction(1):
                    op = [m, ChangeTypes.RENAMED_METHOD]

                if op is not None:
                    diffs.append([method, op[0], op[1]])
                    method_other.remove(m)
                    break

            if op is None:
                diffs.append([method, None, ChangeTypes.NOT_FOUND])

        while len(method_other) > 0:
            method = method_other.pop()
            diffs.append([None, method, ChangeTypes.NOT_FOUND])

        return sames, diffs

    def fields_comparison(self, other, ignores, ret, mappings=None):
        field_self = list(self.fields)
        field_other = list(other.fields)
        fields_temp = list()

        sames = list()
        diffs = list()

        while len(field_self) > 0:
            field = field_self.pop()

            found = False

            for f in field_other:
                if field.equals(f, mappings):
                    found = True
                    sames.append([field, f])
                    field_other.remove(f)
                    break

            if not found:
                fields_temp.append(field)

        field_self = fields_temp

        while len(field_self) > 0:
            field = field_self.pop()

            found = False
            for f in field_other:
                if len(field.differences(f, [ComparisonIgnores.FIELD_INIT])) == 0 or (
                        f.name == field.name and 'static' not in (f.modifiers ^ field.modifiers)):
                    diffs.append([field, f, ChangeTypes.FIELD_CHANGED, field.differences(f, [])])
                    found = True
                    field_other.remove(f)
                    break

            if not found:
                where_is_used = self.where_is_field_used(field)
                f = self.try_to_detect_field_renaming_with_computed_sets(field, where_is_used, other, field_other, ret)

                if f is not None:
                    diffs.append([field, f, ChangeTypes.FIELD_CHANGED, field.differences(f, [])])
                    field_other.remove(f)
                else:
                    diffs.append([field, None, ChangeTypes.NOT_FOUND])

        while len(field_other) > 0:
            field = field_other.pop()
            diffs.append([None, field, ChangeTypes.NOT_FOUND])

        return sames, diffs

    def where_is_field_used(self, field):
        ret = []

        field_call = "%s->%s:%s" % (self.name.strip(), field.name.strip(), field.type.strip())
        for m in self.methods:
            lnr = 0

            if m.get_name() == '<init>' and len(m.params) == 0:
                # Lets skip similarities in the def cstr
                # as init value are put here for non static fields
                continue

            for lc in m.get_clean_lines():
                if field_call in lc:
                    ret.append([m, lnr])
                lnr += 1

        return ret

    def try_to_detect_field_renaming(self, field, where_is_used, new_class, new_fields):
        field_call = "%s->%s:%s" % (self.name.strip(), field.name.strip(), field.type.strip())

        for usage in where_is_used:
            usage_line = usage[1]
            similar_method = new_class.find_similar_method(usage[0])

            if similar_method is not None:
                line1 = usage[0].get_clean_lines()[usage_line]

                line2content = similar_method.get_clean_lines()

                if len(line2content) > usage_line:
                    before = line1[0:line1.index(field_call)]
                    after = line1[len(before) + len(field_call):]

                    line2 = similar_method.get_clean_lines()[usage_line]
                    new_candidate = line2.replace(before, '').replace(after, '')

                    for f in new_fields:
                        if SmaliClass.match_field_and_field_call(f, new_candidate):
                            return f

        return None

    def try_to_detect_field_renaming_with_computed_sets(self, field, where_is_used, new_class, new_fields, ret):
        field_call = "%s->%s:%s" % (self.name.strip(), field.name.strip(), field.type.strip())

        for usage in where_is_used:
            usage_line = usage[1]

            similar_method = None

            for ent in ret:

                if ent[0] is not None and ent[1] is not None:
                    if id(ent[0]) == id(usage[0]):
                        similar_method = ent[1]
                        break
                    elif id(ent[1]) == id(usage[0]):
                        similar_method = ent[0]
                        break

            if similar_method is None:
                similar_method = new_class.find_similar_method(usage[0])

            if similar_method is not None:
                line1 = usage[0].get_clean_lines()[usage_line]

                line2content = similar_method.get_clean_lines()

                if len(line2content) > usage_line:
                    before = line1[0:line1.index(field_call)]
                    after = line1[len(before) + len(field_call):]

                    line2 = similar_method.get_clean_lines()[usage_line]
                    new_candidate = line2.replace(before, '').replace(after, '')

                    for f in new_fields:
                        if SmaliClass.match_field_and_field_call(f, new_candidate):
                            return f

        return None

    def find_similar_method(self, method):
        for m in self.methods:
            if len(method.differences(m, [ComparisonIgnores.WITH_LINES_SOURCECODE])) == 0:
                return m

        return None

    @staticmethod
    def match_field_and_field_call(field, field_call):
        m = method_call_pattern.match(field_call)

        if m is not None:
            return field.name.strip() == m.group(2).strip() and field.type.strip() == m.group(3).strip()

    def find_method(self, name, parameters, ret):
        for m in self.methods:
            if m.name == name and ''.join(m.params) == parameters and m.ret == ret:
                return m

        return None
