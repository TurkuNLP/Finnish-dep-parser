#!/bin/bash
# Sentence splitting, tokenization, and conversion into the conll09 format

source init.sh

cat | opennlp SentenceDetector model/fi-sent.bin | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py
