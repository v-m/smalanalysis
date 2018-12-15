import subprocess
import re

PACKAGE_MATCHER = re.compile(b'package: name=\'(.*?)\'')
DEX_FILES = re.compile('^classes[0-9]*.dex$')


def query_aapt_for_package_name(apkpath):
    task = subprocess.Popen("aapt dump badging \"%s\"" % apkpath, shell=True, stdout=subprocess.PIPE)

    it = PACKAGE_MATCHER.findall(task.stdout.read())

    return None if len(it) < 1 else it[0]
