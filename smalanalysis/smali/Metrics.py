# Metrics Functions
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15

from smalanalysis.smali import ChangesTypes, SmaliObject

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
        if d[2] is not ChangesTypes.REVISED_METHOD:
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
