#!/bin/bash

#Inits the parsing pipeline (exports variable names, modifies path, makes TMPDIR)

export PYTHON=python
THIS=`pwd` #Where am I?
SCRIPT=`dirname $0` #where is this script?
cd $SCRIPT

export PATH=$PATH:$THIS/LIBS/apache-opennlp-1.5.3/bin/:$THIS/LIBS

## Uncomment for real temp directory
#export TMPDIR=`mktemp -d --tmpdir=.` || exit #Get me a temporary directory for intermediate files or die
export TMPDIR=tmp_data ; mkdir -p $TMPDIR #fixed tmpdir, comment out if you uncomment the line above

