import re
import os
from smali.SmaliObject import SmaliClass, SmaliField, SmaliAnnotation, SmaliMethod, compareListsBoolean

class MATCHERS:
    method = re.compile("\\.method( [a-z \\-]+?)?( [a-zA-Z0-9<>_$]+)?\\((.*)\\)(.*)")
    method_param = re.compile("(L[a-zA-Z0-9/]+;|Z|B|S|C|I|J|F|D)")
    field_init = re.compile("(L[a-zA-Z0-9/]+;|Z|B|S|C|I|J|F|D)( = .*)")
    fields = re.compile("\\.field( [a-z ]+)*( [a-zA-Z0-9_$]*)+?:(.*)")
    clazz = re.compile("\\.class( [a-z ]+)*( [a-zA-Z][a-zA-Z0-9_/$]*)+?;")
    annotation = re.compile("\\.annotation( [a-z ]+)*( L[a-zA-Z0-9_/$]*);")
    ressource_classes = re.compile("R(\\$[a-z]+)*\\.smali")

class SmaliProject(object):
    def __init__(self):
        self.classes = []

    def addClass(self, c):
        self.classes.append(c)

    @staticmethod
    def parseFolderLoop(f, target, package = None, root = None):
        if f[-1] == '/':
            f = f[:-1]

        if root is None:
            root = f

        for ff in os.listdir(f):
            fullpath = '%s%c%s' % (f, os.sep, ff)

            if os.path.isdir(fullpath):
                SmaliProject.parseFolderLoop(fullpath, target, package, root)
            elif fullpath.endswith('.smali'):
                if package is None or package.replace('.', '/') in fullpath:
                    if not MATCHERS.ressource_classes.match(ff):
                        target.addClass(SmaliProject.parseClass(fullpath))

    def parseFolder(self, folder, package = None):
        SmaliProject.parseFolderLoop(folder, self, package)

    def searchClass(self, clazzName):
        for c in self.classes:
            if c is None or c.name is None:
                continue

            if c.name[1:-1] == clazzName:
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

        clazz = SmaliClass()

        # Class declaration
        ccontent = fp.read()

        readingmethod = None
        readingannotation = None
        currentobj = clazz

        for line in ccontent.split('\n'):
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

                    readingannotation = SmaliAnnotation(name, modifiers)
                    continue

                matched = MATCHERS.method.match(line)
                if matched is not None:
                    # Well this is a method...
                    modifiers = matched.group(1).strip().split(' ') if matched.group(1) is not None else None
                    name = matched.group(2)
                    parameters = MATCHERS.method_param.findall(matched.group(3))
                    returnval = matched.group(4)

                    readingmethod = SmaliMethod(name, parameters, returnval, modifiers)
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
                        init = matched2.group(2)[3:]

                    currentobj = SmaliField(matched.group(2), type, matched.group(1).strip().split(' ') if matched.group(1) is not None else None, init)
                    clazz.addField(currentobj)
                    continue

                print(line)

        fp.close()
        return clazz

    def parseAddClass(self, file):
        self.addClass(SmaliProject.parseClass(file))

    def __eq__(self, other):
        return compareListsBoolean(self.classes, other.classes)

    def signatureEq(self, other):
        return compareListsBoolean(self.classes, other.classes, True)
