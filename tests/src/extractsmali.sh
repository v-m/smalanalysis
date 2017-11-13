# Generate smali files from a java ones
# Author: Vincenzo Musco (http://www.vmusco.com)
# Date: November 7, 2017

cpath=$(pwd)
cd $1
pwd
javac -source 1.7 -target 1.7 -Xlint:none $(find . -iname '*.java');
dx  --dex --output=classes.dex $(find . -iname '*.class');
rm $(find . -iname '*.class')
java -jar ~/Software/baksmali-2.2.1.jar disassemble classes.dex;
rm *.dex;
cp -r out/* .;
rm -r out;