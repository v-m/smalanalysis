# Detecting save/load instance state faults
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 17, 2017
import argparse
import re

import sys

import smali.SmaliProject
import smali.SmaliInstructionMatchers as sim

#https://developer.android.com/reference/android/app/Activity.html
#https://developer.android.com/reference/android/app/Dialog.html
#https://developer.android.com/reference/android/support/v4/app/Fragment.html

#<a href="https://developer.android.com/reference/(.*?).html">(.*?)</a>,
#'$1',\n

SDK_KNOWN_ACTIVITIES_REF = ('android/app/Activity',
                                'android/accounts/AccountAuthenticatorActivity',
                                'android/app/ActivityGroup',
                                'android/app/AliasActivity',
                                'android/app/ExpandableListActivity',
                                'android/app/ListActivity',
                                'android/app/NativeActivity',
                                'android/app/LauncherActivity',
                                'android/preference/PreferenceActivity',
                                'android/app/TabActivity')

SDK_KNOWN_DIALOG_REF = ('android/app/Dialog',
                                'android/app/AlertDialog',
                                'android/text/method/CharacterPickerDialog',
                                'android/app/Presentation',
                                'android/app/DatePickerDialog',
                                'android/app/ProgressDialog',
                                'android/app/TimePickerDialog')

SDK_KNOWN_FRAGMENT_REF = ('android/support/v17/leanback/app/BrandedSupportFragment',
                            'android/support/v4/app/DialogFragment',
                            'android/support/v17/leanback/app/GuidedStepSupportFragment',
                            'android/support/v17/leanback/app/HeadersSupportFragment',
                            'android/support/v4/app/ListFragment',
                            'android/support/v7/app/MediaRouteDiscoveryFragment',
                            'android/support/v17/leanback/app/OnboardingSupportFragment',
                            'android/support/v17/leanback/app/PlaybackSupportFragment',
                            'android/support/v7/preference/PreferenceFragmentCompat',
                            'android/support/v17/leanback/app/RowsSupportFragment',
                            'android/support/v17/leanback/app/SearchSupportFragment',
                            'android/support/v17/leanback/app/BaseSupportFragment',
                            'android/support/design/widget/BottomSheetDialogFragment',
                            'android/support/v17/leanback/app/BrowseSupportFragment',
                            'android/support/v17/leanback/app/DetailsSupportFragment',
                            'android/support/v7/preference/EditTextPreferenceDialogFragmentCompat',
                            'android/support/v17/leanback/app/ErrorSupportFragment',
                            'android/support/v7/preference/ListPreferenceDialogFragmentCompat',
                            'android/support/v7/app/MediaRouteChooserDialogFragment',
                            'android/support/v7/app/MediaRouteControllerDialogFragment',
                            'android/support/v7/preference/MultiSelectListPreferenceDialogFragmentCompat',
                            'android/support/v7/preference/PreferenceDialogFragmentCompat',
                            'android/support/v17/leanback/app/VerticalGridSupportFragment',
                            'android/support/v17/leanback/app/VideoSupportFragment')


android_support_matcher = re.compile('^Landroid/support/v[47]+.*')



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


def inspectMethodForFragment(method):
    if isThisMethods(method, 'onSaveInstanceState', 'V', ['Landroid/os/Bundle;']):
        return 'S'
    elif isThisMethods(method, 'onCreate', 'V', ['Landroid/os/Bundle;']):
        return 'R'
    elif isThisMethods(method, 'onCreateView', 'V', ['Landroid/view/LayoutInflater;', 'Landroid/view/ViewGroup;', 'Landroid/os/Bundle;']):
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
    retList = []

    for clazz in project.classes:
        ret = clazz.determineParentClassHierarchyNames()
        rootparent = ret[-1][1:-1]

        # If we are not looking at something inheriting a class
        # which may deal with orientation stuffs, then skip...
        type = None
        if rootparent in SDK_KNOWN_ACTIVITIES_REF:
            type = 'A'
        #elif rootparent in SDK_KNOWN_DIALOG_REF:
        #    type = 'D'

        #if type is None:
        #    rootparent = hierarchyHasSetItem(ret, SDK_KNOWN_FRAGMENT_REF)
        #    if rootparent is not None:
        #        type = 'F'

        if type is None:
            continue

        # Do not analyze android support SDK classes
        if android_support_matcher.match(clazz.name):
            continue

        retList.append({"class": clazz, "rootparent": rootparent, "type": type})

    return retList

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
        '''
        elif type == 'D':
            accesstype = inspectMethodForDialog(method)
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
        '''

    return {"load": loadInstanceDeclaration, "save": saveInstanceDeclaration}

def findOnCreateMethods(methods):
    ret = []

    for m in methods:
        if isThisMethods(m, 'onCreate', 'V', ['Landroid/os/Bundle;']) or isThisMethods(m, 'onCreate', 'V', ['Landroid/os/Bundle;', 'Landroid/os/PersistableBundle;']):
            ret.append(m)

    return ret

def compareMethod(method, matcher):
    return method.name == matcher[1] and ''.join(method.params) == matcher[2] and method.ret == matcher[3]

def isSuperInvoked(method):
    for l in method.getCleanLines():
        super = sim.matchSuperInvocation(l)

        if super is not None and compareMethod(method, super):
            return True

    return False

def isThereAnyBundleProtection(method):
    for l in method.getCleanLines():
        if l.startswith('if-nez p1, :') or l.startswith('if-eqz p1, :'):
            return True

    return False

def listBundleAccesses(method):
    ret = []

    lastKey = {}

    for l in method.getCleanLines():
        #print(l)
        match = sim.affectingString(l)

        if match is not None:
            lastKey[match[0]] = match[1]

        match = sim.matchVirtualInvocationBundleAccesses(l)

        if match is not None:
            match = list(match)
            match[0] = lastKey[match[0]]
            ret.append(match)

    if len(ret) == 0:
        return None

    return ret



##########
##########
##
##  PATTERNS IMPLEMENTATION
##
##########
##########




# PATTERN 3 --
# Bundle data acces is protected by == null or != null check ?
def bundleAccessIsProtectedByNullCheck(methods):
    unprotectedMethods = []

    for amethod in methods:
        bac = listBundleAccesses(amethod)

        if bac is not None:
            # We access the bundle... So let's check if it is protected...
            if not isThereAnyBundleProtection(amethod):
                unprotectedMethods.append(bac)

    return unprotectedMethods

# PATTERN 4a --
# Are all bundle item saved well loaded?
def bundleReadWhatIsWritten(methods):
    writeBundle = set()
    readBundle = set()

    for amethod in methods:
        bac = listBundleAccesses(amethod)

        if bac is not None:
            for b in bac:
                if b[1] == 'get':
                    readBundle.add(b[0])
                else:
                    writeBundle.add(b[0])

    # print("Bundle contains %d items..." % (max(len(readBundle), len(writeBundle))))
    symdiff = readBundle ^ writeBundle

    return list(symdiff)
    #if len(symdiff) > 0:
    #    print("Read/Write not done symmetricly. Incoherent items: %s." % ','.join(symdiff))

# PATTERN 4b --
# Writing/loading type sanity check?
def bundleRespectTypeCoherencies(methods):
    dict = {}
    incoherent = set()

    for amethod in methods:
        bac = listBundleAccesses(amethod)

        if bac is not None:
            for b in bac:
                if b[0] not in dict:
                    dict[b[0]] = b[2]
                else:
                    if dict[b[0]] != b[2]:
                        incoherent.add(b[0])

    return list(incoherent)
    #print("Sanity types: %s" % ('OK' if len(incoherent) == 0 else 'ERROR'))

# PATTERN 2 -- 
# Are we calling super methods?
def superCalledOnAllMethods(methods):
    #loadInvokeSuper = 0
    #saveInvokeSuper = 0

    missingSuper = []

    for k in methods:
        # Super invokation analysis
        if not isSuperInvoked(k):
            missingSuper.append(k)
            #if k in loadInstanceDeclaration:
            #    loadInvokeSuper += 1
            #else:
            #    saveInvokeSuper += 1

    #print('%s (%s). Load: %d/%d. Save: %d/%d.' % (clazz.getBaseName().replace('/', '.'), rootparent.split('/')[-1], loadInvokeSuper, len(loadInstanceDeclaration), saveInvokeSuper, len(saveInstanceDeclaration)))
    return missingSuper


if __name__ == '__main__':
    #path = "/Users/vince/Downloads/Kontak"
    #path = "/Users/vince/Downloads/Kontak9"
    #path = "/Users/vince/Temp/SW_072516d"           #V1
    #path = "/Users/vince/Temp/SW_5b66df5"           #V2
    #path = "/Users/vince/Temp/SW_master"           #V2

    parser = argparse.ArgumentParser(description='Search for instance state errors')
    parser.add_argument('smali', type=str, help='Folder containing smali files')

    args = parser.parse_args()
    path = args.smali

    project = smali.SmaliProject.SmaliProject()
    project.parseFolder(path)

    print('Class, P3_bundle_access_protection, P4a_all_read_write, P4b_type_check, P2_super_calling')

    for dentry in findClassesOfInterests(project):
        clazz = dentry["class"]
        type = dentry["type"]
        rootparent = dentry["rootparent"]

        # Let's look if developper override reading/writing methods...
        loadSave = findReadWriteMethods(type, clazz.methods)
        loadInstanceDeclaration = loadSave["load"]
        saveInstanceDeclaration = loadSave["save"]

        #print(clazz.name, '\n')

        sys.stdout.write(clazz.getBaseName())
        sys.stdout.write(',')

        # PATTERN 3 -- Bundle data acces is protected by == null or != null check ?
        r = bundleAccessIsProtectedByNullCheck(findOnCreateMethods(loadInstanceDeclaration))
        sys.stdout.write(':'.join(r))
        sys.stdout.write(',')


        # PATTERN 4a -- Are all bundle item saved well loaded?
        r = bundleReadWhatIsWritten(loadInstanceDeclaration + saveInstanceDeclaration)
        sys.stdout.write(':'.join(r))
        sys.stdout.write(',')

        # PATTERN 4b -- Writing/loading type sanity check?
        r = bundleRespectTypeCoherencies(loadInstanceDeclaration + saveInstanceDeclaration)
        sys.stdout.write(':'.join(r))
        sys.stdout.write(',')

        # PATTERN 2 -- Are we calling super methods?
        r = superCalledOnAllMethods(loadInstanceDeclaration + saveInstanceDeclaration)
        sys.stdout.write(':'.join(['%s(%s)'%(rr.name, ''.join(rr.params)) for rr in r]))
        sys.stdout.write('\n')