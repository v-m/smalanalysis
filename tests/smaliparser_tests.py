import unittest
import metrics
import os
import subprocess

# Unit test for smali class generation
# Date: November 7, 2017
# Author: Vincenzo Musco (http://www.vmusco.com)
from smali.SmaliProject import SmaliProject


class SmaliParseTesting(unittest.TestCase):

    @staticmethod
    def getTestFolder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            subprocess.run(['bash', 'src/extractsmali.sh', 'src/%s'%v1], stdout=subprocess.PIPE, cwd=SmaliParseTesting.getTestFolder())

            sm = SmaliProject()
            sm.parseFolder('%s/src/%s'%(SmaliParseTesting.getTestFolder(), v1), None)
            return sm

    @staticmethod
    def findMethod(obj, name):
        for m in obj.methods:
            if m.name == name:
                return m

        return None


    @staticmethod
    def findField(obj, name):
        for f in obj.fields:
            if f.name == name:
                return f

        return None

    def test_simple_case(self):
        smali = SmaliParseTesting.prepare('v43')


        self.assertEqual(len(smali.classes), 1)
        self.assertEqual(smali.classes[0].getBaseName(), 'my/pkg/Foo')
        self.assertEqual(smali.classes[0].getSuper(), 'java/lang/Object')
        self.assertEqual(smali.classes[0].source, 'Foo.java')

        self.assertEqual(len(smali.classes[0].methods), 3)

        self.assertIsNotNone(SmaliParseTesting.findMethod(smali.classes[0], '<init>'))
        self.assertIsNotNone(SmaliParseTesting.findMethod(smali.classes[0], 'bar'))
        self.assertIsNotNone(SmaliParseTesting.findMethod(smali.classes[0], '<clinit>'))

        m = SmaliParseTesting.findMethod(smali.classes[0], '<init>')
        self.assertEqual(m.ret, 'V')
        self.assertEqual(len(m.params), 0)
        self.assertEqual(len(m.modifiers), 1)
        self.assertTrue('constructor' in m.modifiers)

        m = SmaliParseTesting.findMethod(smali.classes[0], 'bar')
        self.assertEqual(m.ret, 'I')
        self.assertEqual(len(m.params), 7)
        self.assertEqual(m.params[0], 'Ljava/lang/String;')
        self.assertEqual(m.params[1], 'I')
        self.assertEqual(m.params[2], 'C')
        self.assertEqual(m.params[3], 'Ljava/lang/Object;')
        self.assertEqual(m.params[4], 'Z')
        self.assertEqual(m.params[5], 'D')
        self.assertEqual(m.params[6], 'J')
        self.assertEqual(len(m.modifiers), 1)
        self.assertTrue('public' in m.modifiers)

        self.assertEqual(len(smali.classes[0].fields), 6)
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'KEY'))
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'VERSION'))
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'i'))
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'i_dup'))
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'i_dup2'))
        self.assertIsNotNone(SmaliParseTesting.findField(smali.classes[0], 'greeting'))

        f = SmaliParseTesting.findField(smali.classes[0], 'KEY')
        self.assertEqual(f.type, 'Ljava/lang/String;')
        self.assertEqual(len(f.modifiers), 3)
        self.assertTrue('private' in f.modifiers)
        self.assertTrue('static' in f.modifiers)
        self.assertTrue('final' in f.modifiers)
        self.assertTrue('final' in f.modifiers)
        self.assertEqual(f.init, '"ABC123"')

        f = SmaliParseTesting.findField(smali.classes[0], 'VERSION')
        self.assertEqual(f.type, 'I')
        self.assertEqual(len(f.modifiers), 3)
        self.assertTrue('private' in f.modifiers)
        self.assertTrue('static' in f.modifiers)
        self.assertTrue('final' in f.modifiers)
        self.assertEqual(f.init, '0x1')

        f = SmaliParseTesting.findField(smali.classes[0], 'i')
        self.assertEqual(f.type, 'I')
        self.assertEqual(len(f.modifiers), 1)
        self.assertTrue('private' in f.modifiers)
        self.assertIsNone(f.init)

        f = SmaliParseTesting.findField(smali.classes[0], 'i_dup')
        self.assertEqual(f.type, 'I')
        self.assertEqual(len(f.modifiers), 2)
        self.assertTrue('private' in f.modifiers)
        self.assertTrue('static' in f.modifiers)
        self.assertIsNone(f.init)

        f = SmaliParseTesting.findField(smali.classes[0], 'i_dup2')
        self.assertEqual(f.type, 'I')
        self.assertEqual(len(f.modifiers), 2)
        self.assertTrue('private' in f.modifiers)
        self.assertTrue('final' in f.modifiers)
        self.assertIsNone(f.init)

        f = SmaliParseTesting.findField(smali.classes[0], 'greeting')
        self.assertEqual(f.type, 'Ljava/lang/String;')
        self.assertEqual(len(f.modifiers), 1)
        self.assertTrue('private' in f.modifiers)
        self.assertIsNone(f.init)