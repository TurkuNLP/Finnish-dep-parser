THISDIR=`pwd`
mkdir -p TMP
mkdir -p model_tr
mkdir -p log_tr
TRDATA=~/UD_PROJHOOK/UD-dev-branches/UD_Finnish/fi-ud-train.conllu

###### Prepare the all_readings.ud file #############
# cat $TRDATA | cut -f 2 | sort | uniq | python ../omorfi_pos.py > TMP/all_readings.sd
# cd ../morpho-sd2ud
# ./run.sh $THISDIR/TMP_CONV $THISDIR/TMP/all_readings.sd $THISDIR/TMP/all_readings.ud
# cd $THISDIR
######################################################

###### Make Marmot training data  ##############
# Drop empties and multiword tokens from the input

# cat $TRDATA | grep -Pv '^[0-9]+[.-]' | python ../marmot-tag.py --mr $THISDIR/TMP/all_readings.ud --ud -t > $THISDIR/TMP/fi-ud-train.mm
########################################################

function pr {
    param="$*"
    param_str="$(echo -- "$param" | tr ' ' '_' | tr '-' '_')"
    #echo "java -Xmx5G -cp LIBS/marmot.jar marmot.morph.cmd.Trainer -very-verbose true -train-file form-index=1,tag-index=2,morph-index=3,token-feature-index=4,fi-ud-fulltrain.mm -tag-morph true $param -model-file model_tr/fin_ud_model.$param_str.marmot"
    echo "java -Xmx5G -cp ../LIBS/marmot.jar marmot.morph.cmd.Trainer -very-verbose true -train-file form-index=1,tag-index=2,morph-index=3,token-feature-index=4,TMP/fi-ud-train.mm -tag-morph true $param -model-file model_tr/fin_ud_model_trainonly.$param_str.marmot > log_tr/fin_ud_model_trainonly.$param_str.log 2>&1"
    #echo "java -Xmx5G -cp LIBS/marmot.jar marmot.morph.cmd.Trainer -very-verbose true -train-file form-index=1,tag-index=2,morph-index=3,token-feature-index=4,fi-tdt-fulltrain.mm -tag-morph true $param -model-file model_tr/fin_tdt_model.$param_str.marmot"
}



for beam in 1 5 10
do
    for order in 2 3 4
    do
	for l2 in 0.0 0.01 0.05 0.1 0.2 0.4 0.8 1.6 3.2
	do
	    	pr "-order $order -beam-size $beam -quadratic-penalty $l2"
	done
    done
done

