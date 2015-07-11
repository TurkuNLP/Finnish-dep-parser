#!/bin/bash
set -o pipefail

source init.sh

#1) remove old comment dictionary
if [ -f $TMPDIR/comment_hashes.json ];
then
    rm -f $TMPDIR/comment_hashes.json
fi

#2) Sentence splitting, tokenization, and conversion into the conll09 format

cat | $PYTHON check_encoding.py | $PYTHON hash_comments.py -d $TMPDIR/comment_hashes.json > $TMPDIR/hashed_text.txt

if [[ "$1" == "--no-sent-split" ]]
then
    cat $TMPDIR/hashed_text.txt | grep -Pv '^\s*$' | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py -d $TMPDIR/comment_hashes.json
else
    cat $TMPDIR/hashed_text.txt | opennlp SentenceDetector model/fi-sent.bin | opennlp TokenizerME model/fi-token.bin | $PYTHON txt_to_09.py -d $TMPDIR/comment_hashes.json
fi
