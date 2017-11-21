# Regexp matcher for smali
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 21, 2017

import re

INVOKE_SUPER = re.compile("^invoke-super \{[pv0-9, ]*?\}, (.*)->(.*)\((.*)\)(.*)$")
INVOKE_VIRTUAL = re.compile("^invoke-virtual \{[pv0-9, ]*?\}, (.*)->(.*)\((.*)\)(.*)$")
INVOKE_VIRTUAL_BUNDLE_ACCESSES = re.compile("^invoke-virtual \{p1, (v[0-9]+?), v[0-9]+?\}, Landroid/os/Bundle;->(get|put)(.*)\(.*\)(.*)$")
INVOKE_VIRTUAL_BUNDLE_ACCESSES_ARRAY = re.compile("^invoke-virtual \{p1, (v[0-9]+?)\}, Landroid/os/Bundle;->(get|put)(.*)\(.*\)(.*)$")
CONST_STRING_INSTRUCTION = re.compile("^const-string (v[0-9]+?), \"(.*)\"$")

def matchSuperInvocation(smaliline):
    match  = INVOKE_SUPER.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()


def matchVirtualInvocation(smaliline):
    match  = INVOKE_VIRTUAL.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()


def matchVirtualInvocationBundleAccesses(smaliline):
    match  = INVOKE_VIRTUAL_BUNDLE_ACCESSES.match(smaliline.strip())

    if match is None:
        match = INVOKE_VIRTUAL_BUNDLE_ACCESSES_ARRAY.match(smaliline.strip())

        if match is None:
            return None

    #print('>>> ', smaliline)
    return match.groups()


def affectingString(smaliline):
    match = CONST_STRING_INSTRUCTION.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()