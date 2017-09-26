#!/bin/bash
# Computing Metrics - Generic Script
# Author: Vincenzo Musco (http://www.vmusco.com)
# Creation date: 2017-09-18

if ! type "aapt" > /dev/null; then
    echo "Please install aapt first..."
    exit;
fi

if ! type "java" > /dev/null; then
    echo "Please install java first..."
    exit;
fi

v1=${1%.apk}

package=$(aapt dump badging "$v1.apk" | awk '/package/{gsub("name=|'"'"'","");  print $2}')

echo "Package = $package";

if [ ! -d $v1".smali" ]; then
    echo "Disassembling $v1.apk";
	java -jar bin/baksmali-2.2.1.jar disassemble $v1".apk" -o $v1".smali"
else
    echo "$v1.apk already disassembled, skipping";
fi

shift

python including.py $v1".smali" $package $@
