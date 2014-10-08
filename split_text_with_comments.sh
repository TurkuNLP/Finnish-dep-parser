#!/bin/bash
set -o pipefail

# Sentence splitting, tokenization, and conversion into the conll09 format

source init.sh

cat | $PYTHON check_encoding.py | $PYTHON hash_comments.py > $TMPDIR/hashed_text.txt

cat $TMPDIR/hashed_text.txt | opennlp SentenceDetector model/fi-sent.bin | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py
