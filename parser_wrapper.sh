#!/bin/bash

#Sets up variable names, paths, creates $TMPDIR
source init.sh

#1) sentence-split, tokenize, and convert to CoNLL'09 format
./split_text.sh > $TMPDIR/input.conll09

#2) tag the input, and fill in lemmas

cat $TMPDIR/input.conll09 | ./tag.sh > $TMPDIR/input_tagged.conll09

#3) parse

cat $TMPDIR/input_tagged.conll09 | ./parse.sh  > $TMPDIR/input_parsed.conll09

cat $TMPDIR/input_parsed.conll09

#5) delete the temporary directory

##Uncomment to wipe the temp directory when done
#rm -rf $TMPDIR