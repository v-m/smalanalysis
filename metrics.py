# Computing Metrics
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15
import argparse
import sys
import smali.SmaliObject
import smali.ChangesTypes
import smali.SmaliProject
from smali import SmaliObject, ChangesTypes


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

def isRevision(l):
    for d in l:
        if d[2] is not smali.ChangesTypes.REVISED_METHOD:
            return False

    return True

def isChange(l):
    return len(l) > 0 and not isEvolution(l) and not isRevision(l)

def skipThisClass(skips, clazz):
    if clazz[0][1] is not None:
        if SmaliObject.SmaliClass.getDisplayName(clazz[0][1].name) not in skips:
            return True

    if clazz[0][0] is not None:
        if SmaliObject.SmaliClass.getDisplayName(clazz[0][0].name) not in skips:
            return True

    return False

def computeMetrics(v1, v2, pkg):
    old = smali.SmaliProject.SmaliProject()
    old.parseFolder(v1, pkg)
    new = smali.SmaliProject.SmaliProject()
    new.parseFolder(v2, pkg)

    E, R, C = 0, 0, 0
    MA, MD, MC = 0, 0, 0
    FA, FD, FC = 0, 0, 0
    CA, CD, CC = 0, 0, 0

    r = old.differences(new, [])

    for rr in r:
        if args.classes is not None:
            if skipThisClass(args.classes, rr):
                continue

        if rr[1] is None:
            # Class change level here...
            if rr[0][1] is None:
                CD += 1
                continue
            elif rr[0][0] is None:
                CA += 1
                continue

        CC += 1

        l = rr[1]

        if isEvolution(l):
            E += 1

        if isRevision(l):
            R += 1

        if isChange(l):
            C += 1

        for rrr in rr[1]:
            if rrr[0] is not None and rrr[0].isField() and rrr[1] is None:
                FD += 1
            elif rrr[1] is not None and rrr[1].isField() and rrr[0] is None:
                FA += 1
            elif rrr[0] is not None and rrr[0] is not None and rrr[0].isField():
                FC += 1
            elif rrr[0] is not None and rrr[0].isMethod() and rrr[1] is None:
                MD += 1
            elif rrr[1] is not None and rrr[1].isMethod() and rrr[0] is None:
                MA += 1
            elif rrr[0] is not None and rrr[0] is not None and rrr[0].isMethod():
                MC += 1

    return len(old.classes), len(new.classes), E,R,C,CA,CD,CC,MA,MD,MC,FA,FD,FC

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
    parser.add_argument('--classes', type=str, nargs='*',
                        help='Include only these classes')

    args = parser.parse_args()

    oldclasses,newclasses,E,R,C,MA,MD,MC,FA,FD,FC,CA,CD,CC = computeMetrics(args.smaliv1, args.smaliv2, args.pkg)

    if args.verbose:
        print("v0 has %d classes, v1 has %d classes."%(oldclasses, newclasses))
        print("E = %d. R = %d. C = %d" % (E, R, C))
        print("Classes - Added: %5d, Changed: %5d, Deleted: %5d." % (CA, CC, CD))
        print("Methods - Added: %5d, Changed: %5d, Deleted: %5d." % (MA, MC, MD))
        print(" Fields - Added: %5d, Changed: %5d, Deleted: %5d." % (FA, FC, FD))
    else:
        print("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d"%(oldclasses, newclasses, E,R,C, MA,MD,MC, FA,FD,FC, CA,CD,CC))