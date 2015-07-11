#!/bin/bash

# 
export MAX_SEN_LEN=100  #sentences longer than this will be chopped and parsed chunked
export SEN_CHUNK=33 #length of the chunk into which the sentences will be chopped (the actual chunk size will differ a bit, depending where a suitable place can be found to cut the chunks)

#Inits the parsing pipeline (exports variable names, modifies path, makes TMPDIR)

export PYTHON=python
THIS=`pwd` #Where am I?
SCRIPT=`dirname $0` #where is this script?
cd $SCRIPT

export PATH=$PATH:$THIS/LIBS/apache-opennlp-1.5.3/bin/:$THIS/LIBS

## Uncomment for real temp directory, ie if you plan to run several instances on top of each other
#export TMPDIR=`mktemp -d --tmpdir=.` || exit #Get me a temporary directory for intermediate files or die
export TMPDIR=tmp_data ; mkdir -p $TMPDIR #fixed tmpdir, comment out if you uncomment the line above

