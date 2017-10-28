#!/bin/bash
# Morpho analyzis and POS tagging

# Run the input through hunpos and populate the LEMMA,POS,FEAT,PLEMMA,PPOS,PFEAT columns

source init.sh

cat > $TMPDIR/tagger_input.conll09
cat $TMPDIR/tagger_input.conll09 | cut -f 2 | sort | uniq | $PYTHON omorfi_pos.py > $TMPDIR/all_readings.sd
rm -rf $TMPDIR/morpho_conv_tmp
TMPDIR_ABS=$($PYTHON abspath.py $TMPDIR)
cd morpho-sd2ud
./run.sh $TMPDIR_ABS/morpho_conv_tmp $TMPDIR_ABS/all_readings.sd $TMPDIR_ABS/all_readings.ud
cd ..
cat $TMPDIR/tagger_input.conll09 | $PYTHON marmot-tag.py --marmot $THIS/LIBS/marmot.jar --tempdir $TMPDIR --ud --hardpos --mreadings $TMPDIR/all_readings.ud -m model/fin_model.marmot > $TMPDIR/input_tagged_1.conll09

if [[ $? -ne 0 ]]
then
    exit 1
fi

cat $TMPDIR/input_tagged_1.conll09 | $PYTHON conllUtil.py --swap LEMMA:=PLEMMA,POS:=PPOS,FEAT:=PFEAT

exit $?


