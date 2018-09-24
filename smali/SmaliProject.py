# Smali Projects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15

import re
import os

import sys
import zipfile

import smali.SmaliObject
from smali import ComparisonIgnores
from smali.ChangesTypes import REVISED_METHOD, SAME_NAME


class MATCHERS:
    obj = "(\\[*(L[a-zA-Z0-9/_$\\-]+;|Z|B|S|C|I|J|F|D|V))"
    method_reg = re.compile("\\.method( [a-z \\-]+?)*( [a-zA-Z0-9<>_$\\-]+){1}\\((.*)\\)(.*)") #Without obfuscation
    method = re.compile("\\.method( [a-z \\-]+?)*( [^ ]+){1}\\((.*)\\)(.*)")
    method_param = re.compile("%s"%obj)
    field_init = re.compile("%s( = .*)"%obj)
    fields_reg = re.compile("\\.field( [a-z ]+)*( [a-zA-Z0-9_$\\-]*)+?:(.*)")       #Without obfuscation
    fields = re.compile("\\.field( [a-z ]+)*( [^ ]*)+:([^:]*)")
    clazz = re.compile("\\.class( [a-z ]+)*( [a-zA-Z][a-zA-Z0-9_\\-/$]*)+?;")
    annotation = re.compile("\\.annotation( [a-z ]+)*( L[a-zA-Z0-9_/$]*);")
    ressource_classes = re.compile("^.*/R(\\$[a-z]+)?\\.smali$")
    hex_ref = re.compile("0x[0-9abcdef]{2,}")

class SmaliProject(object):
    def __init__(self):
        self.classes = []
        self.classesdict = {}
        self.ressources_id = set()

    def addClass(self, c):
        self.classes.append(c)
        self.classesdict[c.name] = c

    def parseRessource(self, ctnt):
        for line in ctnt.split('\n'):
            refs = MATCHERS.hex_ref.findall(line)

            for r in refs:
                self.ressources_id.add(r)

        pass


    def isProjectObfuscated(self):
        keep, skip = 0, 0

        obfuscatedclassname = re.compile("(.*/)?[a-z]{1,3};")

        for p in self.classes:
            obfuscatedclass = obfuscatedclassname.fullmatch(p.name) is not None
            if not obfuscatedclass:
                keep += 1
            else:
                skip += 1

        if keep == 0:
            return True

        return skip / keep > 0.75

    @staticmethod
    def shouldAnalyzeThisClass(classname, skips = None, includes = None, default = True):
        clazz = classname

        if '/' in classname:
            clazz = classname.replace('/', '.')

        if clazz[0] == '/':
            clazz = clazz[1:]

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


    # 1 = class / 2 = ressource / 0 = skip
    @staticmethod
    def keepThisFile(fullpath, package, includes, skips, includeUnpackaged):
        if fullpath.endswith('.smali'):
            skip = False

            if package is not None and package.replace('.', '/') not in fullpath:
                skip = True

            if MATCHERS.ressource_classes.match(fullpath):
                return 2

            if '/' not in fullpath:
                return 1 if includeUnpackaged else 0

            if (skips is not None or includes is not None):
                skip = not SmaliProject.shouldAnalyzeThisClass(fullpath, skips, includes, not skip)

            if fullpath.endswith('/BuildConfig.smali'):
                skip = True

            if not skip:
                return 1

        return 0

    def parseProject(self, folder, package = None, skiplists = None, includelist = None, includeUnpackaged = False):
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

        if os.path.isfile(folder):
            # This is a ZIP
            zp = zipfile.ZipFile(folder, 'r')
            SmaliProject.parseZipLoop(zp, self, package, skips=skips, includes=includes, includeUnpackaged = includeUnpackaged)
        else:
            print("Parsing folder not supported anymore. Please use archive mode.")
            #SmaliProject.parseFolderLoop(folder, folder, self, package, skips=skips, includes=includes, includeUnpackaged = includeUnpackaged)

    @staticmethod
    def parseZipLoop(zp, target, package=None, skips=None, includes=None, includeUnpackaged=False):
        classes = {}
        innerClasses = []

        for n in zp.namelist():
            op = SmaliProject.keepThisFile(n, package, includes, skips, includeUnpackaged)

            if op == 1:
                ccontent = "".join(map(chr, zp.read(n)))
                cls = SmaliProject.parseClass(ccontent)
                cls.parent = target

                m2 = cls.name[1:-1].split("$")
                if len(m2) > 1:
                    innerClasses.append((cls, m2[0], m2[1:]))
                else:
                    classes[cls.name[1:-1]] = cls
                    target.addClass(cls)

            elif op == 2:
                ccontent = "".join(map(chr, zp.read(n)))
                target.parseRessource(ccontent)

        # Deal with inner classes now
        looplevel = 0
        processedAtLeastOne = True

        while (processedAtLeastOne):
            processedAtLeastOne = False
            looplevel += 1

            for e in innerClasses:
                # if e[1] not in classes:
                #     missingClass = SmaliClass(old)
                #     missingClass.name = "L{};".format(e[1])
                #     classes[e[1]] = missingClass
                #     print("PUSHING {}".format(missingClass.name))
                #     target.addClass(missingClass)

                targetclass = classes[e[1]]
                innerClassPath = list(e[2][:-1])

                if len(e[2]) == looplevel:
                    while (len(innerClassPath) > 0):
                        newLevel = innerClassPath.pop()

                        # if newLevel not in targetclass.innerclasses:
                        #     missingClass = SmaliClass(old)
                        #     newClassName = "L{}{};".format(targetclass.name[1:-1], newLevel)
                        #     missingClass.name = newClassName
                        #     targetclass.innerclasses[newLevel] = missingClass

                    targetclass.innerclasses[e[2][-1]] = e[0]
                    e[0].parent = targetclass
                    e[0].innername = '$'.join(e[2])
                    processedAtLeastOne = True

    def searchClass(self, clazzName):
        searchfor = clazzName

        if '/' not in searchfor and '.' in searchfor:
            searchfor = searchfor.replace('/', '.')

        if not (searchfor[0] == 'L' and searchfor[-1] == ';'):
            searchfor = 'L%s;'%(searchfor)

        for c in self.classes:
            if c is None or c.name is None:
                continue

            if searchfor == c.name:
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

    def differences(self, other, ignores, processInnerClasses=True):
        ret = []
        dd = self.matchClasses(other)
        classesMatching = {}

        def appendMatchedCase(sim):
            classesMatching[sim[0].name] = sim[1].name
            rret = list()
            diff = sim[0].differences(sim[1], ignores)
            if len(diff) > 0:
                rret.extend(diff)
            ret.append([sim, rret])


        for sim in dd[0]:
            appendMatchedCase(sim)

        for diff in dd[1]:
            ret.append([diff, None])

        """
        Additional code for handling inner classes
        """
        if processInnerClasses:
            processClasses = []
            for old, new in dd[0]:
                if old.hasInnerClasses() or new.hasInnerClasses():
                    processClasses.append((old, new))
                elif len(old.innerclasses) + len(new.innerclasses) > 0:
                    # Should not happen
                    assert(False)

            while len(processClasses) > 0:
                popped = processClasses.pop()

                old, new = popped
                result = SmaliProject.diffAnonymousInnerClasses(old, new, classesMatching)

                for matched in result[0]:
                    appendMatchedCase(matched)
                    if matched[0].hasInnerClasses() or matched[1].hasInnerClasses():
                        processClasses.append((matched[0], matched[1]))

                for droppedInnerClasses in result[1]:
                    ret.append([[droppedInnerClasses, None], None])

                for insertedInnerClasses in result[2]:
                    ret.append([[None, insertedInnerClasses], None])

                result = SmaliProject.diffNonAnonymousInnerClasses(old, new, classesMatching)
                for matched in result[0]:
                    appendMatchedCase(matched)
                    if matched[0].hasInnerClasses() or matched[1].hasInnerClasses():
                        processClasses.append((matched[0], matched[1]))

                for droppedInnerClasses in result[1]:
                    ret.append([[droppedInnerClasses, None], None])

                for insertedInnerClasses in result[2]:
                    ret.append([[None, insertedInnerClasses], None])

            #Not matched inner classes
            for diff in dd[1]:
                def analyseIt(clazz, innerclasses):
                    for i in clazz.innerclasses:
                        innerclasses.append(clazz.innerclasses[i])
                        analyseIt(clazz.innerclasses[i], innerclasses)

                innerclasses = []
                analyseIt(diff[1 if diff[0] is None else 0], innerclasses)

                for r in map(lambda x: [[None if diff[0] is None else x, x if diff[0] is None else None], None], innerclasses):
                    ret.append(r)

        return ret

    @staticmethod
    def parseClass(ccontent):
        clazz = smali.SmaliObject.SmaliClass(None)

        # Class declaration
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

        return clazz

    def parseAddClass(self, file):
        fp = open(file, 'r')
        ccontent = fp.read()
        fp.close()
        cls = SmaliProject.parseClass(ccontent)
        cls.parent = self
        self.addClass(cls)

    # def __eq__(self, other):
    #
    #     # FIXIT Do not use __eq__ directly !
    #     assert (False)

    def equals(self, other, mappings=None):
        return smali.compareListsBoolean(self.classes, other.classes)

    # def signatureEq(self, other):
    #     return compareListsBoolean(self.classes, other.classes, True)

    @staticmethod
    def diffAnonymousInnerClasses(old, new, mappings):
        def onlyUnmatched(innerclasses, matchState):
            return filter(lambda x: x not in matchState, innerclasses)

        def thisContextDiff(old, new, mappings):
            ret = []
            for r in old.differences(new, [ComparisonIgnores.CLASS_NAME, ComparisonIgnores.FIELD_NAME], mappings):
                if r[2] == SAME_NAME or r[2] == REVISED_METHOD:
                    continue

                if len(r) > 3 and type(r[3]) == list and len(r[3]) == 1 and r[3][0] == "NOT_SAME_NAME":
                    continue

                ret.append(r)

            return ret

        # Let's compare inner classes to try to match them :)
        matches = []
        matchedOld = []
        matchedNew = []

        for oldinnerclassname in old.getAnonymousInnerClasses():
            for newinnerclassname in onlyUnmatched(new.getAnonymousInnerClasses(), matchedNew):
                diffs = thisContextDiff(old.innerclasses[oldinnerclassname], new.innerclasses[newinnerclassname],
                                        mappings)

                if len(diffs) == 0:
                    # print("\tMatched old ${} and new ${}".format(oldinnerclassname, newinnerclassname))
                    matches.append((old.innerclasses[oldinnerclassname], new.innerclasses[newinnerclassname]))
                    matchedOld.append(oldinnerclassname)
                    matchedNew.append(newinnerclassname)
                    # mappings[old.innerclasses[oldinnerclassname].name] = new.innerclasses[newinnerclassname].name
                    # found = True
                    break
                # elif len(diffs) == 1:
                # print("\tUN-Matched old ${} and new ${} = {}".format(oldinnerclassname, newinnerclassname, diffs))
                # thisContextDiff(old.innerclasses[oldinnerclassname], new.innerclasses[newinnerclassname], mappings)

        # OK, let's see what remains now...
        # for oldinnerclassname in onlyUnmatched(old.getAnonymousInnerClasses(), matchedOld):
        #     print("\tUNMATCHED OLD = {}".format(oldinnerclassname))
        #
        # for newinnerclassname in onlyUnmatched(new.getAnonymousInnerClasses(), matchedNew):
        #     print("\tUNMATCHED NEW = {}".format(newinnerclassname))

        return matches, \
               map(lambda x: old.innerclasses[x],
                   onlyUnmatched(old.getAnonymousInnerClasses(), matchedOld)), \
               map(lambda x: new.innerclasses[x],
                   onlyUnmatched(new.getAnonymousInnerClasses(), matchedNew))

    @staticmethod
    def diffNonAnonymousInnerClasses(old, new, mappings):
        oldc = old.getNonAnonymousInnerClasses()
        oldk = set(list(oldc))
        newc = new.getNonAnonymousInnerClasses()
        newk = set(list(newc))

        matched, unmatchedold, unmatchednew = [], [], []

        for k in oldk.intersection(newk):
            matched.append((old.innerclasses[k], new.innerclasses[k]))
            # print(old.innerclasses[k].differences(old.innerclasses[k], mappings))

        for k in oldk - newk:
            unmatchedold.append(old.innerclasses[k])
            # print("REMOVED: {}".format(k))

        for k in newk - oldk:
            unmatchednew.append(new.innerclasses[k])
            # print("ADDED: {}".format(k))

        return matched, unmatchedold, unmatchednew