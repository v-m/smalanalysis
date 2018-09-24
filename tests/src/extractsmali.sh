# Generate smali files from a java ones
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 7, 2017

cpath=$(pwd)
cd $1
javac -source 1.7 -target 1.7 -Xlint:none $(find . -iname '*.java');
dx --dex --output=classes.dex $(find . -iname '*.class');
rm $(find . -iname '*.class')
java -jar ../../../bin/sa-baksmali-2.2.1.jar disassemble classes.dex;
rm *.dex;
cd out;
zip -r smali.zip *;
cd ..;
mv out/smali.zip .;
#cp -r out/* .;
rm -r out;