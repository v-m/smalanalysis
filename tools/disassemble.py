import shutil
import subprocess
import sys
import os
import zipfile
import re

def runSmali(apkpath, smalipath, overwrite=False):
    if os.path.exists(smalipath):
        if overwrite:
            os.rmdir(smalipath)
        else:
            return

    dexesfolder = []
    z = zipfile.ZipFile(apkpath)
    for file in [file for file in zipfile.ZipFile(apkpath).namelist() if re.match('^classes[0-9]*.dex$', file)]:
        fullsmalipath = '_'.join([smalipath, file])
        dexesfolder.append(fullsmalipath)

        if os.path.exists(fullsmalipath):
            os.rmdir(fullsmalipath)

        base = os.path.realpath(__file__)
        for i in range(2):
            base = base[:base.rindex('/')]

        task = subprocess.Popen('java -jar %s/bin/baksmali-2.2.1.jar disassemble "%s/%s" -o "%s"' % (base, apkpath, file, fullsmalipath), shell=True, stdout=subprocess.PIPE)
        task.wait()

    z.close()

    os.mkdir(smalipath)

    for dir in dexesfolder:
        for sdir in os.listdir(dir):
            shutil.move('/'.join([dir, sdir]), '/'.join([smalipath, sdir]))

        os.rmdir(dir)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        apkpath = sys.argv[1]
        smalifolder = sys.argv[2]
        overwrite = False if len(sys.argv) < 3 else True if sys.argv[3] == '1' else False

        runSmali(apkpath, smalifolder, overwrite)