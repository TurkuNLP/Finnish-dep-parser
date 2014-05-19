#!/bin/bash
# Morpho analyzis and POS tagging

# Run the input through hunpos and populate the LEMMA,POS,FEAT,PLEMMA,PPOS,PFEAT columns

source init.sh

$PYTHON hunpos-tag.py --hunpos hunpos-tag --tempdir $TMPDIR -p model/hunpos.model > $TMPDIR/input_tagged_1.conll09

if [[ $? -ne 0 ]]
then
    exit 1
fi

cat $TMPDIR/input_tagged_1.conll09 | $PYTHON conllUtil.py --swap LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT

exit $?


