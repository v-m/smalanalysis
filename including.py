# Showing the way diffdex includes or not packages
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-26
import argparse
import sys

import re

import smali.SmaliObject
import smali.ChangesTypes
import smali.SmaliProject
from smali import SmaliObject, ChangesTypes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List project classes and the way diffdex includes/excludes it.')
    parser.add_argument('smali', type=str,
                        help='Folder containing smali files')
    parser.add_argument('pkg', type=str,
                        help='The app package name')
    parser.add_argument('--onlyapppackage', '-P', action='store_true',
                        help='Includes only classes in the app package')
    parser.add_argument('--exclude-lists', '-e', type=str, nargs='*',
                        help='Files containing exclude lists')
    parser.add_argument('--include-lists', '-i', type=str, nargs='*',
                        help='Files containing included lits')

    args = parser.parse_args()

    pkg = None
    if args.onlyapppackage:
        pkg = args.pkg
        print("Including only classes in %s"%pkg)

    if args.exclude_lists:
        print("Ignoring classes included in these files: %s"%args.exclude_lists)


    if args.include_lists:
        print("Considering classes included in these files: %s"%args.include_lists)

    run = smali.SmaliProject.SmaliProject()
    run.parseFolder(args.smali, pkg, args.exclude_lists, args.include_lists)

    included = set()
    for c in run.classes:
        included.add(c.name)

    all = smali.SmaliProject.SmaliProject()
    all.parseFolder(args.smali, None, None, None)

    pattern = re.compile('L(.*)/(.*);')

    pakgs = dict()
    status = dict()

    skips = dict()

    if args.exclude_lists is not None:
        for ff in args.exclude_lists:
            skips[ff] = smali.SmaliProject.SmaliProject.loadSkipList(ff)


    includes = dict()

    if args.include_lists is not None:
        for ff in args.include_lists:
            includes[ff] = smali.SmaliProject.SmaliProject.loadSkipList(ff)

    for c in all.classes:
        ret = pattern.match(c.name)
        pakg, clazz = ret.group(1).replace('/', '.'), ret.group(2)

        if pakg not in pakgs:
            pakgs[pakg] = set()

        pakgs[pakg].add((clazz, c.name in included))

    for pakg in pakgs:

        why = None

        if pkg is not None and pakg != args.pkg:
            why = "NOT IN APP PKG"

        for excllist in skips:
            for p in skips[excllist]:
                if p in pakg:
                    why = 'EXCLUDED BY %s'%excllist

        for incllist in includes:
            for p in includes[incllist]:
                if p in pakg:
                    why = 'INCLUDED BY %s' % incllist

        for clazz in pakgs[pakg]:
            if clazz[1]:
                print('%75s %s' % (pakg, '\033[92mANALYZED\033[39m %s'%("" if why is None else why)))
            else:
                print('%75s - %s' % (pakg, '\033[91mSKIPPED\033[39m %s'%("" if why is None else why)))

            break