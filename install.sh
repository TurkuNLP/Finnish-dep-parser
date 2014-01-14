#!/bin/bash

function runc {
    echo "**** CMD **** $*"
    $*
    if [ "$?" != "0" ]
	then
	echo "FAILED!"
	exit
    fi
    echo
}

function checkc {
    $* > /dev/null 2>&1
    if [ "$?" != "0" ]
	then
	echo "FAILED!"
	exit
    fi
    echo "      ...OK"
    echo
}

function echoc {
    echo "**** INFO **** $*"
}

echo "Checking pre-requisites"
echo "java"
checkc java -version
echo "python"
checkc python --version

runc mkdir -p LIBS
runc cd LIBS

echoc "Downloading Omorfi java implementation (morphological analyzer)"
runc wget http://sourceforge.net/projects/hfst/files/optimized-lookup/hfst-ol.jar/download -O hfst-ol.jar

echoc "Downloading the parser binary from http://mate-tools.googlecode.com/files/anna-3-1.jar"
runc wget http://mate-tools.googlecode.com/files/anna-3-1.jar

echoc "Downloading the POS tagger binary from http://hunpos.googlecode.com/files/hunpos-1.0-linux.tgz"
runc wget http://hunpos.googlecode.com/files/hunpos-1.0-linux.tgz
runc tar zxf hunpos-1.0-linux.tgz

echoc "Downloading Apache OpenNLP (sentence splitter and tokenizer)"
runc wget http://www.nic.funet.fi/pub/mirrors/apache.org//incubator/opennlp/apache-opennlp-1.5.2-incubating-bin.tar.gz
runc tar zxf apache-opennlp-1.5.2-incubating-bin.tar.gz

runc cd ..
echo "SUCCESS"
echo
echo "Now try"
echo "cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.txt"



