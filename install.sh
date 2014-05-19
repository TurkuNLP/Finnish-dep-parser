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
    echo "Selecting the HunPOS binary to run:"
    #Do we already have a working hunpos-tag in LIBS?
    echo "koira" | ./hunpos-tag ../model/hunpos.model > /dev/null 2>&1
    if (( $? == 0 ))
    then
	echo "...seems to have been done already, works."
	return 0
    fi

    #Try the distributed binaries until you find one which works
    for huntag in ../LIBS-LOCAL/hunpos/hunpos-tag-*
    do
	echo "Trying $huntag"
	echo "koira" | $huntag ../model/hunpos.model > /dev/null 2>&1
	if (( $? == 0 ))
	then
	#it works! symlink it
	    echo "Works. Selecting it"
	    ln -f -s $huntag ./hunpos-tag
	    return 0
	fi
    done
    echo
    echo "Couldn't get any of the HunPOS binaries in LIBS-LOCAL/hunpos to work"
    echo
    echo "Try to compile it yourself by following the commands in LIBS-LOCAL/hunpos/compile-hunpos.sh"
    echo "If you can make the program hunpos-tag to run, copy or symlink it as LIBS/hunpos-tag and"
    echo "kindly contribute the compiled binary to the project: ginter@cs.utu.fi   Thank you!"
    return 1
}

function select_hfstol {
    echo "Selecting the hfst-ol.jar to run:"
    #Do we already have a working one in in LIBS?
    T=$(echo "koiransa" | java -jar hfst-ol.jar ../model/morphology.finntreebank.hfstol 2>&1 | grep -c 'Ready for input')
    if (( "$T" == "1" ))
    then
	echo "...seems to have been done already, works."
	return 0
    fi

    #Try the distributed binaries until you find one which works
    for ol in ../LIBS-LOCAL/hfst-ol/hfst-ol.jar.*
    do
	echo "Trying $ol"
	T=$(echo "koiransa" | java -jar $ol ../model/morphology.finntreebank.hfstol 2>&1 | grep -c 'Ready for input')
	if (( "$T" == "1" ))
	then
	#it works! symlink it
	    echo "Works. Selecting it"
	    ln -f -s $ol ./hfst-ol.jar
	    return 0
	fi
    done
    echo
    echo "Couldn't get any of the hfst-ol.jar versions in LIBS-LOCAL/hfst-ol to work"
    echo
    echo "Try to compile it yourself from the sources on the HFST project pages"
    echo "If you can produce a working .jar file, copy or symlink it as LIBS/hfst-ol.jar and"
    echo "kindly contribute the compiled binary to the project: ginter@cs.utu.fi   Thank you!"
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

runc select_hunpos_binary  #This checks which hunpos works (the downloaded binary, or the binary included here) and makes a symlink to LIBS/hunpos-tag
runc select_hfstol

runc cd ..
echo
echo "Now try"
echo "cat data/wiki-test.txt | ./parser_wrapper.sh > wiki-test-parsed.txt"



