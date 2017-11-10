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
v2=${2%.apk}

package=$(aapt dump badging "$v1.apk" | awk '/package/{gsub("name=|'"'"'","");  print $2}')
package2=$(aapt dump badging "$v1.apk" | awk '/package/{gsub("name=|'"'"'","");  print $2}')

if [ $VERBOSE -eq 1 ]; then
    echo "Package v1 = $package";
    echo "Package v2 = $package2";
fi

if [ ! $package = $package2 ]; then
    echo "Packages should be the sames!";
    exit;
fi


if [ ! -d $v1".smali" ]; then
    if [ $VERBOSE -eq 1 ]; then
        echo "Disassembling $v1.apk";
    fi
    python tools/disassemble.py $v1".apk" $v1".smali"
else
    if [ $VERBOSE -eq 1 ]; then
        echo "$v1.apk already disassembled, skipping";
    fi
fi

if [ ! -d $v2".smali" ]; then
    if [ $VERBOSE -eq 1 ]; then
        echo "Disassembling $v2.apk";
    fi
    python tools/disassemble.py $v2".apk" $v2".smali"
else
    if [ $VERBOSE -eq 1 ]; then
        echo "$v2.apk already disassembled, skipping";
    fi
fi

if [ $VERBOSE -eq 1 ]; then
    echo "Running metrics..."
fi

shift
shift

python $TOOL.py $v1".smali" $v2".smali" $package $@
