# Smali Objects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-15
import re

from smali import ComparisonIgnores, ChangesTypes

NOT_SAME_NAME = 'NOT_SAME_NAME'
NOT_SAME_RETURN_TYPE = 'NOT_SAME_RETURN_TYPE'
NOT_SAME_MODIFIERS = 'NOT_SAME_MODIFIERS'
NOT_SAME_PARAMETERS = 'NOT_SAME_PARAMETERS'
NOT_SAME_TYPE = 'NOT_SAME_TYPE'
NOT_SAME_SOURCECODE_LINES = 'NOT_SAME_SOURCECODE_LINES'
NOT_SAME_ANNOTATIONS = 'NOT_SAME_ANNOTATIONS'
NOT_SAME_PARENT = 'NOT_SAME_PARENT'
NOT_SAME_INIT_VALUE = 'NOT_SAME_INIT_VALUE'

NOT_SAME_INTERFACES = 'NOT_SAME_INTERFACES'

SELF = 'SELF'
OTHER = 'OTHER'

classnamepattern = re.compile("L(.*?)(\\$.+)*;")
methodcallpattern = re.compile("(.*)->(.*):(.*)")

def compareStringSets(m1, m2):
    for a in m1:
        if a not in m2:
            return False

    return True

def compareListsSameposition(l1, l2):
    if len(l1) != len(l2):
        return False

    for i in range(len(l1)):
        if not l1[i].__eq__(l2[i]):
            return False

    return True

def bidirectCompareLists(l1, l2, ignores = None):
    if ignores is None:
        ignores = []

    ret = []

    for m in compareLists(l1, l2, ignores):
        ret.append([SELF, m])

    for m in compareLists(l2, l1, ignores):
        ret.append([OTHER, m])

    return ret


def compareListsSignatureEq(l1, l2):
    missings = []

    if l1 is None and l2 is None:
        return missings
    elif l1 is not None and l2 is not None:
        for it1 in l1:
            found = False

            for it2 in l2:
                if it1==it2:
                    found = True
                    break

            if not found:
                missings.append(it1)
    else:
        return None

    return missings

def compareLists(l1, l2, ignores = None):
    if ignores is None:
        ignores = []

    missings = []

    if l1 is None and l2 is None:
        return missings
    elif l1 is not None and l2 is not None:
        for it1 in l1:
            found = False

            for it2 in l2:
                if type(it1) == str or type(it2) == str:
                    if it1 == it2:
                        found = True
                        break
                elif len(it1.differences(it2, ignores)) == 0:
                    found = True
                    break

            if not found:
                missings.append(it1)
    else:
        return None

    return missings

def compareListsBoolean(l1, l2):
    if l1 is None and l2 is None:
        return True
    elif l1 is not None and l2 is not None:
        for it1 in l1:
            found = False

            for it2 in l2:
                if it1.__eq__(it2):
                    found = True
                    break

            if not found:
                return False
    else:
        return False

    return True
















class SmaliAnnotableModifiable(object):
    def __init__(self):
        self.annotations = []
        self.modifiers = set()

    def addAnnotation(self, a):
        self.annotations.append(a)

    def addModifiersFromList(self, modifiers):
        if modifiers is None:
            return

        for m in modifiers:
            self.modifiers.add(m.strip())

    def isField(self):
        return False

    def isMethod(self):
        return False

    def __eq__(self, other):
        if not compareStringSets(self.modifiers, other.modifiers) or not len(self.annotations) == len(other.annotations): #TODO annotations ?
            return False

        return True

    def differences(self, other, ignores):
        ret = []


        if ComparisonIgnores.ANOT_MOD_MODIFIERS not in ignores:
            if not compareStringSets(self.modifiers, other.modifiers):
                ret.append(NOT_SAME_MODIFIERS)

        if ComparisonIgnores.ANOT_MOD_ANNOTATIONS not in ignores:
            if not not len(self.annotations) != len(other.annotations):
                ret.append(NOT_SAME_ANNOTATIONS)
                #TODO annotations ?

        return ret

    def getDisplayName(self):
        return self.__repr__()



class SmaliWithLines(SmaliAnnotableModifiable):
    def __init__(self, name, modifiers):
        SmaliAnnotableModifiable.__init__(self)
        self.name = name
        self.lines = list()
        self.addModifiersFromList(modifiers)

    def addLine(self, line):
        self.lines.append(line)

    def __eq__(self, other):
        if self.name != other.name or not self.areSourceCodeSimilars(other):
            return False

        return SmaliAnnotableModifiable.__eq__(self, other)

    def differences(self, other, ignores):
        ret = []

        if ComparisonIgnores.WITHLINES_NAME not in ignores:
            if self.name != other.name:
                ret.append(NOT_SAME_NAME)

        if ComparisonIgnores.WITHLINES_SOURCECODE not in ignores:
            if not self.areSourceCodeSimilars(other):
                ret.append(NOT_SAME_SOURCECODE_LINES)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    @staticmethod
    def cleanLines(lines):
        slines = list()
        for line in lines:
            if SmaliWithLines.keepThisLine(line):
                slines.append(line)
        return slines

    def getCleanLines(self):
        return SmaliWithLines.cleanLines(self.lines)

    def areSourceCodeSimilars(self, other):
        slines = self.getCleanLines()
        olines = other.getCleanLines()
        return compareListsSameposition(slines, olines)

    @staticmethod
    def keepThisLine(line):
        lline = line.strip()
        return len(lline) > 0 and lline[0] != '.'

class SmaliField(SmaliAnnotableModifiable):
    def __init__(self, name, type, modifiers, init):
        super(SmaliField, self).__init__()
        self.name = name
        self.type = type
        self.init = init
        self.addModifiersFromList(modifiers)

    def __eq__(self, other):
        if self.name == other.name and self.type == other.type and self.init == other.init:
            return SmaliAnnotableModifiable.__eq__(self, other)

        return False

    def differences(self, other, ignores):
        ret = []

        if ComparisonIgnores.FIELD_NAME not in ignores:
            if self.name != other.name:
                ret.append(NOT_SAME_NAME)

        if ComparisonIgnores.FIELD_TYPE not in ignores:
            if self.type != other.type:
                ret.append(NOT_SAME_TYPE)

        if ComparisonIgnores.FIELD_INIT not in ignores:
            if self.init != other.init:
                ret.append(NOT_SAME_INIT_VALUE)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    def isField(self):
        return True


class SmaliMethod(SmaliWithLines):
    def __init__(self, name, params, ret, modifiers):
        SmaliWithLines.__init__(self, name, modifiers)
        self.params = params
        self.ret = ret

    def __eq__(self, other):
        if self.ret != other.ret or not compareListsSameposition(self.params, other.params):
            return False

        return SmaliWithLines.__eq__(self, other)

    def getLightParams(self):
        ret = []

        for p in self.params:
            ret.append(p[0:1])

        return ret

    def differences(self, other, ignores):
        ret = []

        if ComparisonIgnores.METHOD_RETURN not in ignores:
            if self.ret != other.ret:
                ret.append(NOT_SAME_RETURN_TYPE)

        if ComparisonIgnores.METHOD_PARAMS not in ignores:
            if(not compareListsSameposition(self.params, other.params)):
                ret.append(NOT_SAME_PARAMETERS)

        ret.extend(SmaliWithLines.differences(self, other, ignores))
        return ret

    def isMethod(self):
        return True


class SmaliAnnotation(SmaliWithLines):
    pass




















class SmaliClass(SmaliAnnotableModifiable):
    def __init__(self):
        super(SmaliClass, self).__init__()
        self.name = None
        self.zuper = None
        self.source = None
        self.implements = set()

        self.methods = []
        self.fields = []

    @staticmethod
    def getDisplayName(clazzname):
        mt = classnamepattern.match(clazzname)

        if mt is not None:
            return clazzname[1:-1].strip().replace('/', '.')
        else:
            return clazzname

    def getBaseName(self):
        mt = classnamepattern.match(self.name)

        if mt is None:
            return self.name[1:-1]
        else:
            return mt.group(1)

    def addMethod(self, m):
        self.methods.append(m)

    def addField(self, f):
        self.fields.append(f)

    def setName(self, name):
        self.name = name

    def setSuper(self, zuper):
        self.zuper = zuper

    def addImplementedInterface(self, ifce):
        self.implements.add(ifce)

    def __eq__(self, other):
        if self.name != other.name or self.zuper != other.zuper or \
                        not compareListsBoolean(self.implements, other.implements) or \
                        not compareListsBoolean(self.methods, other.methods) or \
                        not compareListsBoolean(self.fields, other.fields) or \
                        not compareListsBoolean(other.implements, self.implements) or \
                        not compareListsBoolean(other.methods, self.methods) or \
                        not compareListsBoolean(other.fields, self.fields):
            return False

        return SmaliAnnotableModifiable.__eq__(self, other)

    def differences(self, other, ignores):
        fret = []

        if ComparisonIgnores.CLASS_NAME not in ignores:
            if self.name != other.name:
                fret.append([self, other, NOT_SAME_NAME])

        if ComparisonIgnores.CLASS_SUPER not in ignores:
            if self.zuper != other.zuper:
                fret.append([self, other, NOT_SAME_PARENT])

        if ComparisonIgnores.CLASS_IMPLEMENTS not in ignores:
            ret = bidirectCompareLists(self.implements, other.implements)
            if len(ret) > 0:
                fret.append([self, other, NOT_SAME_INTERFACES, ret])

        if ComparisonIgnores.CLASS_METHODS not in ignores:
            ret = self.methodsComparison(other, ignores)

            for diff in ret[1]:
                fret.append(diff)

        if ComparisonIgnores.CLASS_FIELDS not in ignores:
            ret = self.fieldsComparison(other, ignores)

            for diff in ret[1]:
                fret.append(diff)

        return fret

    def isRevisionOf(self, other):         # No change in anything else than code !
        df = self.differences(other, [])
        return len(df) == 1 and df[0] == NOT_SAME_SOURCECODE_LINES

    def setSource(self, param):
        self.source = param

    def methodsComparison(self, other, ignores):
        mself = list(self.methods)
        mother = list(other.methods)
        mttemp = list()

        sames = list()
        diffs = list()

        while len(mself) > 0:
            meth = mself.pop()

            found = False

            for m in mother:
                if meth == m:
                    found = True
                    sames.append([meth, m])
                    mother.remove(m)
                    break

            if not found:
                mttemp.append(meth)

        mself = mttemp


        while len(mself) > 0:
            meth = mself.pop()

            op = None

            for m in mother:
                diff = meth.differences(m, ignores)

                if len(diff) == 1:
                    if diff[0] == NOT_SAME_SOURCECODE_LINES:
                        op = [m, ChangesTypes.REVISED_METHOD]
                    elif diff[0] == NOT_SAME_NAME:
                        op = [m, ChangesTypes.REFACTORED_METHOD]
                if op is None and meth.name == m.name:
                    op = [m, ChangesTypes.SAME_NAME]

                if op is not None:
                    diffs.append([meth, op[0], op[1]])
                    mother.remove(m)
                    break

            if op is None:
                diffs.append([meth, None, ChangesTypes.NOT_FOUND])

        while len(mother) > 0:
            meth = mother.pop()
            diffs.append([None, meth, ChangesTypes.NOT_FOUND])

        return sames, diffs

    def fieldsComparison(self, other, ignores):
        fself = list(self.fields)
        fother = list(other.fields)
        mttemp = list()

        sames = list()
        diffs = list()

        while len(fself) > 0:
            field = fself.pop()

            found = False

            for f in fother:
                if field == f:
                    found = True
                    sames.append([field, f])
                    fother.remove(f)
                    break

            if not found:
                mttemp.append(field)

        fself = mttemp

        while len(fself) > 0:
            field = fself.pop()

            found = False
            for f in fother:
                if len(field.differences(f, ComparisonIgnores.FIELD_INIT)) == 0 or f.name == field.name:
                    diffs.append([field, f, ChangesTypes.FIELD_CHANGED, field.differences(f, [])])
                    found = True
                    fother.remove(f)
                    break

            if not found:
                whereIsUsed = self.whereIsFieldUsed(field)
                f = self.tryToDetectFieldRenaming(field, whereIsUsed, other, fother)

                if f is not None:
                    diffs.append([field, f, ChangesTypes.FIELD_CHANGED, field.differences(f, [])])
                    fother.remove(f)
                else:
                    diffs.append([field, None, ChangesTypes.NOT_FOUND])

        while len(fother) > 0:
            field = fother.pop()
            diffs.append([None, field, ChangesTypes.NOT_FOUND])

        return sames, diffs

    def whereIsFieldUsed(self, field):
        ret = []

        fieldCall = "%s->%s:%s"%(self.name.strip(), field.name.strip(), field.type.strip())
        for m in self.methods:
            lnr = 0

            for lc in m.getCleanLines():
                if fieldCall in lc:
                    ret.append([m, lnr])
                lnr+=1

        return ret

    def tryToDetectFieldRenaming(self, field, whereIsUsed, newClass, nfields):
        fieldCall = "%s->%s:%s"%(self.name.strip(), field.name.strip(), field.type.strip())

        for usage in whereIsUsed:
            usageline = usage[1]
            simeth = newClass.findSimilarMethod(usage[0])

            if simeth is not None:
                line1 = usage[0].getCleanLines()[usageline]

                line2content = simeth.getCleanLines()

                if len(line2content) > usageline:
                    before = line1[0:line1.index(fieldCall)]
                    after = line1[len(before) + len(fieldCall):]

                    line2 = simeth.getCleanLines()[usageline]
                    newCandidate = line2.replace(before, '').replace(after, '')

                    for f in nfields:
                        if SmaliClass.matchFieldAndFieldCall(f, newCandidate):
                            return f

        return None

    def findSimilarMethod(self, method):
        for m in self.methods:
            if len(method.differences(m, [ ComparisonIgnores.WITHLINES_SOURCECODE ])) == 0:
                return m

        return None

    @staticmethod
    def matchFieldAndFieldCall(field, fieldcall):
        m = methodcallpattern.match(fieldcall)

        if m is not None:
            return field.name.strip() == m.group(2).strip() and field.type.strip() == m.group(3).strip()

    def findFieldWithMethodCall(self, fcall):
        if self.name == m.group(1):
            for f in self.fields:
                if SmaliClass.matchFieldAndFieldCall(f, fcall):
                    return f

        return None