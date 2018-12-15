"""Smali Projects.
Represent a smali project (i.e. app/apk)"""

__author__ = "Vincenzo Musco (http://www.vmusco.com)"
__date__ = "2017-09-15"

import re
import os

import sys
import zipfile

import smalanalysis.smali.objects
from smalanalysis.smali.objects import SmaliClass
from smalanalysis.smali.enums import ComparisonIgnores, ChangeTypes


class MATCHERS:
    obj = "(\\[*(L[a-zA-Z0-9/_$\\-]+;|Z|B|S|C|I|J|F|D|V))"
    method_reg = re.compile("\\.method( [a-z \\-]+?)*( [a-zA-Z0-9<>_$\\-]+)\\((.*)\\)(.*)")  # Without obfuscation
    method = re.compile("\\.method( [a-z \\-]+?)*( [^ ]+)\\((.*)\\)(.*)")
    method_param = re.compile("%s" % obj)
    field_init = re.compile("%s( = .*)" % obj)
    fields_reg = re.compile("\\.field( [a-z ]+)*( [a-zA-Z0-9_$\\-]*)+?:(.*)")  # Without obfuscation
    fields = re.compile("\\.field( [a-z ]+)*( [^ ]*)+:([^:]*)")
    clazz = re.compile("\\.class( [a-z ]+)*( [a-zA-Z][a-zA-Z0-9_\\-/$]*)+?;")
    annotation = re.compile("\\.annotation( [a-z ]+)*( L[a-zA-Z0-9_/$]*);")
    ressource_classes = re.compile("^.*/R(\\$[a-z]+)?\\.smali$")
    hex_ref = re.compile("0x[0-9abcdef]{2,}")


class ModeDeprecatedError(BaseException):
    pass


class SmaliProject(object):
    """
    Helper object for holding all internal representations for a smali project.
    """

    def __init__(self):
        self.classes = []
        self.classesdict = {}
        self.ressources_id = set()

    @staticmethod
    def parse_project(source, package=None, skip_list=None, include_list=None, include_unpackaged=False):
        """
        Static method used to parse a project and get a SmaliObject on it.
        :param source: the source folder to parse
        :param package: the package id under study
        :param skip_list: the list of elements to exclude from the parsing
        :param include_list: the list of elements to include in the parsing
        :param include_unpackaged: True to include unpackaged classes and elements
        :raise FileNotFoundError: if the smali project does not exist
        :raise ModeDeprecatedError: when trying to parse a smali folder
        :return: a SmaliProject object
        """
        return_object = SmaliProject()
        return_object._parse_project(source, package, skip_list, include_list, include_unpackaged)
        return return_object

    def add_class(self, c):
        self.classes.append(c)
        self.classesdict[c.name] = c

    def _parse_ressource(self, ctnt):
        for line in ctnt.split('\n'):
            refs = MATCHERS.hex_ref.findall(line)

            for r in refs:
                self.ressources_id.add(r)

        pass

    def is_project_obfuscated(self):
        """Determine whether a project uses obfuscation."""
        keep, skip = 0, 0

        obfuscatedclassname = re.compile("(.*/)?[a-z]{1,3};")

        for p in self.classes:
            obfuscatedclass = obfuscatedclassname.fullmatch(p.name) is not None
            if not obfuscatedclass:
                keep += 1
            else:
                skip += 1

        if keep == 0:
            return True

        return skip / keep > 0.75

    @staticmethod
    def _should_analyze_this_class(classname, skips=None, includes=None, default=True):
        clazz = classname

        if '/' in classname:
            clazz = classname.replace('/', '.')

        if clazz[0] == '/':
            clazz = clazz[1:]

        if includes is not None:
            for include in includes:
                if include in clazz:
                    return True
        if skips is not None:
            for skip in skips:
                if skip in clazz:
                    return False
        return default

    @staticmethod
    def load_rules_list(fileslist):
        rules = set()

        if type(fileslist) == str:
            fileslist = [fileslist]

        for f in fileslist:
            rules = rules.union(SmaliProject._load_rules_list_from_file(f))

        return rules

    @staticmethod
    def _load_rules_list_from_file(file):
        rules = set()

        for entry in open(file, 'r'):
            rules.add(entry.strip())

        return rules

    # 1 = class / 2 = ressource / 0 = skip
    @staticmethod
    def _keep_this_file(fullpath, package, includes, skips, include_unpackaged):
        if fullpath.endswith('.smali'):
            skip = False

            if package is not None and package.replace('.', '/') not in fullpath:
                skip = True

            if MATCHERS.ressource_classes.match(fullpath):
                return 2

            if '/' not in fullpath:
                return 1 if include_unpackaged else 0

            if skips is not None or includes is not None:
                skip = not SmaliProject._should_analyze_this_class(fullpath, skips, includes, not skip)

            if fullpath.endswith('/BuildConfig.smali'):
                skip = True

            if not skip:
                return 1

        return 0

    def _parse_project(self, folder, package=None, skiplists=None, includelist=None, include_unpackaged=False):
        """
        Class method used to parse a project.
        Consider using the helper static method (SmaliProject.build_and_parse_project)
        :param source: the source folder to parse
        :param package: the package id under study
        :param skip_list: the list of elements to exclude from the parsing
        :param include_list: the list of elements to include in the parsing
        :param include_unpackaged: True to include unpackaged classes and elements
        :raise FileNotFoundError: if smali project does not exist
        :raise ModeDeprecatedError: when trying to parse a smali folder
        """
        skips = None
        includes = None
        if skiplists is not None:
            skips = set()
            for s in skiplists:
                skips = skips.union(SmaliProject._load_rules_list_from_file(s))
        if includelist is not None:
            includes = set()
            for s in includelist:
                includes = includes.union(SmaliProject._load_rules_list_from_file(s))

        if os.path.exists(folder):
            if os.path.isfile(folder):
                # This is a ZIP
                zp = zipfile.ZipFile(folder, 'r')
                SmaliProject._parse_zip_loop(zp, self, package, skips=skips, includes=includes,
                                             include_unpackaged=include_unpackaged)
            else:
                raise ModeDeprecatedError()
                # print("Parsing folder is not supported anymore. Please use archive mode.")
        else:
            raise FileNotFoundError()
            # print("File {} not found!".format(folder))

    @staticmethod
    def _parse_zip_loop(zp, target, package=None, skips=None, includes=None, include_unpackaged=False):
        classes = {}
        inner_classes = []

        for n in zp.namelist():
            op = SmaliProject._keep_this_file(n, package, includes, skips, include_unpackaged)

            if op == 1:
                ccontent = "".join(map(chr, zp.read(n)))
                cls = SmaliProject._parse_class(ccontent)
                cls.parent = target

                m2 = cls.name[1:-1].split("$")
                if len(m2) > 1 and m2[0][-1] != '/':
                    inner_classes.append((cls, m2[0], m2[1:]))
                else:
                    classes[cls.name[1:-1]] = cls
                    target.add_class(cls)

            elif op == 2:
                ccontent = "".join(map(chr, zp.read(n)))
                target._parse_ressource(ccontent)

        # Deal with inner classes now
        loop_level = 0
        processed_at_least_one = True

        while processed_at_least_one:
            processed_at_least_one = False
            loop_level += 1

            for e in inner_classes:
                if e[1] not in classes:
                    missing_class = SmaliClass(target)
                    missing_class.name = "L{};".format(e[1])
                    classes[e[1]] = missing_class
                    target.add_class(missing_class)

                target_class = classes[e[1]]
                # inner_class_path = list(e[2][:-1])

                if len(e[2]) == loop_level:
                    # while len(inner_class_path) > 0:
                    # newLevel = inner_class_path.pop()

                    # if newLevel not in targetclass.innerclasses:
                    #     missing_class = smali.SmaliObject.SmaliClass(e[1])
                    #     missing_class.name = "L{}{};".format(targetclass.name[1:-1], newLevel)
                    #     targetclass.innerclasses[newLevel] = missing_class

                    target_class.innerclasses[e[2][-1]] = e[0]
                    e[0].parent = target_class
                    e[0].innername = '$'.join(e[2])
                    processed_at_least_one = True

    def search_class(self, class_name):
        search_for = class_name

        if '/' not in search_for and '.' in search_for:
            search_for = search_for.replace('/', '.')

        if not (search_for[0] == 'L' and search_for[-1] == ';'):
            search_for = 'L%s;' % search_for

        for c in self.classes:
            if c is None or c.name is None:
                continue

            if search_for == c.name:
                return c

        return None

    def _match_classes(self, other):
        old = list(self.classes)
        new = list(other.classes)
        old2 = list()

        differents = []
        similars = []

        while len(old) > 0:
            clazz = old.pop()

            found = False
            for c in new:
                if clazz.name == c.name:
                    similars.append([clazz, c])
                    new.remove(c)
                    found = True
                    break

            if not found:
                old2.append(clazz)

        while len(old2) > 0:
            clazz = old2.pop()

            found = False
            for c in new:
                if clazz.name.split('/')[-1] == c.name.split('/')[-1]:
                    similars.append([clazz, c])
                    new.remove(c)
                    found = True
                    break

            if not found:
                differents.append([clazz, None])

        while len(new) > 0:
            c = new.pop()
            differents.append([None, c])

        return similars, differents

    def differences(self, other, ignores, process_inner_classes=True):
        ret = []
        dd = self._match_classes(other)
        classes_matching = {}

        def _append_matched_case(matched_cases_sim):
            classes_matching[matched_cases_sim[0].name] = matched_cases_sim[1].name
            matched_cases_ret = list()
            matched_cases_diff = matched_cases_sim[0].differences(matched_cases_sim[1], ignores)
            if len(matched_cases_diff) > 0:
                matched_cases_ret.extend(matched_cases_diff)

            ret.append([matched_cases_sim, matched_cases_ret])

        for sim in dd[0]:
            _append_matched_case(sim)

        for diff in dd[1]:
            ret.append([diff, None])

        # Additional code for handling inner classes
        if process_inner_classes:
            process_classes = []
            for old, new in dd[0]:
                if old.has_inner_classes() or new.has_inner_classes():
                    process_classes.append((old, new))
                elif len(old.innerclasses) + len(new.innerclasses) > 0:
                    # Should not happen
                    assert False

            while len(process_classes) > 0:
                popped = process_classes.pop()

                old, new = popped
                result = SmaliProject._diff_anonymous_inner_classes(old, new, classes_matching)

                for matched in result[0]:
                    _append_matched_case(matched)
                    if matched[0].has_inner_classes() or matched[1].has_inner_classes():
                        process_classes.append((matched[0], matched[1]))

                for droppedInnerClasses in result[1]:
                    ret.append([[droppedInnerClasses, None], None])

                for insertedInnerClasses in result[2]:
                    ret.append([[None, insertedInnerClasses], None])

                result = SmaliProject._diff_non_anonymous_inner_classes(old, new, classes_matching)
                for matched in result[0]:
                    _append_matched_case(matched)
                    if matched[0].has_inner_classes() or matched[1].has_inner_classes():
                        process_classes.append((matched[0], matched[1]))

                for droppedInnerClasses in result[1]:
                    ret.append([[droppedInnerClasses, None], None])

                for insertedInnerClasses in result[2]:
                    ret.append([[None, insertedInnerClasses], None])

            # Not matched inner classes
            for diff in dd[1]:
                def analyse_it(clazz, class_inner_classes):
                    for i in clazz.innerclasses:
                        class_inner_classes.append(clazz.innerclasses[i])
                        analyse_it(clazz.innerclasses[i], class_inner_classes)

                inner_classes = []
                analyse_it(diff[1 if diff[0] is None else 0], inner_classes)

                for r in map(lambda x: [[None if diff[0] is None else x, x if diff[0] is None else None], None],
                             inner_classes):
                    ret.append(r)

        return ret

    @staticmethod
    def _parse_class(class_content):
        clazz = smalanalysis.smali.objects.SmaliClass(None)

        # Class declaration
        reading_method = None
        reading_annotation = None
        current_obj = clazz

        line_nr = -1
        for line in class_content.split('\n'):
            line_nr += 1
            if len(line) > 0 and line[0:1] != '#':
                if reading_method is not None:
                    if line == '.end method':
                        reading_method = None
                        current_obj = clazz
                    else:
                        reading_method.add_line(line.strip())
                    continue

                if line == '.end field':
                    current_obj = clazz
                    continue

                if reading_annotation is not None:
                    if line.strip() == '.end annotation':
                        current_obj.add_annotation(reading_annotation)
                        reading_annotation = None
                    else:
                        reading_annotation.add_line(line.strip())
                    continue

                matched = MATCHERS.clazz.match(line)
                if matched is not None:
                    clazz.set_name('%s;' % (matched.group(2).strip()))
                    clazz.add_modifiers_from_list(
                        matched.group(1).strip().split(' ') if matched.group(1) is not None else None)
                    continue

                if line.startswith('.super '):
                    clazz.set_super(line[len('.super'):].strip())
                    continue

                if line.startswith('.source '):
                    clazz.set_source(line[len('.source'):].replace('"', '').strip())
                    continue

                if line.startswith('.implements '):
                    clazz.add_mplemented_nterface(line[len('.implements'):].strip())
                    continue

                matched = MATCHERS.annotation.match(line.strip())
                if matched is not None:
                    modifiers = matched.group(1).strip().split(' ')
                    name = matched.group(2)

                    reading_annotation = smalanalysis.smali.objects.SmaliAnnotation(name, modifiers, clazz)
                    continue

                matched = MATCHERS.method.match(line)
                if matched is not None:
                    # Well this is a method...
                    modifiers = None
                    name = matched.group(2)
                    if name is None:
                        name = matched.group(1)
                    else:
                        modifiers = matched.group(1).strip().split(' ') if matched.group(1) is not None else None

                    name = name.strip()
                    parameters = [it[0] for it in MATCHERS.method_param.findall(matched.group(3))]

                    return_val = matched.group(4)

                    reading_method = smalanalysis.smali.objects.SmaliMethod(name, parameters, return_val, modifiers,
                                                                            clazz)
                    current_obj = reading_method
                    clazz.add_method(reading_method)
                    continue

                matched = MATCHERS.fields.match(line)
                if matched is not None:
                    field_type = matched.group(3)
                    field_init = None

                    matched2 = MATCHERS.field_init.match(field_type)
                    if matched2 is not None:
                        field_type = matched2.group(1)
                        field_init = matched2.group(3)[3:]

                    current_obj = smalanalysis.smali.objects.SmaliField(matched.group(2).strip(), field_type,
                                                                        matched.group(1).strip().split(
                                                                                ' ') if matched.group(
                                                                                1) is not None else None, field_init,
                                                                        clazz)
                    clazz.add_field(current_obj)
                    continue

                sys.stderr.write("Parsing error.\nLine: %s.\n" % line)
                sys.exit(1)

        return clazz

    def _parse_add_class(self, file):
        fp = open(file, 'r')
        ccontent = fp.read()
        fp.close()
        cls = SmaliProject._parse_class(ccontent)
        cls.parent = self
        self.add_class(cls)

    def equals(self, other, mappings=None):
        return smalanalysis.smali.objects.compare_lists_boolean(self.classes, other.classes)

    @staticmethod
    def _diff_anonymous_inner_classes(old, new, mappings):
        def only_unmatched(inner_classes, match_state):
            return filter(lambda x: x not in match_state, inner_classes)

        def _this_context_diff(context_old, context_new, context_mappings):
            ret = []
            for r in context_old.differences(context_new, [ComparisonIgnores.CLASS_NAME, ComparisonIgnores.FIELD_NAME],
                                             context_mappings):
                if r[2] == ChangeTypes.SAME_NAME or r[2] == ChangeTypes.REVISED_METHOD:
                    continue

                if len(r) > 3 and type(r[3]) == list and len(r[3]) == 1 and r[3][0] == "NOT_SAME_NAME":
                    continue

                ret.append(r)

            return ret

        # Let's compare inner classes to try to match them :)
        matches = []
        matched_old = []
        matched_new = []

        for old_inner_class_name in old.get_anonymous_inner_classes():
            for new_inner_class_name in only_unmatched(new.get_anonymous_inner_classes(), matched_new):
                diffs = _this_context_diff(old.innerclasses[old_inner_class_name],
                                          new.innerclasses[new_inner_class_name],
                                          mappings)

                if len(diffs) == 0:
                    matches.append((old.innerclasses[old_inner_class_name], new.innerclasses[new_inner_class_name]))
                    matched_old.append(old_inner_class_name)
                    matched_new.append(new_inner_class_name)
                    break

        return matches, \
               map(lambda x: old.innerclasses[x],
                   only_unmatched(old.get_anonymous_inner_classes(), matched_old)), \
               map(lambda x: new.innerclasses[x],
                   only_unmatched(new.get_anonymous_inner_classes(), matched_new))

    @staticmethod
    def _diff_non_anonymous_inner_classes(old, new, mappings):
        oldc = old.get_non_anonymous_inner_classes()
        oldk = set(list(oldc))
        newc = new.get_non_anonymous_inner_classes()
        newk = set(list(newc))

        matched, unmatched_old, unmatched_new = [], [], []

        for k in oldk.intersection(newk):
            matched.append((old.innerclasses[k], new.innerclasses[k]))

        for k in oldk - newk:
            unmatched_old.append(old.innerclasses[k])

        for k in newk - oldk:
            unmatched_new.append(new.innerclasses[k])

        return matched, unmatched_old, unmatched_new
