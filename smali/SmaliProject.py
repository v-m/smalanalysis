# Smali Projects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15

import re
import os

import sys

import smali.SmaliObject

class MATCHERS:
    obj = "(\\[*(L[a-zA-Z0-9/_$\\-]+;|Z|B|S|C|I|J|F|D|V))"
    method = re.compile("\\.method( [a-z \\-]+?)*( [a-zA-Z0-9<>_$\\-]+){1}\\((.*)\\)(.*)")
    method_param = re.compile("%s"%obj)
    field_init = re.compile("%s( = .*)"%obj)
    fields = re.compile("\\.field( [a-z ]+)*( [a-zA-Z0-9_$\\-]*)+?:(.*)")
    clazz = re.compile("\\.class( [a-z ]+)*( [a-zA-Z][a-zA-Z0-9_\\-/$]*)+?;")
    annotation = re.compile("\\.annotation( [a-z ]+)*( L[a-zA-Z0-9_/$]*);")
    ressource_classes = re.compile("^.*/R(\\$[a-z]+)?\\.smali$")
    hex_ref = re.compile("0x[0-9abcdef]{2,}")

class SmaliProject(object):
    def __init__(self):
        self.classes = []
        self.ressources_id = set()

    def addClass(self, c):
        self.classes.append(c)

    def parseRessource(self, f):
        fp = open(f, 'r')
        ctnt = fp.read()
        fp.close()

        for line in ctnt.split('\n'):
            refs = MATCHERS.hex_ref.findall(line)

            for r in refs:
                self.ressources_id.add(r)

        pass

    @staticmethod
    def shouldAnalyzeThisClass(classname, skips = None, includes = None, default = True):
        clazz = classname

        if '/' in classname:
            clazz = classname.replace('/', '.')[1:]

        if includes is not None:
            for include in includes:
                if include in clazz:
                    return True
        if skips is not None:
            for skip in skips:
                if skip in clazz:
                    return False
        return default

    @staticmethod
    def loadRulesList(fileslist):
        rules = set()

        if type(fileslist) == str:
            fileslist = [fileslist]

        for f in fileslist:
            rules = rules.union(SmaliProject.loadRulesListFromFile(f))

        return rules

    @staticmethod
    def loadRulesListFromFile(file):
        rules = set()

        for entry in open(file, 'r'):
            rules.add(entry.strip())

        return rules

    @staticmethod
    def parseFolderLoop(f, target, package = None, root = None, skips = None, includes = None):
        if f[-1] == '/':
            f = f[:-1]

        if root is None:
            root = f

        for ff in os.listdir(f):
            fullpath = '%s%c%s' % (f, os.sep, ff)

            if os.path.isdir(fullpath):
                SmaliProject.parseFolderLoop(fullpath, target, package, root, skips, includes)
            elif fullpath.endswith('.smali'):
                skip = False
                if package is not None and package.replace('.', '/') not in fullpath:
                    skip = True

                if MATCHERS.ressource_classes.match(fullpath):
                    target.parseRessource(fullpath)
                    skip = True

                if (skips is not None or includes is not None):
                    skip = not SmaliProject.shouldAnalyzeThisClass(fullpath, skips, includes, not skip)

                if fullpath.endswith('/BuildConfig.smali'):
                    skip = True

                if not skip:
                    cls = SmaliProject.parseClass(fullpath)
                    cls.parent = target
                    target.addClass(cls)

    def parseFolder(self, folder, package = None, skiplists = None, includelist = None):
        skips = None
        includes = None
        if skiplists is not None:
            skips = set()
            for s in skiplists:
                skips = skips.union(SmaliProject.loadRulesListFromFile(s))
        if includelist is not None:
            includes = set()
            for s in includelist:
                includes = includes.union(SmaliProject.loadRulesListFromFile(s))
        SmaliProject.parseFolderLoop(folder, self, package, skips=skips, includes=includes)

    def searchClass(self, clazzName):
        searchfor = clazzName

        if '/' not in searchfor and '.' in searchfor:
            searchfor = searchfor.replace('/', '.')

        if searchfor[0] == 'L' and searchfor[-1] == ';':
            searchfor = searchfor[1:-1]

        for c in self.classes:
            if c is None or c.name is None:
                continue

            if searchfor == clazzName:
                return c

        return None

    def matchClasses(self, other):
        old = list(self.classes)
        new = list(other.classes)
        old2 = list()

        differents = []
        similars = []

        while len(old) > 0:
            clazz = old.pop()

            found = False
            for c in new:
                if clazz.name == c.name:
                    similars.append([clazz, c])
                    new.remove(c)
                    found = True
                    break

            if not found:
                old2.append(clazz)

        while len(old2) > 0:
            clazz = old2.pop()

            found = False
            for c in new:
                if clazz.name.split('/')[-1] == c.name.split('/')[-1]:
                    similars.append([clazz, c])
                    new.remove(c)
                    found = True
                    break

            if not found:
                differents.append([clazz, None])

        while len(new) > 0:
            c = new.pop()
            differents.append([None, c])

        return similars, differents

    def differences(self, other, ignores):
        ret = []
        dd = self.matchClasses(other)

        for sim in dd[0]:
            rret = list()
            diff = sim[0].differences(sim[1], ignores)
            if len(diff) > 0:
                rret.extend(diff)

            ret.append([sim, rret])

        for diff in dd[1]:
            ret.append([diff, None])

        return ret

    @staticmethod
    def parseClass(file):
        fp = open(file, 'r')

        clazz = smali.SmaliObject.SmaliClass(None)

        # Class declaration
        ccontent = fp.read()

        readingmethod = None
        readingannotation = None
        currentobj = clazz

        linenr = -1
        for line in ccontent.split('\n'):
            linenr += 1
            if len(line) > 0 and line[0:1] != '#':
                if readingmethod is not None:
                    if line == '.end method':
                        readingmethod = None
                        currentobj = clazz
                    else:
                        readingmethod.addLine(line.strip())
                    continue

                if line == '.end field':
                    currentobj = clazz
                    continue

                if readingannotation is not None:
                    if line.strip() == '.end annotation':
                        currentobj.addAnnotation(readingannotation)
                        readingannotation = None
                    else:
                        readingannotation.addLine(line.strip())
                    continue

                matched = MATCHERS.clazz.match(line)
                if matched is not None:
                    clazz.setName('%s;' % (matched.group(2).strip()))
                    clazz.addModifiersFromList(matched.group(1).strip().split(' ') if matched.group(1) is not None else None)
                    continue

                if line.startswith('.super '):
                    clazz.setSuper(line[len('.super'):].strip())
                    continue

                if line.startswith('.source '):
                    clazz.setSource(line[len('.source'):].replace('"', '').strip())
                    continue

                if line.startswith('.implements '):
                    clazz.addImplementedInterface(line[len('.implements'):].strip())
                    continue

                matched = MATCHERS.annotation.match(line.strip())
                if matched is not None:
                    modifiers = matched.group(1).strip().split(' ')
                    name = matched.group(2)

                    readingannotation = smali.SmaliObject.SmaliAnnotation(name, modifiers, clazz)
                    continue

                matched = MATCHERS.method.match(line)
                if matched is not None:
                    # Well this is a method...
                    modifiers = None
                    name = matched.group(2)
                    if name is None:
                        name = matched.group(1)
                    else:
                        modifiers = matched.group(1).strip().split(' ') if matched.group(1) is not None else None

                    name = name.strip()
                    parameters = [it[0] for it in MATCHERS.method_param.findall(matched.group(3)) ]

                    returnval = matched.group(4)

                    readingmethod = smali.SmaliObject.SmaliMethod(name, parameters, returnval, modifiers, clazz)
                    currentobj = readingmethod
                    clazz.addMethod(readingmethod)
                    continue

                matched = MATCHERS.fields.match(line)
                if matched is not None:
                    type = matched.group(3)
                    init = None

                    matched2 = MATCHERS.field_init.match(type)
                    if matched2 is not None:
                        type = matched2.group(1)
                        init = matched2.group(3)[3:]

                    currentobj = smali.SmaliObject.SmaliField(matched.group(2).strip(), type, matched.group(1).strip().split(' ') if matched.group(1) is not None else None, init, clazz)
                    clazz.addField(currentobj)
                    continue

                sys.stderr.write("Parsing error.\nLine: %s.\n"%line)
                sys.exit(1)



        fp.close()
        return clazz

    def parseAddClass(self, file):
        cls = SmaliProject.parseClass(file)
        cls.parent = self
        self.addClass(cls)

    def __eq__(self, other):
        return compareListsBoolean(self.classes, other.classes)

    def signatureEq(self, other):
        return compareListsBoolean(self.classes, other.classes, True)
