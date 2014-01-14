#!/bin/bash

PYTHON=python
THIS=`pwd` #Where am I?
SCRIPT=`dirname $0` #where is this script?
cd $SCRIPT

PATH=$PATH:$THIS/LIBS/apache-opennlp-1.5.2-incubating/bin/

## Uncomment for real temp directory
## Also uncomment the last line to get it deleted
#TMPDIR=`mktemp -d --tmpdir=.` || exit #Get me a temporary directory for intermediate files or die
TMPDIR=tmp_data ; mkdir -p $TMPDIR #fixed tmpdir, comment out if you uncomment the line above

#1) sentence-split, tokenize, and convert to CoNLL'09 format

cat | opennlp SentenceDetector model/fi-sent.bin | opennlp TokenizerME model/fi-token.bin | $PYTHON conllUtil.py --txt_to_09 > $TMPDIR/input.conll09

#2) tag the input, and fill in lemmas

cat $TMPDIR/input.conll09 | $PYTHON hunpos-tag.py --hunpos LIBS/hunpos-1.0-linux/hunpos-tag --tempdir $TMPDIR -p model/hunpos.model | $PYTHON conllUtil.py --swap LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT > $TMPDIR/input_tagged.conll09

#3) parse

java -Xmx1000M -classpath LIBS/anna-3-1.jar is2.parser.Parser -model model/parser.model -test $TMPDIR/input_tagged.conll09 -out $TMPDIR/input_parsed_raw.conll09 1>&2

cat $TMPDIR/input_parsed_raw.conll09 | $PYTHON conllUtil.py --swap HEAD:=PHEAD,DEPREL:=PDEPREL > $TMPDIR/input_parsed.conll09

cat $TMPDIR/input_parsed.conll09


#5) delete the temporary directory

##Uncomment to wipe the temp directory when done
#rm -rf $TMPDIR