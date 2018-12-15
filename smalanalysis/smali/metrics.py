"""Metrics Functions"""

__author__ = "Vincenzo Musco (http://www.vmusco.com)"
__date__ = "2017-09-15"

from smalanalysis.smali.enums import ChangeTypes, DifferenceType


class ProjectObfuscatedException(BaseException):
    pass


def is_evolution(l):
    at_least_one = False

    for d in l:
        if d[1] is None:
            return False
        elif d[0] is None and d[2] == ChangeTypes.NOT_FOUND:
            at_least_one = True
        elif d[2] == ChangeTypes.REVISED_METHOD:
            pass
        else:
            return False

    return at_least_one


def is_method_body_change_only(l):
    for d in l:
        if d[2] is not ChangeTypes.REVISED_METHOD:
            return False

    return True


def is_change(l):
    return len(l) > 0 and not is_evolution(l) and not is_method_body_change_only(l)


def skip_this_class(skips, clazz):
    if clazz[0][1] is not None:
        if clazz[0][1].get_display_name() not in skips:
            return True

    if clazz[0][0] is not None:
        if clazz[0][0].get_display_name() not in skips:
            return True

    return False


def print_name(m):
    return "{}.{}".format(m.parent.get_display_name(), m.get_signature())


keys = ["#C-", "#C+", "#M-", "#M+", "E", "B", "A", "D", "C", "MA", "MD", "MR", "MC", "MRev", "FA", "FD", "FC", "FR",
        "CA", "CD", "CC"]


def init_metrics_dict(key, ret):
    for k in keys:
        ret["{}{}".format(key, k)] = 0

    ret["{}addedLines".format(key)] = set()
    ret["{}removedLines".format(key)] = set()


def compute_metrics(r, out, metric_key="", diff_ops_only=True, aggregate_ops=False):
    changed_class = set()

    for rr in r:
        if rr[1] is None:
            # Class change level here...
            if rr[0][1] is None:
                out["{}CD".format(metric_key)] += 1
                out["{}#C-".format(metric_key)] += 1
                continue
            elif rr[0][0] is None:
                out["{}CA".format(metric_key)] += 1
                out["{}#C+".format(metric_key)] += 1
                continue

        out["{}#C-".format(metric_key)] += 1
        out["{}#C+".format(metric_key)] += 1

        if len(rr[1]) == 0:
            continue

        changed_class.add(rr[0][0].name)

        l = rr[1]

        if is_evolution(l):
            out["{}E".format(metric_key)] += 1

        if is_method_body_change_only(l):
            out["{}B".format(metric_key)] += 1

        if is_change(l):
            out["{}C".format(metric_key)] += 1

        at_least_one_method_added, at_least_one_method_deleted = False, False
        for rrr in rr[1]:
            if rrr[0] is not None and rrr[0].is_field() and rrr[1] is None:
                out["{}FD".format(metric_key)] += 1
            elif rrr[1] is not None and rrr[1].is_field() and rrr[0] is None:
                out["{}FA".format(metric_key)] += 1
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].is_field():
                if len(rrr) > 3 and len(rrr[3]) == 1 and rrr[3][0] == DifferenceType.NOT_SAME_NAME:
                    out["{}FR".format(metric_key)] += 1
                else:
                    out["{}FC".format(metric_key)] += 1
            elif rrr[0] is not None and rrr[0].is_method() and rrr[1] is None:
                out["{}MD".format(metric_key)] += 1
                at_least_one_method_deleted = True
            elif rrr[1] is not None and rrr[1].is_method() and rrr[0] is None:
                out["{}MA".format(metric_key)] += 1
                at_least_one_method_added = True
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].is_method():
                if rrr[2] == ChangeTypes.RENAMED_METHOD:
                    out["{}MR".format(metric_key)] += 1
                else:
                    out["{}MC".format(metric_key)] += 1
                    if not rrr[0].are_source_code_similars(rrr[1]):
                        out["{}MRev".format(metric_key)] += 1

                    l = set(rrr[1].get_clean_lines()) - set(rrr[0].get_clean_lines())
                    if diff_ops_only:
                        l = list(map(lambda x: x.split(' ')[0], l))
                    for cmd in l:
                        if aggregate_ops:
                            cmd = cmd.split('/')[0].split('-')[0]
                        out["{}addedLines".format(metric_key)].add(cmd)

                    l = set(rrr[0].get_clean_lines()) - set(rrr[1].get_clean_lines())
                    if diff_ops_only:
                        l = list(map(lambda x: x.split(' ')[0], l))
                    for cmd in l:
                        if aggregate_ops:
                            cmd = cmd.split('/')[0].split('-')[0]
                        out["{}removedLines".format(metric_key)].add(cmd)

        out["{}CC".format(metric_key)] += len(changed_class)
        out["{}A".format(metric_key)] += 1 if at_least_one_method_added else 0
        out["{}D".format(metric_key)] += 1 if at_least_one_method_deleted else 0


def split_inner_outer_changed(diff):
    inner_diff, outer_diff = [], []

    for d in diff:
        if (d[0][0] is not None and "$" in d[0][0].name) or (d[0][1] is not None and "$" in d[0][1].name):
            inner_diff.append(d)
        else:
            outer_diff.append(d)

    return inner_diff, outer_diff


def count_methods_in_project(project):
    cpt = 0
    inner_cpt = 0

    for c in project.classes:
        cpt += len(c.methods)

        for ic in c.innerclasses:
            inner_cpt += count_methods_in_class(c.innerclasses[ic])

    return cpt, inner_cpt


def count_methods_in_class(clazz):
    cpt = len(clazz.methods)

    for ic in clazz.innerclasses:
        cpt += count_methods_in_class(clazz.innerclasses[ic])

    return cpt
