# Computing Metrics
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15
import argparse
import smali.SmaliObject
import smali.ChangesTypes
import smali.SmaliProject
from smali import SmaliObject, ChangesTypes, SmaliProject
import sys

def isEvolution(l):
    atLeastOne = False

    for d in l:
        if d[1] is None:
            return False
        elif d[0] is None and d[2] == ChangesTypes.NOT_FOUND:
            atLeastOne = True
        elif d[2] == ChangesTypes.REVISED_METHOD:
            pass
        else:
            return False

    return atLeastOne


def isMethodBodyChangeOnly(l):
    for d in l:
        if d[2] is not smali.ChangesTypes.REVISED_METHOD:
            return False

    return True


def isChange(l):
    return len(l) > 0 and not isEvolution(l) and not isMethodBodyChangeOnly(l)


def skipThisClass(skips, clazz):
    if clazz[0][1] is not None:
        if SmaliObject.SmaliClass.getDisplayName(clazz[0][1].name) not in skips:
            return True

    if clazz[0][0] is not None:
        if SmaliObject.SmaliClass.getDisplayName(clazz[0][0].name) not in skips:
            return True

    return False


class ProjectObfuscatedException(Exception):
    pass


def printName(m):
    return "{}.{}".format(m.parent.getDisplayName(m.parent.name), m.getSignature())


keys = ["#C-", "#C+", "#M-", "#M+", "E", "B", "A", "D", "C", "MA", "MD", "MR", "MC", "MRev", "FA", "FD", "FC", "FR", "CA", "CD", "CC"]


def initMetricsDict(key, ret):
    for k in keys:
        ret["{}{}".format(key, k)] = 0

    ret["{}addedLines".format(key)] = set()
    ret["{}removedLines".format(key)] = set()


def computeMetrics(r, out, metricKey="", diffOpOnly=True, aggregateOps=False):
    changedclass = set()

    for rr in r:
        if rr[1] is None:
            # Class change level here...
            if rr[0][1] is None:
                out["{}CD".format(metricKey)] += 1
                out["{}#C-".format(metricKey)] += 1
                continue
            elif rr[0][0] is None:
                out["{}CA".format(metricKey)] += 1
                out["{}#C+".format(metricKey)] += 1
                continue

        out["{}#C-".format(metricKey)] += 1
        out["{}#C+".format(metricKey)] += 1

        if len(rr[1]) == 0:
            continue

        changedclass.add(rr[0][0].name)

        l = rr[1]

        if isEvolution(l):
            out["{}E".format(metricKey)] += 1

        if isMethodBodyChangeOnly(l):
            out["{}B".format(metricKey)] += 1

        if isChange(l):
            out["{}C".format(metricKey)] += 1

        atLeastOneMethodAdded, atLeastOneMethodDeleted = False, False
        for rrr in rr[1]:
            if rrr[0] is not None and rrr[0].isField() and rrr[1] is None:
                out["{}FD".format(metricKey)] += 1
            elif rrr[1] is not None and rrr[1].isField() and rrr[0] is None:
                out["{}FA".format(metricKey)] += 1
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].isField():
                if len(rrr) > 3 and len(rrr[3]) == 1 and rrr[3][0] == SmaliObject.NOT_SAME_NAME:
                    out["{}FR".format(metricKey)] += 1
                else:
                    out["{}FC".format(metricKey)] += 1
            elif rrr[0] is not None and rrr[0].isMethod() and rrr[1] is None:
                out["{}MD".format(metricKey)] += 1
                atLeastOneMethodDeleted = True
            elif rrr[1] is not None and rrr[1].isMethod() and rrr[0] is None:
                out["{}MA".format(metricKey)] += 1
                atLeastOneMethodAdded = True
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].isMethod():
                if rrr[2] == ChangesTypes.RENAMED_METHOD:
                    out["{}MR".format(metricKey)] += 1
                else:
                    out["{}MC".format(metricKey)] += 1
                    if not rrr[0].areSourceCodeSimilars(rrr[1]):
                        out["{}MRev".format(metricKey)] += 1

                    l = set(rrr[1].getCleanLines()) - set(rrr[0].getCleanLines())
                    if diffOpOnly:
                        l = list(map(lambda x: x.split(' ')[0], l))
                    for cmd in l:
                        if aggregateOps:
                            cmd = cmd.split('/')[0].split('-')[0]
                        out["{}addedLines".format(metricKey)].add(cmd)

                    l = set(rrr[0].getCleanLines()) - set(rrr[1].getCleanLines())
                    if diffOpOnly:
                        l = list(map(lambda x: x.split(' ')[0], l))
                    for cmd in l:
                        if aggregateOps:
                            cmd = cmd.split('/')[0].split('-')[0]
                        out["{}removedLines".format(metricKey)].add(cmd)

        out["{}CC".format(metricKey)] += len(changedclass)
        out["{}A".format(metricKey)] += 1 if atLeastOneMethodAdded else 0
        out["{}D".format(metricKey)] += 1 if atLeastOneMethodDeleted else 0


def splitInnerOuterChanged(diff):
    innerDiff, outerDiff = [], []

    for d in diff:
        if (d[0][0] is not None and "$" in d[0][0].name) or (d[0][1] is not None and "$" in d[0][1].name):
            innerDiff.append(d)
        else:
            outerDiff.append(d)

    return innerDiff, outerDiff


def countMethodsInProject(project):
    cpt = 0
    incpt = 0

    for c in project.classes:
        cpt += len(c.methods)

        for ic in c.innerclasses:
            incpt += countMethodsInClass(c.innerclasses[ic])

    return cpt, incpt

def countMethodsInClass(clazz):
    cpt = len(clazz.methods)

    for ic in clazz.innerclasses:
        cpt += countMethodsInClass(clazz.innerclasses[ic])

    return cpt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute evolution metrics between two smali versions.')
    parser.add_argument('smaliv1', type=str,
                        help='Version 1 folder containing smali files')
    parser.add_argument('smaliv2', type=str,
                        help='Version 2 folder containing smali files')
    parser.add_argument('pkg', type=str,
                        help='The app package name')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show metrics details')
    parser.add_argument('--onlyapppackage', '-P', action='store_true',
                        help='Includes only classes in the app package specified')
    parser.add_argument('--fulllinesofcode', '-f', action='store_true',
                        help='Show full lines instead of opcodes for differences')
    parser.add_argument('--aggregateoperators', '-a', action='store_true',
                        help='Aggregate the operator by their first keywork.')
    parser.add_argument('--include-unpackaged', '-U', action='store_true',
                        help='Includes classes which are not in a package')
    parser.add_argument('--exclude-lists', '-e', type=str, nargs='*',
                        help='Files containing excluded list')
    parser.add_argument('--include-lists', '-i', type=str, nargs='*',
                        help='Files containing included list')
    parser.add_argument('--no-innerclasses-split', '-I', action='store_true',
                        help='Do not split metrics for inner/outer classes')

    args = parser.parse_args()

    pkg = None
    if args.onlyapppackage:
        pkg = args.pkg
        if args.verbose:
            print("Including classes only in %s" % pkg)

    if args.verbose and args.exclude_lists:
        print("Ignoring classes includes in these files: %s" % args.exclude_lists)

    if args.aggregateoperators and args.fulllinesofcode:
        print("Aggregation and full lines cannot be enabled at the same time!")
        sys.exit(1)

    try:
        old = smali.SmaliProject.SmaliProject()
        old.parseProject(args.smaliv1, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)
        #parseProject(old, args.smaliv1, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)

        if old.isProjectObfuscated():
            raise ProjectObfuscatedException()

        mold, moldin = countMethodsInProject(old)

        new = smali.SmaliProject.SmaliProject()
        new.parseProject(args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)
        #parseProject(new, args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)

        mnew, mnewin = countMethodsInProject(new)

        if new.isProjectObfuscated():
            raise ProjectObfuscatedException()

        diff = old.differences(new, [])

        metrics = {}

        if args.no_innerclasses_split:
            initMetricsDict("", metrics)
            metrics["#M-"] = mold + moldin
            metrics["#M+"] =  mnew + mnewin
            computeMetrics(diff, metrics, "", not args.fulllinesofcode, args.aggregateoperators)

        else:
            innerDiff, outerDiff = splitInnerOuterChanged(diff)

            initMetricsDict("OUT", metrics)
            initMetricsDict("IN", metrics)
            metrics["IN#M-"] = moldin
            metrics["IN#M+"] = mnewin
            metrics["OUT#M-"] = mold
            metrics["OUT#M+"] = mnew

            computeMetrics(outerDiff, metrics, "OUT", not args.fulllinesofcode, args.aggregateoperators)
            computeMetrics(innerDiff, metrics, "IN", not args.fulllinesofcode, args.aggregateoperators)

    except ProjectObfuscatedException:
        print("This project is obfuscated. Unable to proceed.", file=sys.stderr)
        sys.exit(1)

    bases = [""]
    if not args.no_innerclasses_split:
        bases = ["IN", "OUT"]

    if args.verbose:
        for b in bases:
            if len(b) > 0:
                print("===== {} CLASSES =====".format(b))

            print("v0 has {} classes/{} methods, v1 has {} classes/{} methods.".format(metrics["{}{}".format(b, "#C-")], metrics["{}{}".format(b, "#M-")], metrics["{}{}".format(b, "#C+")], metrics["{}{}".format(b, "#M+")]))
            print("B = %d. A = %d. D = %d." % (metrics["{}{}".format(b, "B")], metrics["{}{}".format(b, "A")], metrics["{}{}".format(b, "D")]))
            print("E = %d. C = %d." % (metrics["{}{}".format(b, "E")], metrics["{}{}".format(b, "C")]))
            print("Classes - Added: %5d, Changed: %5d, Deleted: %5d." % (metrics["{}{}".format(b, "CA")], metrics["{}{}".format(b, "CC")], metrics["{}{}".format(b, "CD")]))
            print("Methods - Added: %5d, Revised: %5d, Changed: %5d, Renamed: %5d, Deleted: %5d." % (
            metrics["{}{}".format(b, "MA")], metrics["{}{}".format(b, "MRev")], metrics["{}{}".format(b, "MC")], metrics["{}{}".format(b, "MR")], metrics["{}{}".format(b, "MD")]))
            print(" Fields - Added: %5d, Changed: %5d, Renamed: %5d, Deleted: %5d." % (
            metrics["{}{}".format(b, "FA")], metrics["{}{}".format(b, "FC")], metrics["{}{}".format(b, "FR")], metrics["{}{}".format(b, "FD")]))
            print("Added lines:")
            for l in metrics["{}{}".format(b, "addedLines")]:
                print("\t- {}".format(l))
            print("Removed lines:")
            for l in metrics["{}{}".format(b, "removedLines")]:
                print("\t- {}".format(l))
    else:
        # for b in bases:
        #     for k in keys:
        #         print("{}{},".format(b, k), end='')
        #
        #     print("{}addedLines,{}removedLines,".format(b, b), end='')
        #
        # print("")

        for b in bases:
            for k in keys:
                print("%d," % metrics["{}{}".format(b, k)], end='')
            print('|'.join(metrics["{}addedLines".format(b)]), end='')
            print(",", end='')
            print('|'.join(metrics["{}removedLines".format(b)]), end='')
            print(",", end='')

        print("")
