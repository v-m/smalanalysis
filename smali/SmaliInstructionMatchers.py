# Regexp matcher for smali
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 21, 2017

import re

INVOKE_SUPER = re.compile("^invoke-super(/range)? \{[pv0-9,. ]*?\}, (.*)->(.*)\((.*)\)(.*)$")
INVOKE_VIRTUAL_DIRECT = re.compile("^invoke-(virtual|direct) \{([pv0-9, ]*?)\}, (.*)->(.*)\((.*)\)(.*)$")
INVOKE_VIRTUAL_BUNDLE_ACCESSES = re.compile("^invoke-virtual \{([0-9pv, ]*)\}, Landroid/os/Bundle;->(get|put)(.*)\((.*)\)(.*)$")
CONST_STRING_INSTRUCTION = re.compile("^const-string(/jumbo)? (v[0-9]+?), \"(.*)\"$")


class VIRTUAL_INVOCATION_ENTRIES:
    DYNAMICALLY_OBTAINED = 'dynamic'
    METHOD = 'method'
    TYPE = 'type'
    PARAMETERS = 'params'
    RETURN = 'ret'
    REGISTERS = 'registers'

def matchSuperInvocation(smaliline):
    match  = INVOKE_SUPER.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()[1:]


def matchVirtualOrDirectInvocation(smaliline):
    match  = INVOKE_VIRTUAL_DIRECT.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()


def matchVirtualInvocationBundleAccesses(smaliline, defregister):
    #print(smaliline.strip())
    match  = INVOKE_VIRTUAL_BUNDLE_ACCESSES.match(smaliline.strip())

    if match is not None:
        registers = match.groups()[0].replace(' ', '').split(',')
        _, method, operation, params, ret = match.groups()

        r = {
            VIRTUAL_INVOCATION_ENTRIES.METHOD: method,
            VIRTUAL_INVOCATION_ENTRIES.TYPE: operation,
            VIRTUAL_INVOCATION_ENTRIES.PARAMETERS: params,
            VIRTUAL_INVOCATION_ENTRIES.RETURN: ret,
            VIRTUAL_INVOCATION_ENTRIES.REGISTERS: registers
        }

        if r[VIRTUAL_INVOCATION_ENTRIES.REGISTERS][0] == defregister:
            r[VIRTUAL_INVOCATION_ENTRIES.REGISTERS] = r[VIRTUAL_INVOCATION_ENTRIES.REGISTERS][1:]
            return r

    return None


def affectingString(smaliline):
    match = CONST_STRING_INSTRUCTION.match(smaliline.strip())

    if match is None:
        return None

    return match.groups()