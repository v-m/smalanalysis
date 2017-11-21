# Detecting save/load instance state faults
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 17, 2017

import re
import smali.SmaliProject
import smali.SmaliInstructionMatchers

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

def compareMethod(method, matcher):
    return method.name == matcher[1] and ''.join(method.params) == matcher[2] and method.ret == matcher[3]

if __name__ == '__main__':

    path = "/Users/vince/Downloads/Kontak"
    path = "/Users/vince/Downloads/Kontak9"
    path = "/Users/vince/Temp/SW_072516d"           #V1
    path = "/Users/vince/Temp/SW_5b66df5"           #V2

    project = smali.SmaliProject.SmaliProject()
    project.parseFolder(path)



    for dentry in findClassesOfInterests(project):
        clazz = dentry["class"]
        type = dentry["type"]
        rootparent = dentry["rootparent"]

        # Let's look if developper override reading/writing methods...
        loadSave = findReadWriteMethods(type, clazz.methods)
        loadInstanceDeclaration = loadSave["load"]
        saveInstanceDeclaration = loadSave["save"]

        loadInvokeSuper = 0
        saveInvokeSuper = 0

        for k in loadInstanceDeclaration:
            invokeSuper = False
            for l in k.getCleanLines():
                super = smali.SmaliInstructionMatchers.matchSuperInvocation(l)

                if super is not None and compareMethod(k, super):
                    invokeSuper = True
                    #print('\t\t %s'%l)

            if invokeSuper:
                loadInvokeSuper += 1

            #print('\t- %s(%s). Invoke super = %s'%(k.name, ','.join(k.params), invokeSuper))

        for k in saveInstanceDeclaration:
            invokeSuper = False
            for l in k.getCleanLines():
                super = smali.SmaliInstructionMatchers.matchSuperInvocation(l)

                if super is not None and compareMethod(k, super):
                    invokeSuper = True
                    #print('\t\t %s'%l)

            if invokeSuper:
                saveInvokeSuper += 1

            #print('\t- %s(%s). Invoke super = %s'%(k.name, ','.join(k.params), invokeSuper))

        print('%s (%s). Load: %d/%d. Save: %d/%d.' % (clazz.getBaseName().replace('/', '.'), rootparent.split('/')[-1], loadInvokeSuper, len(loadInstanceDeclaration), saveInvokeSuper, len(saveInstanceDeclaration)))