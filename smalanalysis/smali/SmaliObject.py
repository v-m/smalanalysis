# Smali Objects
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: 2017-09-15
import re

from smalanalysis.smali import ComparisonIgnores, ChangesTypes
import smalanalysis.smali.SmaliProject
import smalanalysis.smali.SmaliObject

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

RREFERENCE_PATTERN = re.compile('^const [vp][0-9]{1,2}, (0x[0-9a-f]{5,})$')

class_ref_pattern = re.compile('L(.*?);')
method_access_pattern = re.compile('L(.*?)->(.*?)\\)')
field_access_pattern = re.compile('L(.*?)->(.*?):')
jumps_pattern = re.compile(':[a-zA-Z0-9_\\-]+')
local_registers_pattern = re.compile('v[0-9]+')
param_registers_pattern = re.compile('p[0-9]+')

inner_anonymous_class_reference_matcher = re.compile("\$[0-9$]+;")

def compareStringSets(m1, m2):
    return len(m1 ^ m2) == 0

def compareListsSameposition(l1, l2, mappings=None):
    if len(l1) != len(l2):
        return False

    for i in range(len(l1)):
        if(type(l1[i]) != type(l2[i])):
            return False

        if(type(l1[i]) == str):
            if(mappings is not None and l1[i] in mappings):
                if mappings[l1[i]] != l2[i]:
                    return False
            else:
                if l1[i] != l2[i]:
                    return False
        else:
            if not l1[i].equals(l2[i], mappings):
                return False

    return True

def bidirectCompareLists(l1, l2, ignores = None, mappings = None):
    if ignores is None:
        ignores = []

    ret = []

    for m in compareLists(l1, l2, ignores, mappings):
        ret.append([SELF, m])

    for m in compareLists(l2, l1, ignores, mappings):
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

def compareLists(l1, l2, ignores = None, mappings = None):
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
                    if mappings is not None and compareWithMapping(it1, it2, mappings):
                        found = True
                        break
                    elif it1 == it2:
                        found = True
                        break
                elif len(it1.differences(it2, ignores, mappings)) == 0:
                    found = True
                    break

            if not found:
                missings.append(it1)
    else:
        return None

    return missings

def compareListsBoolean(l1, l2, mappings=None):
    return len(compareLists(l1, l2, mappings)) == 0
















class SmaliAnnotableModifiable(object):
    def __init__(self, parent):
        self.annotations = []
        self.modifiers = set()
        self.parent = parent

    def getParentProjectIfAny(self):
        trg = self.parent

        while trg is not None and not isinstance(trg, smalanalysis.smali.SmaliProject.SmaliProject):
            trg = trg.parent

        return trg

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

    #VINCE No need to compare mappings (yet?) at this stage
    # def __eq__(self, other):
    #
    #     #FIXIT Do not use __eq__ directly !
    #     assert(False)

    def equals(self, other, mappings=None):
        if not compareStringSets(self.modifiers, other.modifiers) or not len(self.annotations) == len(other.annotations): #TODO annotations ?
            return False

        return True

    def differences(self, other, ignores, mappings = None):
        ret = []


        if ComparisonIgnores.ANOT_MOD_MODIFIERS not in ignores:
            if not compareStringSets(self.modifiers, other.modifiers):
                ret.append(NOT_SAME_MODIFIERS)

        #if ComparisonIgnores.ANOT_MOD_ANNOTATIONS not in ignores:
        #    if not not len(self.annotations) != len(other.annotations):
        #        ret.append(NOT_SAME_ANNOTATIONS)
                #TODO annotations ?

        return ret

    def getDisplayName(self):
        return self.__repr__()



class SmaliWithLines(SmaliAnnotableModifiable):
    def __init__(self, name, modifiers, parent):
        SmaliAnnotableModifiable.__init__(self, parent)
        self.name = name.strip()
        self.lines = list()
        self.addModifiersFromList(modifiers)

    def getName(self):
        return self.name

    def addLine(self, line):
        self.lines.append(line)

    def getLines(self):
        return list(self.lines)

    # def __eq__(self, other):
    #     #FIXIT Do not use __eq__ directly !
    #     assert(False)

    def equals(self, other, mappings=None):
        if not compareWithMapping(self.name, other.name, mappings) or not self.areSourceCodeSimilars(other,mappings):
            return False

        return SmaliAnnotableModifiable.equals(self, other, mappings)

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.WITHLINES_NAME not in ignores:
            if not compareWithMapping(self.name, other.name, mappings):
                ret.append(NOT_SAME_NAME)

        if ComparisonIgnores.WITHLINES_SOURCECODE not in ignores:
            if not self.areSourceCodeSimilars(other,mappings):
                ret.append(NOT_SAME_SOURCECODE_LINES)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    def getIdentityLines(self):
        ret = list()

        for l in self.getCleanLines():
            l = class_ref_pattern.sub('L', l)
            l = method_access_pattern.sub('m', l)
            l = field_access_pattern.sub('f', l)
            l = jumps_pattern.sub('JMP', l)
            l = local_registers_pattern.sub('vr', l)
            l = param_registers_pattern.sub('pr', l)
            ret.append(l)

        return ret

    @staticmethod
    def cleanLines(lines):
        slines = list()
        for line in lines:
            if SmaliWithLines.keepThisLine(line):
                slines.append(line)
        return slines


    @staticmethod
    def cleanIdentityLines(lines):
        slines = list()
        for line in lines:
            if SmaliWithLines.keepThisLine(line):
                line = field_access_pattern.sub(r'\1->///FIELD///:', line)
                line = method_access_pattern.sub(r'\1->///METHOD///:', line)
                slines.append(line)
        return slines


    def getCleanIdentityLines(self):
        return SmaliWithLines.cleanIdentityLines(self.lines)

    def getCleanLines(self):
        return SmaliWithLines.cleanLines(self.lines)

    def moreThanNInstruction(self, n):
        return len(self.getCleanLines()) > n

    def areSourceCodeSimilars(self, other, considerRReferences=False, dropAnonymousClassContent=True, mappings=None):
        """
        Compare the smali lines
        :param other:
        :param considerRReferences:
        :param dropAnonymousClassContent: Do not compare the $X references in source lines.
                                            This option may induce some inacurracy but better match changes between
                                            two versions.
        :return:
        """
        slines = self.getCleanIdentityLines()
        olines = other.getCleanIdentityLines()

        if not considerRReferences:
            slines = SmaliMethod.clearRReferences(slines)
            olines = SmaliMethod.clearRReferences(olines)

        if dropAnonymousClassContent:
            slines = SmaliMethod.clearInnerClassesReferences(slines)
            olines = SmaliMethod.clearInnerClassesReferences(olines)

        if mappings is not None:
            slines = self.transposeWithNewReferences(slines, mappings)


        return compareListsSameposition(slines, olines)

    def transposeWithNewReferences(self, old, mappings):
        ret = []

        for line in old:
            thisline = line
            for m in mappings:
                thisline = thisline.replace(m.replace(";", ""), mappings[m].replace(";", ""))

            ret.append(thisline)

        return ret

    @staticmethod
    def clearRReferences(lines):
        ret = list()

        for line in lines:
            mtch = RREFERENCE_PATTERN.search(line)

            if mtch is not None:
                ret.append(line.replace(mtch.group(1), '<R_REF>'))
            else:
                ret.append(line)

        return ret

    @staticmethod
    def clearInnerClassesReferences(lines):
        ret = list()

        for line in lines:
            ret.append(inner_anonymous_class_reference_matcher.sub("$?", line))

        return ret

    @staticmethod
    def keepThisLine(line):
        lline = line.strip()
        return len(lline) > 0 and lline[0] != '.' and lline[0] != ':' and lline[0] != '#'

class SmaliField(SmaliAnnotableModifiable):
    def __init__(self, name, type, modifiers, init, clazz):
        super(SmaliField, self).__init__(clazz)
        self.name = name
        self.type = type
        self.init = init
        self.addModifiersFromList(modifiers)

    # def __eq__(self, other):
    #
    #     # FIXIT Do not use __eq__ directly !
    #     assert (False)

    def equals(self, other, mappings = None):
        if self.name == other.name and compareWithMapping(self.type, other.type, mappings) and self.init == other.init:
            return SmaliAnnotableModifiable.equals(self, other)

        return False

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.FIELD_NAME not in ignores:
            if not compareWithMapping(self.name, other.name, mappings):
                ret.append(NOT_SAME_NAME)

        if ComparisonIgnores.FIELD_TYPE not in ignores:
            if not compareWithMapping(self.type, other.type, mappings):
                ret.append(NOT_SAME_TYPE)

        if ComparisonIgnores.FIELD_INIT not in ignores:
            if self.init != other.init:
                ret.append(NOT_SAME_INIT_VALUE)

        ret.extend(SmaliAnnotableModifiable.differences(self, other, ignores))

        return ret

    def isField(self):
        return True


class SmaliMethod(SmaliWithLines):
    def __init__(self, name, params, ret, modifiers, clazz):
        SmaliWithLines.__init__(self, name, modifiers, clazz)
        self.params = params
        self.ret = ret

    # def __eq__(self, other):
    #     #FIXIT Do not use __eq__ directly !
    #     assert(False)
    #     return self.equals(other, None)

    def equals(self, other, mappings = None):
        if not isinstance(other, SmaliMethod) or not isinstance(self, SmaliMethod):
            return False

        if self.ret != other.ret or not compareListsSameposition(self.params, other.params, mappings):
            return False

        return SmaliWithLines.equals(self, other)

    def getLightParams(self):
        ret = []

        for p in self.params:
            ret.append(p[0:1])

        return ret

    def differences(self, other, ignores, mappings=None):
        ret = []

        if ComparisonIgnores.METHOD_RETURN not in ignores:
            if not compareWithMapping(self.ret, other.ret, mappings):
                ret.append(NOT_SAME_RETURN_TYPE)

        if ComparisonIgnores.METHOD_PARAMS not in ignores:
            if(not compareListsSameposition(self.params, other.params)):
                ret.append(NOT_SAME_PARAMETERS)

        ret.extend(SmaliWithLines.differences(self, other, ignores))
        return ret

    def isMethod(self):
        return True

    def getSignature(self):
        return ('%s(%s)%s'%(self.name, ''.join(self.params), self.ret)).strip()

    def getFullSignature(self):
        return '%s.%s'%('?' if self.parent is None else self.parent.getBaseName().replace('/', '.'), self.getSignature())


class SmaliAnnotation(SmaliWithLines):
    pass






def compareWithMapping(old, new, mappings):
    oldres = old

    if mappings is not None and "$" in old:
        oldres = "L{};".format(re.match("(\[*?)L(.*?)(\$(.*))?;", old).group(2))

    if mappings is not None and oldres in mappings:
        if(mappings[oldres] == new):
            return True

        oold = inner_anonymous_class_reference_matcher.sub("$?;", old)
        onew = inner_anonymous_class_reference_matcher.sub("$?;", new)

        for m in mappings:
            if m.replace(";", "") in oold:
                oold = oold.replace(m.replace(";", ""), mappings[m].replace(";", ""))
                break

        return oold == onew
    else:
        return old == new












class SmaliClass(SmaliAnnotableModifiable):
    def __init__(self, project):
        super(SmaliClass, self).__init__(project)
        self.name = None
        self.innername = None
        self.zuper = None
        self.source = None
        self.implements = set()
        self.innerclasses = {}
        self.methods = []
        self.fields = []

    def getName(self):
        return self.name

    def hasInnerClasses(self):
        return len(self.innerclasses) > 0

    def getAnonymousInnerClasses(self):
        return filter(lambda x: re.match(("^[0-9]+$"), x), self.innerclasses)

    def getNonAnonymousInnerClasses(self):
        return filter(lambda x: not re.match(("^[0-9]+$"), x), self.innerclasses)

    def determineParentClass(self):
        if self.parent is not None:
            if self.zuper is not None:
                return self.parent.searchClass(self.zuper)

        return None

    def determineParentClassHierarchy(self):
        ret = []

        parent = self.determineParentClass()

        while parent is not None:
            ret.append(parent)
            parent = parent.determineParentClass()

        return ret


    def determineParentClassHierarchyNames(self):
        ret = self.determineParentClassHierarchy()

        if len(ret) == 0:
            return [self.zuper]

        lastParent = ret[-1].zuper
        ret = list(map(lambda x: x.name, ret))
        ret.append(lastParent)
        return ret

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


    def getSuper(self):
        return self.zuper[1:-1]

    def addImplementedInterface(self, ifce):
        self.implements.add(ifce)

    #def __eq__(self, other):
    # FIXIT Do not use __eq__ directly !
    #    assert (False)

    def equals(self, other, mappings = None):
        if not compareWithMapping(self.name, other.name, mappings) or \
                not compareWithMapping(self.zuper, other.zuper, mappings) or \
                not compareListsBoolean(self.implements, other.implements, mappings) or \
                not compareListsBoolean(self.methods, other.methods, mappings) or \
                not compareListsBoolean(self.fields, other.fields, mappings) or \
                not compareListsBoolean(other.implements, self.implements, mappings) or \
                not compareListsBoolean(other.methods, self.methods, mappings) or \
                not compareListsBoolean(other.fields, self.fields, mappings):
            return False

        return SmaliAnnotableModifiable.equals(self, other)

    def differences(self, other, ignores, mappings=None):
        fret = []

        if ComparisonIgnores.CLASS_NAME not in ignores:
            if not compareWithMapping(self.name, other.name, mappings):
                fret.append([self, other, NOT_SAME_NAME])

        if ComparisonIgnores.CLASS_SUPER not in ignores:
            if not compareWithMapping(self.zuper, other.zuper, mappings):
                fret.append([self, other, NOT_SAME_PARENT])

        if ComparisonIgnores.CLASS_IMPLEMENTS not in ignores:
            ret = bidirectCompareLists(self.implements, other.implements, mappings)
            if len(ret) > 0:
                fret.append([self, other, NOT_SAME_INTERFACES, ret])

        if ComparisonIgnores.CLASS_METHODS not in ignores:
            ret = self.methodsComparison(other, ignores, mappings)

            for diff in ret[1]:
                fret.append(diff)

        if ComparisonIgnores.CLASS_FIELDS not in ignores:
            ret = self.fieldsComparison(other, ignores, fret, mappings)

            for diff in ret[1]:
                fret.append(diff)

        return fret

    def isRevisionOf(self, other):         # No change in anything else than code !
        df = self.differences(other, [])
        return len(df) == 1 and df[0] == NOT_SAME_SOURCECODE_LINES

    def setSource(self, param):
        self.source = param

    def methodsComparison(self, other, ignores, mappings=None):
        mself = list(self.methods)
        mother = list(other.methods)
        mttemp = list()

        sames = list()
        diffs = list()

        while len(mself) > 0:
            meth = mself.pop()

            found = False

            for m in mother:
                if meth.equals(m, mappings):
                    found = True
                    sames.append([meth, m])
                    mother.remove(m)
                    break

            if not found:
                mttemp.append(meth)

        mself = mttemp
        mttemp = list()

        while len(mself) > 0:
            meth = mself.pop()

            op = None
            found = False

            for m in mother:
                diff = meth.differences(m, ignores, mappings)

                if len(diff) == 1:
                    if diff[0] == NOT_SAME_SOURCECODE_LINES:
                        op = [m, ChangesTypes.REVISED_METHOD]
                    elif diff[0] == NOT_SAME_NAME and meth.moreThanNInstruction(1):
                        op = [m, ChangesTypes.RENAMED_METHOD]
                if op is None and meth.name == m.name:
                    # More than one change but they have the same source code,
                    # so we can suppose they are the same changed methods...
                    op = [m, ChangesTypes.SAME_NAME]

                if op is not None:
                    found = True
                    diffs.append([meth, op[0], op[1]])
                    mother.remove(m)
                    break

            if not found:
                mttemp.append(meth)

        mself = mttemp
        mttemp = list()

        while len(mself) > 0:
            meth = mself.pop()

            op = None

            for m in mother:
                if meth.areSourceCodeSimilars(m,mappings) and meth.moreThanNInstruction(1):
                    op = [m, ChangesTypes.RENAMED_METHOD]

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

    def fieldsComparison(self, other, ignores, ret, mappings=None):
        fself = list(self.fields)
        fother = list(other.fields)
        mttemp = list()

        sames = list()
        diffs = list()

        while len(fself) > 0:
            field = fself.pop()

            found = False

            for f in fother:
                if field.equals(f, mappings):
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
                if len(field.differences(f, ComparisonIgnores.FIELD_INIT)) == 0 or (f.name == field.name and 'static' not in (f.modifiers ^ field.modifiers)):
                    diffs.append([field, f, ChangesTypes.FIELD_CHANGED, field.differences(f, [])])
                    found = True
                    fother.remove(f)
                    break

            if not found:
                whereIsUsed = self.whereIsFieldUsed(field)
                f = self.tryToDetectFieldRenamingWithComputedSets(field, whereIsUsed, other, fother, ret)

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

            if m.getName() == '<init>' and len(m.params) == 0:
                # Lets skip similarities in the def cstr
                # as init value are put here for non static fields
                continue

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

    def tryToDetectFieldRenamingWithComputedSets(self, field, whereIsUsed, newClass, nfields, ret):
        fieldCall = "%s->%s:%s"%(self.name.strip(), field.name.strip(), field.type.strip())

        for usage in whereIsUsed:
            usageline = usage[1]

            simeth = None

            for ent in ret:

                if ent[0] is not None and ent[1] is not None:
                    if id(ent[0]) == id(usage[0]):
                        simeth = ent[1]
                        break
                    elif id(ent[1]) == id(usage[0]):
                        simeth = ent[0]
                        break

            if simeth is None:
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

    # def findFieldWithMethodCall(self, fcall):
    #     if self.name == m.group(1):
    #         for f in self.fields:
    #             if SmaliClass.matchFieldAndFieldCall(f, fcall):
    #                 return f

    #     return None

    def findMethod(self, name, parameters, ret):
        for m in self.methods:
            if m.name == name and ''.join(m.params) == parameters and m.ret == ret:
                return m

        return None