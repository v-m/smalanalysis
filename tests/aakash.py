'''
Unit tests writted by Aakashkumar Patel (aakpat).
Requires    python3.
'''

import unittest
import subprocess
import os
import shutil
import metrics
#from metrics import computeMetrics

class TestUM(unittest.TestCase):
    @staticmethod
    def computeMetrics(v1, v2, pkg):
        testfold = TestUM.getTestFolder()

        return metrics.computeMetrics('%s/%s'%(testfold, v1),
                               '%s/%s' % (testfold, v2),
                               pkg)

    @staticmethod
    def getTestFolder():
        return os.path.realpath(__file__)[:-1 * len(os.path.basename(__file__))]

    @staticmethod
    def prepare(v1):
        if not os.path.exists(v1):
            name = v1.replace('.smali', '.apk')
            subprocess.run(['java', '-jar', '../bin/baksmali-2.2.1.jar', 'disassemble', name, '-o', v1], stdout=subprocess.PIPE, cwd=TestUM.getTestFolder())

    @classmethod
    def tearDownClass(cls):
        for p in os.listdir(TestUM.getTestFolder()):
            fullfile = '%s/%s'%(TestUM.getTestFolder(), p)
            if p.endswith('.smali') and os.path.isdir(fullfile):
                shutil.rmtree(fullfile)

    def test_v1v2(self):
        pkg = 'com.example.aakash.versiona'
        v1 = 'Version1.smali'
        v2 = 'Version2.smali'

        TestUM.prepare(v1)
        TestUM.prepare(v2)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v1, v2, pkg)

        self.assertEqual(E, 1)
        self.assertEqual(R, 0)
        self.assertEqual(C, 0)
        self.assertEqual(CA, 0)
        self.assertEqual(CD, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(MA, 3)
        self.assertEqual(MD, 0)
        self.assertEqual(MC, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FD, 0)
        self.assertEqual(FC, 0)

    def test_v2v3(self):
        pkg = 'com.example.aakash.versiona'
        v2 = 'Version2.smali'
        v3 = 'Version3.smali'

        TestUM.prepare(v2)
        TestUM.prepare(v3)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v2, v3, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CD, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(MA, 1)
        self.assertEqual(MD, 1)
        self.assertEqual(MC, 2)
        self.assertEqual(FA, 0)
        self.assertEqual(FD, 0)
        self.assertEqual(FC, 0)

    def test_v3v4(self):
        pkg = 'com.example.aakash.versiona'
        v3 = 'Version3.smali'
        v4 = 'Version4.smali'

        TestUM.prepare(v3)
        TestUM.prepare(v4)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v3, v4, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 1)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 1)
        self.assertEqual(FA, 2)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_v4v5(self):
        pkg = 'com.example.aakash.versiona'
        v4 = 'Version4.smali'
        v5 = 'Version5.smali'

        TestUM.prepare(v4)
        TestUM.prepare(v5)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v4, v5, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 2)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 2)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 1)

    def test_v5v6(self):
        pkg = 'com.example.aakash.versiona'
        v5 = 'Version5.smali'
        v6 = 'Version6.smali'

        TestUM.prepare(v5)
        TestUM.prepare(v6)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v5, v6, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 3)
        self.assertEqual(MD, 1)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_v6v7(self):
        pkg = 'com.example.aakash.versiona'
        v6 = 'Version6.smali'
        v7 = 'Version7.smali'

        TestUM.prepare(v6)
        TestUM.prepare(v7)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v6, v7, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 6)
        self.assertEqual(MC, 3)
        self.assertEqual(MD, 1)
        self.assertEqual(FA, 6)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 1)

    def test_v7v8(self):
        pkg = 'com.example.aakash.versiona'
        v7 = 'Version7.smali'
        v8 = 'Version8.smali'

        TestUM.prepare(v7)
        TestUM.prepare(v8)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v7, v8, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 2)
        self.assertEqual(MC, 3)
        self.assertEqual(MD, 6)
        self.assertEqual(FA, 2)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 6)

    def test_v8v9(self):
        pkg = 'com.example.aakash.versiona'
        v8 = 'Version8.smali'
        v9 = 'Version9.smali'

        TestUM.prepare(v8)
        TestUM.prepare(v9)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(v8, v9, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 0)
        self.assertEqual(C, 1)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 2)
        self.assertEqual(MD, 2)
        self.assertEqual(FA, 5)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 3)

    # def test_v9v10(self):
    # 	pkg = 'com.example.aakash.versiona'
    # 	v9 = 'Version9.smali'
    # 	v10 = 'Version10.smali'

    #   TestUM.prepare(v9)
    #   TestUM.prepare(v10)

    # 	global Len_OldClass,len_newclass,E,R,C,CA,CD,CC,MA,MD,MC,FA,FD,FC
    # 	Len_OldClass,len_newclass,E,R,C,CA,CD,CC,MA,MD,MC,FA,FD,FC=computeMetrics(v9,v10,pkg)

    # 	self.assertEqual(E,1)
    # 	self.assertEqual(R,0)
    # 	self.assertEqual(C,0)
    # 	self.assertEqual(CA,0)
    # 	self.assertEqual(CC,1)
    # 	self.assertEqual(CD,0)
    # 	self.assertEqual(MA,0)
    # 	self.assertEqual(MC,1)
    # 	self.assertEqual(MD,2)
    # 	self.assertEqual(FA,5)
    # 	self.assertEqual(FC,0)
    # 	self.assertEqual(FD,3)

    def test_vavb(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        vb = 'Versionb.smali'

        TestUM.prepare(va)
        TestUM.prepare(vb)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, vb, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 1)
        self.assertEqual(MC, 0)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vbvc(self):
        pkg = 'com.example.aakash.versiona'
        vb = 'Versionb.smali'
        vc = 'Versionc.smali'

        TestUM.prepare(vb)
        TestUM.prepare(vc)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vb, vc, pkg)

        self.assertEqual(E, 0)
        self.assertEqual(R, 1)
        self.assertEqual(C, 0)
        self.assertEqual(CA, 0)
        self.assertEqual(CC, 1)
        self.assertEqual(CD, 0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vcvd(self):
        pkg = 'com.example.aakash.versiona'
        vc = 'Versionc.smali'
        vd = 'Versiond.smali'

        TestUM.prepare(vc)
        TestUM.prepare(vd)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vc, vd, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 1)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 1)
        self.assertEqual(FD, 0)

    def test_vave(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        ve = 'Versione.smali'

        TestUM.prepare(va)
        TestUM.prepare(ve)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, ve, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vevf(self):
        pkg = 'com.example.aakash.versiona'
        ve = 'Versione.smali'
        vf = 'Versionf.smali'

        TestUM.prepare(ve)
        TestUM.prepare(vf)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(ve, vf, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vfvg(self):
        pkg = 'com.example.aakash.versiona'
        vf = 'Versionf.smali'
        vg = 'Versiong.smali'

        TestUM.prepare(vf)
        TestUM.prepare(vg)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vf, vg, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 0)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 1)
        self.assertEqual(FD, 0)

    def test_vavh(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        vh = 'Versionh.smali'

        TestUM.prepare(va)
        TestUM.prepare(vh)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, vh, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vhvi(self):
        pkg = 'com.example.aakash.versiona'
        vh = 'Versionh.smali'
        vi = 'Versioni.smali'

        TestUM.prepare(vh)
        TestUM.prepare(vi)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vh, vi, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vavj(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        vj = 'Versionj.smali'

        TestUM.prepare(va)
        TestUM.prepare(vj)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, vj, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vjvk(self):
        pkg = 'com.example.aakash.versiona'
        vj = 'Versionj.smali'
        vk = 'Versionk.smali'

        TestUM.prepare(vj)
        TestUM.prepare(vk)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vj, vk, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vkvl(self):
        pkg = 'com.example.aakash.versiona'
        vk = 'Versionk.smali'
        vl = 'Versionl.smali'

        TestUM.prepare(vk)
        TestUM.prepare(vl)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vk, vl, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 0)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 1)
        self.assertEqual(FD, 0)

    def test_vavm(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        vm = 'Versionm.smali'

        TestUM.prepare(va)
        TestUM.prepare(vm)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, vm, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vmvn(self):
        pkg = 'com.example.aakash.versiona'
        vm = 'Versionm.smali'
        vn = 'Versionn.smali'

        TestUM.prepare(vm)
        TestUM.prepare(vn)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vm, vn, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 1)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)

    def test_vnvo(self):
        pkg = 'com.example.aakash.versiona'
        vn = 'Versionn.smali'
        vo = 'Versiono.smali'

        TestUM.prepare(vn)
        TestUM.prepare(vo)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(vn, vo, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 0)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 0)
        self.assertEqual(FC, 1)
        self.assertEqual(FD, 0)

    def test_vavp(self):
        pkg = 'com.example.aakash.versiona'
        va = 'Versiona.smali'
        vp = 'Versionp.smali'

        TestUM.prepare(va)
        TestUM.prepare(vp)

        global Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC
        Len_OldClass, len_newclass, E, R, C, CA, CD, CC, MA, MD, MC, FA, FD, FC = TestUM.computeMetrics(va, vp, pkg)

        # self.assertEqual(E,0)
        # self.assertEqual(R,0)
        # self.assertEqual(C,1)
        # self.assertEqual(CA,0)
        # self.assertEqual(CC,1)
        # self.assertEqual(CD,0)
        self.assertEqual(MA, 0)
        self.assertEqual(MC, 0)
        self.assertEqual(MD, 0)
        self.assertEqual(FA, 1)
        self.assertEqual(FC, 0)
        self.assertEqual(FD, 0)


if __name__ == '__main__':
    unittest.main()


