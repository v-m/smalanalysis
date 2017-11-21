# Regexp matcher for smali
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 21, 2017

import re

INVOKE_SUPER = re.compile("^invoke-super \{[pv0-9, ]*?\}, (.*)->(.*)\((.*)\)(.{1})$")
INVOKE_VIRTUAL = re.compile("^invoke-virtual \{[pv0-9, ]*?\}, (.*)->(.*)\((.*)\)(.{1})$")

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
