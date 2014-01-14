#!/bin/bash
# Morpho analyzis and POS tagging

# Run the input through hunpos and populate the LEMMA,POS,FEAT,PLEMMA,PPOS,PFEAT columns

source init.sh

$PYTHON hunpos-tag.py --hunpos LIBS/hunpos-1.0-linux/hunpos-tag --tempdir $TMPDIR -p model/hunpos.model | $PYTHON conllUtil.py --swap LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT
