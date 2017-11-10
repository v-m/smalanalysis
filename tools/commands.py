import subprocess
import re

PACKAGEMATCHER = re.compile(b'package: name=\'(.*?)\'')
dexfiles = re.compile('^classes[0-9]*.dex$')

def queryAaptForPackageName(apkpath):
    task = subprocess.Popen("aapt dump badging \"%s\""%apkpath, shell=True, stdout=subprocess.PIPE)

    it = PACKAGEMATCHER.findall(task.stdout.read())

    return None if len(it) < 1 else it[0]