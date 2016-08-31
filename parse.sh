#!/bin/bash
# Parse a tagged conll-09 file

source init.sh

java -Xmx2000M -classpath LIBS/anna-3.6.jar is2.parser.Parser -model model/parser.model -test /dev/stdin -out $TMPDIR/input_parsed_raw.conll09 1>&2
cat $TMPDIR/input_parsed_raw.conll09 | $PYTHON conllUtil.py --swap HEAD:=PHEAD,DEPREL:=PDEPREL

