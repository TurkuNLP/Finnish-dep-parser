#!/bin/bash
# Morpho analyzis and POS tagging

# Run the input through hunpos and populate the LEMMA,POS,FEAT,PLEMMA,PPOS,PFEAT columns

source init.sh

$PYTHON marmot-tag.py --marmot $THIS/LIBS/marmot.jar --tempdir $TMPDIR -m model/fin_model.marmot > $TMPDIR/input_tagged_1.conll09

if [[ $? -ne 0 ]]
then
    exit 1
fi

cat $TMPDIR/input_tagged_1.conll09 | $PYTHON conllUtil.py --swap LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT

exit $?


