#!/bin/bash

set -u
set -e
shopt -s failglob

INPUT=$2
OUTPUT=$3

WORKDIR=$1

# clean up possible previous versions
rm -rf $OUTPUT
rm -rf $WORKDIR
mkdir $WORKDIR

in=$INPUT
for f in [0-9][0-9][0-9]-*; do
    
    if [[ $f =~ .*~ ]]; then
	continue # skip emacs backups
    fi

    out=$WORKDIR/${f%.*}.txt

    echo >&2
    echo "Running $f $in $out ... " >&2
    ./$f $in $out

    echo -n "Checking $out ... " >&2
    inlines=`cat $in | wc -l`
    outlines=`cat $out | wc -l`
    if [ $inlines -ne $outlines ]; then
	# some scripts are expected to change the line count
	if [[ \
	    $f =~ .*add-AUX.* || \
	    $f =~ .*clean-extra.* \
	    ]]
	then
	    echo >&2
	    echo "Note: $in has $inlines lines, $out has $outlines" >&2
	else
	    echo >&2
	    echo "ERROR: $in has $inlines lines, $out has $outlines" >&2
	    exit 1
	fi
    fi
    echo "OK." >&2

    in=$out
done

echo -n "Copying $out to $OUTPUT ... " >&2
cp $out $OUTPUT
echo "done." >&2
