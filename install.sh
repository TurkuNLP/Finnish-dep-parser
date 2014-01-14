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

function select_hunpos_binary {
    #Do we already have a working hunpos-tag in LIBS?
    echo "koira" | hunpos-tag ../model/hunpos.model > /dev/null 2>&1
    if (( $? == 0 ))
    then
	return 0
    fi
    #Does the downloaded version work?
    echo "koira" | hunpos-1.0-linux/hunpos-tag ../model/hunpos.model > /dev/null 2>&1
    if (( $? == 0 ))
    then
	#yes, symlink it
	ln -f -s hunpos-1.0-linux/hunpos-tag hunpos-tag
	return 0
    fi
    #Does the pre-compiled version work?
    echo "koira" | ../LIBS-LOCAL/hunpos/hunpos-tag ../model/hunpos.model > /dev/null 2>&1
    if (( $? == 0 ))
    then
	#yes, symlink it
	ln -f -s ../LIBS-LOCAL/hunpos/hunpos-tag hunpos-tag
	return 0
    fi
    #Does the older pre-compiled version work?
    echo "koira" | ../LIBS-LOCAL/hunpos/hunpos-tag-64bit-glibc-2.10 ../model/hunpos.model > /dev/null 2>&1
    if (( $? == 0 ))
    then
	#yes, symlink it
	ln -f -s ../LIBS-LOCAL/hunpos/hunpos-tag-64bit-glibc-2.10 hunpos-tag
	return 0
    fi    
    echo
    echo "Couldn't get HunPOS to work"
    echo
    echo "Try to compile it yourself by following the commands in LIBS-LOCAL/hunpos/compile-hunpos.sh"
    echo "If you can make the program hunpos-tag to run, copy or symlink it as LIBS/hunpos-tag"
    return 1
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

echoc "Downloading Apache OpenNLP (sentence splitter and tokenizer)"
runc wget http://mirror.netinch.com/pub/apache/opennlp/opennlp-1.5.3/apache-opennlp-1.5.3-bin.tar.gz
runc tar zxf apache-opennlp-1.5.3-bin.tar.gz

echoc "Downloading the POS tagger binary from http://hunpos.googlecode.com/files/hunpos-1.0-linux.tgz"
runc wget http://hunpos.googlecode.com/files/hunpos-1.0-linux.tgz
runc tar zxf hunpos-1.0-linux.tgz
runc select_hunpos_binary  #This checks which hunpos works (the downloaded binary, or the binary included here) and makes a symlink to LIBS/hunpos-tag

runc cd ..
echo "SUCCESS"
echo
echo "Now try"
echo "cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.txt"



