#!/bin/bash
#set -e

#Sets up variable names, paths, creates $TMPDIR
source init.sh

#1) remove old comment dictionary
if [ -f $TMPDIR/comments_parser.json ];
then
    rm -f $TMPDIR/comments_parser.json
fi


#2) remove comments, tag the input, and fill in lemmas
# MAX_SEN_LEN and SEN_CHUNK are defined in init.sh
cat | $PYTHON conv_u_09.py --output=09 | $PYTHON limit_sentence_len.py -N $MAX_SEN_LEN -C $SEN_CHUNK | $PYTHON store_comments.py -d $TMPDIR/comments_parser.json | ./tag.sh > $TMPDIR/input_tagged.conll09

if [[ $? -ne 0 ]]
then
    echo "Tagging of the input failed. Please check the error messages above for any help" 1>&2
    exit 1
fi

#3) parse

cat $TMPDIR/input_tagged.conll09 | ./parse.sh  > $TMPDIR/input_parsed.conll09

#4) add comments

cat $TMPDIR/input_parsed.conll09 | $PYTHON add_comments.py -d $TMPDIR/comments_parser.json | $PYTHON limit_sentence_len.py --reverse | $PYTHON conv_u_09.py --output=u

#5) delete the temporary directory

##Uncomment to wipe the temp directory when done
#rm -rf $TMPDIR
