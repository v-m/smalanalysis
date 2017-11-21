import argparse
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
    parser = argparse.ArgumentParser(description='Extract smali content.')
    parser.add_argument('apkpath', type=str,
                        help='The full path to the apk')
    parser.add_argument('smalifolder', type=str,
                        help='Folder where to output smali files')
    parser.add_argument('--overwrite', '-o', action='store_true',
                        help='Delete all previous exportation')

    args = parser.parse_args()

    apkpath = args.apkpath
    smalifolder = args.smalifolder
    overwrite = args.overwrite

    runSmali(apkpath, smalifolder, overwrite)
