import argparse
import shutil
import subprocess
import os
import zipfile
import re

def zipdir(path, smalizip):
    for root, dirs, files in os.walk(path):
        for file in files:
            pth = os.path.join(root, file)
            pthinzip = '/'.join(pth.split('/')[1:])
            smalizip.write(pth, pthinzip)

def runSmali(apkpath, smalipath, overwrite=False, buildZip=False):
    if os.path.exists(smalipath):
        if overwrite:
            if os.path.isfile(smalipath):
                os.remove(smalipath)
            else:
                shutil.rmtree(smalipath)
        else:
            return

    dexesfolder = []
    z = zipfile.ZipFile(apkpath)
    for file in [file for file in zipfile.ZipFile(apkpath).namelist() if re.match('^classes[0-9]*.dex$', file)]:
        fullsmalipath = '_'.join([smalipath, file])
        dexesfolder.append(fullsmalipath)

        if os.path.exists(fullsmalipath):
            shutil.rmtree(fullsmalipath)

        base = os.path.realpath(__file__)
        for i in range(2):
            base = base[:base.rindex('/')]

        task = subprocess.Popen('java -jar %s/bin/baksmali-2.2.1.jar disassemble "%s/%s" -o "%s"' % (base, apkpath, file, fullsmalipath), shell=True, stdout=subprocess.PIPE)
        task.wait()

    z.close()

    if buildZip:
        with zipfile.ZipFile(smalipath, 'w') as smalizip:
            for dir in dexesfolder:
                zipdir(dir, smalizip)
                shutil.rmtree(dir)
    else:
        os.mkdir(smalipath)

        for dir in dexesfolder:
            for sdir in os.listdir(dir):
                shutil.move('/'.join([dir, sdir]), '/'.join([smalipath, sdir]))

            shutil.rmtree(dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract smali content.')
    parser.add_argument('apkpath', type=str,
                        help='The full path to the apk')
    parser.add_argument('output', type=str,
                         help='Where to output smali files', nargs='?', default = None )
    parser.add_argument('--overwrite', '-o', action='store_true',
                        help='Delete all previous exportation')
    parser.add_argument('--zip', '-z', action='store_true',
                        help='Build an archive instead of a folder')

    args = parser.parse_args()

    apkpath = args.apkpath
    output = args.output
    dozip = args.zip

    if output is None:
        output = '%s.smali'%apkpath

    overwrite = args.overwrite

    runSmali(apkpath, output, overwrite, dozip)
