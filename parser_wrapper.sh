#!/bin/bash
#set -e

#Sets up variable names, paths, creates $TMPDIR
source init.sh

#1) sentence-split, tokenize, and convert to CoNLL'09 format
./split_text.sh > $TMPDIR/input.conll09

if [[ $? -ne 0 ]]
then
    echo "Sentence splitting failed. Check the error messages above." 1>&2
    exit 1
fi

#2) tag and parse

cat $TMPDIR/input.conll09 | ./parse_conll.sh
