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

def computeMetrics(v1, v2, pkg, excludeListFiles=None, includeListFiles=None, includeUnpackaged = False):
    old = smali.SmaliProject.SmaliProject()
    old.parseProject(v1, pkg, excludeListFiles, includeListFiles, includeUnpackaged)
    new = smali.SmaliProject.SmaliProject()
    new.parseProject(v2, pkg, excludeListFiles, includeListFiles, includeUnpackaged)

    E, R, C = 0, 0, 0
    MA, MD, MC, MR = 0, 0, 0, 0
    FA, FD, FC, FR = 0, 0, 0, 0
    CA, CD = 0, 0
    changedclass = set()

    r = old.differences(new, [])

    for rr in r:
        if rr[1] is None:
            # Class change level here...
            if rr[0][1] is None:
                CD += 1
                continue
            elif rr[0][0] is None:
                CA += 1
                continue

        if len(rr[1]) == 0:
            continue

        changedclass.add(rr[0][0].name)

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
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].isField():
                if len(rrr) > 3 and len(rrr[3]) == 1 and rrr[3][0] == SmaliObject.NOT_SAME_NAME:
                    FR += 1
                else:
                    FC += 1
            elif rrr[0] is not None and rrr[0].isMethod() and rrr[1] is None:
                MD += 1
            elif rrr[1] is not None and rrr[1].isMethod() and rrr[0] is None:
                MA += 1
            elif rrr[0] is not None and rrr[1] is not None and rrr[0].isMethod():
                if rrr[2] == ChangesTypes.RENAMED_METHOD:
                    MR += 1
                else:
                    MC += 1

    CC = len(changedclass)
    return len(old.classes), len(new.classes),E,R,C,CA,CD,CC,MA,MD,MC,MR,FA,FD,FC,FR

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
    parser.add_argument('--include-unpackaged', '-U', action='store_true',
                        help='Includes classes which are not in a package')
    parser.add_argument('--exclude-lists', '-e', type=str, nargs='*',
                        help='Files containing excluded lits')
    parser.add_argument('--include-lists', '-i', type=str, nargs='*',
                        help='Files containing included lits')


    args = parser.parse_args()

    pkg = None
    if args.onlyapppackage:
        pkg = args.pkg
        if args.verbose:
            print("Including classes only in %s"%pkg)

    if args.verbose and args.exclude_lists:
        print("Ignoring classes includes in these files: %s"%args.exclude_lists)

    oldclasses,newclasses,E,R,C,CA,CD,CC,MA,MD,MC,MR,FA,FD,FC,FR = computeMetrics(args.smaliv1, args.smaliv2, pkg, args.exclude_lists, args.include_lists, args.include_unpackaged)

    if args.verbose:
        print("v0 has %d classes, v1 has %d classes."%(oldclasses, newclasses))
        print("E = %d. R = %d. C = %d." % (E, R, C))
        print("Classes - Added: %5d, Changed: %5d, Deleted: %5d." % (CA, CC, CD))
        print("Methods - Added: %5d, Changed: %5d, Renamed: %5d, Deleted: %5d." % (MA, MC, MR, MD))
        print(" Fields - Added: %5d, Changed: %5d, Renamed: %5d, Deleted: %5d." % (FA, FC, FR, FD))
    else:
        print("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d"%(oldclasses, newclasses,E,R,C,MA,MD,MC,MR,FA,FD,FC,FR,CA,CD,CC))