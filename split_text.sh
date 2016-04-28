#!/bin/bash
set -o pipefail

# Sentence splitting, tokenization, and conversion into the conll09 format

source init.sh

if [[ "$1" == "--no-sent-split" ]]
then
    cat | $PYTHON check_encoding.py | grep -Pv '^\s*$' | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py
else 
    cat | $PYTHON check_encoding.py | opennlp SentenceDetector model/fi-sent.bin | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py
fi