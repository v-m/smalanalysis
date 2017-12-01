# Detecting save/load instance state faults
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 17, 2017
import argparse
import re
import sys
import colors

import smali.SmaliProject
import smali.SmaliInstructionMatchers as sim
from tools.android import *

#https://developer.android.com/reference/android/app/Activity.html
#https://developer.android.com/reference/android/app/Dialog.html
#https://developer.android.com/reference/android/support/v4/app/Fragment.html

#<a href="https://developer.android.com/reference/(.*?).html">(.*?)</a>,
#'$1',\n

android_support_matcher = re.compile('^Landroid/support/+.*')


findAlertDialogInstance_pattern_lines = [re.compile('^new-instance [vp][0-9]+, Landroid/support/v7/app/AlertDialog\$Builder;$'),
                                         re.compile('^invoke-virtual {[vp][0-9]+}, .*->getActivity\(\)L.*/FragmentActivity;$'),
                                         re.compile('^invoke-direct {[vp][0-9]+, [vp][0-9]+}, Landroid/support/v7/app/AlertDialog\$Builder;-><init>\(Landroid/content/Context;\)V$')
]


def isThisMethods(method, name, returnval, parameters):
    if method.name != name:
        return False

    if method.ret != returnval:
        return False

    if len(method.params) != len(parameters):
        return False

    for p in range(len(method.params)):
        if method.params[p] != parameters[p]:
            return False

    return True

def inspectMethodForActivity(method):
    if isThisMethods(method, 'onSaveInstanceState', 'V', ['Landroid/os/Bundle;']):
        return 'S'
    elif isThisMethods(method, 'onSaveInstanceState', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;']):
        return 'S'
    elif isThisMethods(method, 'onRestoreInstanceState', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onRestoreInstanceState', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;']):
        return 'R'
    elif isThisMethods(method, 'onCreate', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;']):
        return 'R'
    elif isThisMethods(method, 'onCreate', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onPostCreate', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;']):
        return 'R'
    elif isThisMethods(method, 'onPostCreate', 'V', ['Landroid/os/Bundle;']):
        return 'R'

    return None

def inspectMethodForDialog(method):
    if isThisMethods(method, 'onSaveInstanceState', 'Landroid/os/Bundle;', []):
        return 'S'
    elif isThisMethods(method, 'onRestoreInstanceState', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onCreate', 'V', ['Landroid/os/Bundle;']):
        return 'R'

    return None


def inspectMethodForView(method):
    if isThisMethods(method, 'onSaveInstanceState', 'Landroid/os/Parcelable;', []):
        return 'S'
    elif isThisMethods(method, 'onRestoreInstanceState', 'V', ['Landroid/os/Parcelable;']):
        return 'R'
    #TODO What about saveHierarchyState(SparseArray), dispatchSaveInstanceState(SparseArray), setSaveEnabled(boolean).
    return None


def inspectMethodForFragment(method):
    if isThisMethods(method, 'onSaveInstanceState', 'V', ['Landroid/os/Bundle;']):
        return 'S'
    elif isThisMethods(method, 'onCreate', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    #onCreateDialog(Landroid/os/Bundle;)Landroid/app/Dialog;
    elif isThisMethods(method, 'onCreateDialog', 'Landroid/app/Dialog;', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onCreateView', 'Landroid/view/View;', ['Landroid/view/LayoutInflater;', 'Landroid/view/ViewGroup;', 'Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onActivityCreated', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onViewStateRestored', 'V', ['Landroid/os/Bundle;']):
        return 'R'

def hierarchyHasSetItem(hierarchy, theSet):
    for setItem in theSet:
        for element in hierarchy:
            if element[1:-1] == setItem:
                return setItem

    return None




def findClassesOfInterests(project):
    #retList = []

    total = len(project.classes)
    i = 0
    for clazz in project.classes:
        i+=1

        ret = clazz.determineParentClassHierarchyNames()
        rootparent = ret[-1][1:-1]

        # If we are not looking at something inheriting a class
        # which may deal with orientation stuffs, then skip...
        type = None
        if rootparent in SDK_KNOWN_ACTIVITIES_REF:
            type = 'A'
        elif rootparent in SDK_KNOWN_DIALOG_REF:
            type = 'D'
        elif rootparent in SDK_KNOWN_VIEWS_REF:
            type = 'V'

        if type is None:
            rootparent = hierarchyHasSetItem(ret, SDK_KNOWN_FRAGMENT_REF)
            if rootparent is not None:
                type = 'F'

        if type is None:
            continue

        # Do not analyze android support SDK classes
        if android_support_matcher.match(clazz.name):
            continue

        #retList.append({"class": clazz, "rootparent": rootparent, "type": type})
        yield {"class": clazz, "rootparent": rootparent, "type": type, "nb": i, "total": total}

    #return retList

def findReadWriteMethods(type, methods):
    loadInstanceDeclaration = []
    saveInstanceDeclaration = []

    for method in methods:
        if type == 'A':
            accesstype = inspectMethodForActivity(method)
            if accesstype == 'R':
                loadInstanceDeclaration.append(method)
            elif accesstype == 'S':
                saveInstanceDeclaration.append(method)


        elif type == 'D':
            accesstype = inspectMethodForDialog(method)
            if accesstype == 'R':
                loadInstanceDeclaration.append(method)
            elif accesstype == 'S':
                saveInstanceDeclaration.append(method)

        elif type == 'V':
            accesstype = inspectMethodForView(method)
            if accesstype == 'R':
                loadInstanceDeclaration.append(method)
            elif accesstype == 'S':
                saveInstanceDeclaration.append(method)

        elif type == 'F':
            accesstype = inspectMethodForFragment(method)
            if accesstype == 'R':
                loadInstanceDeclaration.append(method)
            elif accesstype == 'S':
                saveInstanceDeclaration.append(method)

    return {"load": loadInstanceDeclaration, "save": saveInstanceDeclaration}

def isThisOnCreateMethod(m):
    return isThisMethods(m, 'onCreate', 'V', ['Landroid/os/Bundle;']) or isThisMethods(m, 'onCreate', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;'])

def findOnCreateMethods(methods):
    ret = []

    for m in methods:
        if isThisOnCreateMethod(m):
            ret.append(m)

    return ret

def compareMethod(method, matcher):
    return method.name == matcher[1] and ''.join(method.params) == matcher[2] and method.ret == matcher[3]

def isSuperInvoked(method, onlySameIdentities = True):
    supers = []

    for l in method.getCleanLines():
        super = sim.matchSuperInvocation(l)

        if super is not None:
            if onlySameIdentities:
                if compareMethod(method, super):
                    supers.append(l)
            else:
                supers.append(l)

    return supers

def superInvokations(method):
    supers = []

    for l in method.getCleanLines():
        super = sim.matchSuperInvocation(l)

        if super is not None:
            supers.append((l, compareMethod(method, super)))

    return supers

def isAlertDialogBuilderInstantiated(method):
    currentmatch = 0

    for l in method.getCleanLines():
        if findAlertDialogInstance_pattern_lines[currentmatch].match(l):
            currentmatch += 1

        if currentmatch >= len(findAlertDialogInstance_pattern_lines):
            return True

    return False


def isThereAnyBundleProtection(method):
    for l in method.getCleanLines():
        if l.startswith('if-nez p1, :') or l.startswith('if-eqz p1, :'):
            return True

    return False

def listContainerAccesses(method, keepDynamics = True, container = sim.INVOKE_VIRTUAL_BUNDLE_ACCESSES):
    ret = []

    lastKey = {}

    line = 0

    reg = findTargetParameterPosition(method)

    for l in method.getCleanLines():
        #print(l)
        match = sim.affectingString(l)

        if match is not None:
            lastKey[match[1]] = match[2]

        match = sim.matchVirtualInvocationContainerAccesses(l, reg, container)

        if match is not None:
            if match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0] not in lastKey:
                if keepDynamics:
                    match[sim.VIRTUAL_INVOCATION_ENTRIES.DYNAMICALLY_OBTAINED] = True
                    match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0] = '?%s?l%d?' % (match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0], line)
            else:
                match[sim.VIRTUAL_INVOCATION_ENTRIES.DYNAMICALLY_OBTAINED] = False
                remthis = match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0]
                match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0] = lastKey[match[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0]]
                del lastKey[remthis]

            ret.append(match)

        line += 1

    return ret

def listBundleAccessesFollowingCalls(method, missing, project):
    ret = []

    analyzing = None

    for l in method.getCleanLines():
        #print(l)
        match = sim.affectingString(l)

        if match is not None:
            if analyzing is not None:
                analyzing = None
                #print('Matching ended')

            if match[2] in missing:
                analyzing = match
                #print('Matching: ', match)

            #print(l)

        if analyzing is not None:
            match = sim.matchVirtualOrDirectInvocation(l)

            if match is not None:
                reg = [s.strip() for s in match[1].split(',')]

                if analyzing[0] in reg:

                    # Are we able to find the class/method in analyzed methods?
                    relclass = project.searchClass(match[2])

                    if relclass is not None:
                        relmeth = relclass.findMethod(*match[3:])
                        #print(relmeth)

                        if relmeth is not None:
                            # If the methods takes a Bundle parameter...
                            if 'Landroid/os/Bundle;' in relmeth.params:
                                reg = findTargetParameterPosition(relmeth)

                                for ll in relmeth.getCleanLines():
                                    match = sim.matchVirtualInvocationBundleAccesses(ll, reg)

                                    if match is not None:
                                        #action = match[1]
                                        #type = match[2]
                                        #print('*****', ll, match[1])
                                        match[0] = analyzing[1]
                                        ret.append(match)

    if len(ret) == 0:
        return None

    return ret

# Determine the Bundle position in the parameters of a method...
def findTargetParameterPosition(method):
    if 'Landroid/os/Bundle;' in method.params:
        return 'p%d'%(method.params.index('Landroid/os/Bundle;') + 1)
    elif 'Landroid/os/Parcelable;' in method.params:
        return 'p%d' % (method.params.index('Landroid/os/Parcelable;') + 1)
    return None


##########
##########
##
##  PATTERNS IMPLEMENTATION
##
##########
##########



# PATTERN 3 --
# Bundle data acces is protected by == null or != null check ?
def bundleAccessIsProtectedByNullCheckWholeProject(instances):
    unprotectedMethods = []

    for instance in instances:
        m, isread, bac = instance

        if isThisOnCreateMethod(m) and bac is not None:
            # We access the bundle... So let's check if it is protected...
            if not isThereAnyBundleProtection(m):
                unprotectedMethods.append(m.getSignature())

    return unprotectedMethods







# PATTERN 4a --
# Are all bundle item saved well loaded?
def bundleReadWhatIsWrittenWholeClass(instances):
    bundleAccessesCount = 0
    bundleAccessesCountMeth = 0
    bundles = [set(), set()]
    dynamicBundles = [0,0]

    for instance in instances:
        m, isread, bac = instance

        if bac is not None:
            bundleAccessesCountMeth += 1
            for b in bac:
                bundleAccessesCount += 1
                target = 0 if b[sim.VIRTUAL_INVOCATION_ENTRIES.METHOD] == 'get' else 1

                if b[sim.VIRTUAL_INVOCATION_ENTRIES.DYNAMICALLY_OBTAINED]:
                    dynamicBundles[target] += 1
                else:
                    bundles[target].add(b[sim.VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0])

    # print("Bundle contains %d items..." % (max(len(readBundle), len(writeBundle))))
    return {"meth_bundles_accesses": bundleAccessesCountMeth,
            "total_bundles_accesses": bundleAccessesCount,
            "static_bundle_read": bundles[0],
            "static_bundle_write": bundles[1],
            "dynamic_bundle_read": dynamicBundles[0],
            "dynamic_bundle_write": dynamicBundles[1]
            }

    #return list(symdiff)
    #if len(symdiff) > 0:
    #    print("Read/Write not done symmetricly. Incoherent items: %s." % ','.join(symdiff))


def bundleReadWhatIsWrittenRecursive(methods, missing, project):
    readBundle = missing['static_bundle_read']
    writeBundle = missing['static_bundle_write']

    for amethod in methods:
        bac = listBundleAccessesFollowingCalls(amethod, readBundle ^ writeBundle, project)
        #print(bac)
        if bac is not None:
            for b in bac:
                if b[sim.VIRTUAL_INVOCATION_ENTRIES.DYNAMICALLY_OBTAINED]:
                    if b[1] == 'get':
                        readBundle.add(b[0])
                    else:
                        writeBundle.add(b[0])

    return readBundle, writeBundle

# TODO find new cases with that !
def bundleReadWhatIsWrittenRecursiveWholeProject(instances, missing, project):
    readBundle = missing['static_bundle_read']
    writeBundle = missing['static_bundle_write']

    for instance in instances:
        m, isread, bac = instance

        # Recompute bac
        bac = listBundleAccessesFollowingCalls(m, readBundle ^ writeBundle, project)
        #print(bac)

        if bac is not None:
            for b in bac:
                if b[sim.VIRTUAL_INVOCATION_ENTRIES.DYNAMICALLY_OBTAINED]:
                    if b[1] == 'get':
                        readBundle.add(b[0])
                    else:
                        writeBundle.add(b[0])

    return readBundle, writeBundle

# PATTERN 4b --
# Writing/loading type sanity check?
def bundleRespectTypeCoherenciesWholeProject(instances):
    occs = [[], []]

    for instance in instances:
        m, isread, bac = instance

        if bac is not None:
            for b in bac:
                ttable = 0 if b[sim.VIRTUAL_INVOCATION_ENTRIES.METHOD] == 'get' else 1
                occs[ttable].append(b[sim.VIRTUAL_INVOCATION_ENTRIES.TYPE])

    miss = {'read': [], 'write': []}
    cp = list(occs[1])
    for occ in occs[0]:
        if occ in cp:
            cp.remove(occ)
        else:
            miss['read'].append(occ)

    for occ in cp:
        miss['write'].append(occ)

    return miss



# PATTERN 2 --
# Are we calling super methods?
def whereSuperIsMissingWholeProject(instances, onlySameIdentities = True):
    missingSuper = []

    for instance in instances:
        m, isread, bac = instance

        # Super invokation analysis
        if len(isSuperInvoked(m, onlySameIdentities)) == 0:
            missingSuper.append(m)

    return missingSuper

# PATTERN 2 detailed --
# Are we calling super methods?
def superCallsWholeProject(instances):
    supers = {}

    for instance in instances:
        m, isread, bac = instance

        if m.getSignature() not in supers:
            supers[m.getSignature()] = []

        [supers[m.getSignature()].append(i) for i in superInvokations(m)]

    return supers

# Return the onCreateDialog methods which are invoking the AlertDialog builder...
def alertDialogBuilderInvokedOn(methods):
    invokedOn = []

    for k in methods:
        if isThisMethods(k, 'onCreateDialog', 'Landroid/app/Dialog;', ['Landroid/os/Bundle;']):
            if isAlertDialogBuilderInstantiated(k):
                invokedOn.append(k)

    return invokedOn


def process_csv(args, dentry, SEP):
    suspiciousCount = 0

    line = []

    clazz = dentry["class"]
    type = dentry["type"]
    rootparent = dentry["rootparent"]

    # Let's look if developper override reading/writing methods...
    loadSave = findReadWriteMethods(type, clazz.methods)
    loadInstanceDeclaration = loadSave["load"]
    saveInstanceDeclaration = loadSave["save"]

    if type == 'V':
        instances = listAllContainerAccesses(loadInstanceDeclaration, saveInstanceDeclaration, sim.INVOKE_VIRTUAL_PARCELABLE_ACCESSES)
    else:
        instances = listAllContainerAccesses(loadInstanceDeclaration, saveInstanceDeclaration, sim.INVOKE_VIRTUAL_BUNDLE_ACCESSES)

    # print(clazz.name, '\n')

    line.append(path)
    # line.append(clazz.getBaseName())
    line.append(clazz.name)
    line.append('%d' % len(clazz.fields))  # nb fields
    line.append('%d' % len(loadInstanceDeclaration))  # nb load methods
    line.append('%d' % len(saveInstanceDeclaration))  # nb save methods

    # PATTERN 3 -- Bundle data acces is protected by == null or != null check ?
    oncreatemeth = findOnCreateMethods(loadInstanceDeclaration)
    line.append('%d' % len(oncreatemeth))  # nb oncreatemeth

    # TODO PATTERN 4

    # 1. WE MATCH ONLY THE TYPES
    tmatching = bundleRespectTypeCoherenciesWholeProject(instances)

    line.append('%d' % len(tmatching['read']))  # nb type incoherencies R
    line.append('%d' % len(tmatching['write']))  # nb type incoherencies W
    lline = []

    for tm in tmatching['read']:
        lline.append('%s(R)' % (tm))
    for tm in tmatching['write']:
        lline.append('%s(W)' % (tm))
    line.append('%s' % ':'.join(lline))  # nb type incoherencies
    if len(line[-1]) > 0:
        suspiciousCount += 1

    # PATTERN 4a -- Are all static bundle item saved well loaded?
    rr = bundleReadWhatIsWrittenWholeClass(instances)
    line.append('%d' % rr['meth_bundles_accesses'])  # nb method accessing bundle
    line.append('%d' % rr['total_bundles_accesses'])  # nb of total bundle accesses
    line.append('%d' % rr['dynamic_bundle_read'])  # nb dynamic bundleaccesses read
    line.append('%d' % rr['dynamic_bundle_write'])  # nb dynamic bundleaccesses write
    if rr['dynamic_bundle_read'] != rr['dynamic_bundle_write']:
        suspiciousCount += 1

    # PATTERN 3 -- Bundle data acces is protected by == null or != null check ? (cont.)
    r = bundleAccessIsProtectedByNullCheckWholeProject(instances)
    line.append(':'.join(r))
    if len(line[-1]) > 0:
        suspiciousCount += 1

    # PATTERN 4a -- Are all bundle item saved well loaded? (cont.)
    symdiff = rr['static_bundle_read'] ^ rr['static_bundle_write']

    if not args.no_recursion and len(symdiff) > 0:
        # With not matched, just redo a deep analysis to ensure that the read/write is not occuring in external method...
        r = bundleReadWhatIsWrittenRecursive(loadInstanceDeclaration + saveInstanceDeclaration, rr, project)
        symdiff = r[0] ^ r[1]

    line.append(':'.join(symdiff))
    if len(line[-1]) > 0:
        suspiciousCount += 1

    # PATTERN 4b -- Writing/loading type sanity check?
    # r = bundleRespectTypeCoherencies(loadInstanceDeclaration + saveInstanceDeclaration)
    # line.append(':'.join(r))

    # PATTERN 2 -- Are we calling super methods?
    ## But before, let's check for FragmentDialog > onCreateDialog if we are using the AlertDialog.Builder handler...
    analyze_these = loadInstanceDeclaration + saveInstanceDeclaration
    # for meth in alertDialogBuilderInvokedOn(analyze_these):
    #    analyze_these.remove(meth)

    r = whereSuperIsMissingWholeProject(instances)
    line.append(':'.join(['%s(%s)' % (rr.name, ''.join(rr.params)) for rr in r]))
    if len(line[-1]) > 0:
        suspiciousCount += 1

    r = whereSuperIsMissingWholeProject(instances, False)
    line.append(':'.join(['%s(%s)' % (rr.name, ''.join(rr.params)) for rr in r]))
    if len(line[-1]) > 0:
        suspiciousCount += 1

    if not args.only_positives or suspiciousCount > 0:
        line.insert(0, '+' if suspiciousCount > 0 else '-')
        print(SEP.join(line))

def listAllContainerAccesses(loadInstanceDeclaration, saveInstanceDeclaration, container = sim.INVOKE_VIRTUAL_BUNDLE_ACCESSES):
    instances = []
    for m in loadInstanceDeclaration + saveInstanceDeclaration:
        instances.append((m, m in loadInstanceDeclaration, listContainerAccesses(m, container)))
    return instances

def process_details(args, dentry, SEP):
    lines = []

    mayBeIgnored = True

    clazz = dentry["class"]
    type = dentry["type"]
    rootparent = dentry["rootparent"]

    lines.append(colors.color('     Class: %s' % clazz.name, style='bold'))
    lines.append('Base class: %s' % rootparent)
    lines.append('      Type: %s' % type)
    lines.append('')

    loadSave = findReadWriteMethods(type, clazz.methods)
    loadInstanceDeclaration = loadSave["load"]
    saveInstanceDeclaration = loadSave["save"]

    if type == 'V':
        instances = listAllContainerAccesses(loadInstanceDeclaration, saveInstanceDeclaration, sim.INVOKE_VIRTUAL_PARCELABLE_ACCESSES)
    else:
        instances = listAllContainerAccesses(loadInstanceDeclaration, saveInstanceDeclaration, sim.INVOKE_VIRTUAL_BUNDLE_ACCESSES)

    #2
    supers = superCallsWholeProject(instances)

    #3
    missing_null_protection = bundleAccessIsProtectedByNullCheckWholeProject(instances)

    #4a
    read_write_incoherencies = bundleReadWhatIsWrittenWholeClass(instances)
    read_write_incoherencies_int = read_write_incoherencies['static_bundle_read'] ^ read_write_incoherencies['static_bundle_write']

    #4b
    read_write_types_incoherencies = bundleRespectTypeCoherenciesWholeProject(instances)

    lines.append('Bundle access statistics:')
    lines.append('\tBundle accessed %d times in %d methods.' % (read_write_incoherencies['total_bundles_accesses'], read_write_incoherencies['meth_bundles_accesses']))

    lines.append('\tStatic R/W: %d/%d' % (len(read_write_incoherencies['static_bundle_read']), len(read_write_incoherencies['static_bundle_write'])))
    if(len(read_write_incoherencies['static_bundle_read']) != len(read_write_incoherencies['static_bundle_write'])):
        lline = lines.pop()
        lline = '%s%s' % (lline, colors.color(' (incoherencies may exist - see Method Analysis)', fg='red'))
        lines.append(lline)
        mayBeIgnored = False
    lines.append('\tDynamic R/W: %d/%d' % (read_write_incoherencies['dynamic_bundle_read'], read_write_incoherencies['dynamic_bundle_write']))
    if(read_write_incoherencies['dynamic_bundle_read'] != read_write_incoherencies['dynamic_bundle_write']):
        lline = lines.pop()
        lline = '%s%s' % (lline, colors.color(' (incoherencies may exist)', fg='red'))
        lines.append(lline)
        mayBeIgnored = False

    #lines.append('')

    if len(read_write_types_incoherencies['read']) > 0:
        lines.append(colors.color('\tTypes read not written: %s' % (','.join(read_write_types_incoherencies['read'])), fg='red'))
        mayBeIgnored = False
    #else:
    #    lines.append('\tAny types read and not written.')


    if len(read_write_types_incoherencies['write']) > 0:
        lines.append(colors.color('\tTypes written not read: %s' % (','.join(read_write_types_incoherencies['write'])), fg='red'))
        mayBeIgnored = False
    #else:
    #    lines.append('\tAny types written and not read.')

    lines.append('')

    lines.append('Method analysis:')
    clen = len(lines)
    for aninstance in instances:
        mayBeIgnored = False
        m, isread, bac = aninstance

        adds = []

        if m.getSignature() in missing_null_protection:
            adds.append(colors.color('[not null protected]', fg='red'))
        else:
            adds.append(colors.color('[null protected or not needed]', fg='green'))

        lines.append('\t\t* [%s] %s %s' %('REA' if isread else 'WRI', m.getSignature(), ' '.join(adds)))

        found = False
        if m.getSignature() in supers:
            lines.append('\t\t\t- Super calls:')
            for sups in supers[m.getSignature()]:
                if not found:
                    found = sups[1]

                aline = '\t\t\t\t: %s' % (sups[0])

                if sups[1]:
                    aline = colors.color('%s (self)' % (aline), fg='green')

                lines.append(aline)

        if not found:
            lines.append(colors.color('\t WARNING: Self super not called', fg='red'))

        if m.getSignature() not in supers:
            lines.append(colors.color('\t WARNING: No super called at all', fg='red'))

        lines.append('\t\t\t- Containers accesses:')
        cclen = len(lines)

        for b in bac:
            if b['dynamic']:
                lines.append('\t\t\t\t: [DYN] %s' % (b))
            else:
                name = b['registers'][0]

                if name in read_write_incoherencies_int:
                    name = colors.color(name, fg='red')

                lines.append('\t\t\t\t: [STA] %s (%s)' % (name, b['type']))#, b))

        if cclen == len(lines):
            lines.pop()
            lines.append('\t\t\t- No container access found.')

    if clen == len(lines):
        lines.pop()
        lines.append('No interesting methods found.')

    s = ""
    lines.append(colors.color(''.join(['%s%s' % (s, ' ') for i in range(150)]), style='underline'))

    return '\n'.join(lines), mayBeIgnored

if __name__ == '__main__':
    SEP = ','

    parser = argparse.ArgumentParser(description='Search for instance state errors')
    parser.add_argument('smali', type=str, help='Folder containing smali files')
    parser.add_argument('--only-positives', '-p', action='store_true', help='Display only suspicious elements')
    parser.add_argument('--header', '-H', action='store_true', help='Print the CSV header')
    parser.add_argument('--exclude-lists', '-e', type=str, nargs='*', help='Files containing excluded lits')
    parser.add_argument('--include-lists', '-i', type=str, nargs='*', help='Files containing included lits')
    parser.add_argument('--tab', '-T', action='store_true', help='Separate columns using tab instead of semicolon.')
    parser.add_argument('--no-recursion', action='store_true', help='Disable recusion resolving to speed up the process.')
    parser.add_argument('--details', action='store_true', help='Get a detailed report instead of a summary CSV file.')
    parser.add_argument('--html', action='store_true', help='Produce such detailed report in HTML format.')
    parser.add_argument('--no-activities', action='store_true', help='Report do not includes Activities.')
    parser.add_argument('--no-fragments', action='store_true', help='Report do not includes Fragments.')
    parser.add_argument('--no-dialogs', action='store_true', help='Report do not includes Dialogs.')
    parser.add_argument('--no-views', action='store_true', help='Report do not includes Views.')

    args = parser.parse_args()
    path = args.smali

    if args.tab:
        SEP = '\t'

    if args.header:
        fields = ['S', 'Apk', 'Class', '#fields', '#meth_R', '#meth_W', '#meth_oncreate', '#types_incoh_R', '#types_incoh_W', 'types_incoh', '#meth_bundles_acc', '#bundles_acc', 'P4_#dyn_bundle_R', 'P4_#dyn_bundle_W', 'P3_#bundle_access_prot', 'P4_#static_bundle_incoh', 'P2_#super_call_miss_same_ID', 'P2_#super_call_miss_any_ID']
        print(SEP.join(fields))

    sys.stderr.write('Starting parsing smali project...\n')
    sys.stderr.flush()
    project = smali.SmaliProject.SmaliProject()
    project.parseProject(path, None, args.exclude_lists, args.include_lists)
    sys.stderr.write('Project parsed. Starting analysis...\n')
    sys.stderr.flush()

    sys.stderr.write('Looking for classes of interests...\n')
    sys.stderr.flush()
    #classes =
    #sys.stderr.write('Starting parsing smali project...\n')
    #sys.stderr.flush()

    #nbclasses = len(classes)
    #sys.stderr.write('%d classes found...\n' % nbclasses)
    #sys.stderr.flush()

    from ansi2html import Ansi2HTMLConverter
    conv = Ansi2HTMLConverter(dark_bg=False)
    all = []

    for dentry in findClassesOfInterests(project):
        if args.no_dialogs and dentry["type"] == 'D':
            continue
        if args.no_activities and dentry["type"] == 'A':
            continue
        if args.no_fragments and dentry["type"] == 'F':
            continue
        if args.no_views and dentry["type"] == 'V':
            continue

        sys.stderr.write('Class %d/%d = %s of type %s...\n' % (dentry["nb"], dentry["total"], dentry["class"].name, dentry["rootparent"]))
        sys.stderr.flush()

        if args.details:
            line = process_details(args, dentry, SEP)

            if not args.only_positives or (args.only_positives and not line[1]):
                if args.html:
                    all.append(line[0])
                else:
                    print(line[0])
        else:
            process_csv(args, dentry, SEP)

    if args.details and args.html:
        ret = conv.convert('\n'.join(all))
        #ret = ret.replace('.body_background { background-color: #AAAAAA; }', '.body_background { background-color: #FFFFFF; }')
        ret = ret.replace('<body class="body_foreground body_background"', '<body')
        print(ret)