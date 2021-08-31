#!/bin/bash

SRC_DIR=$PWD
cd $PWD

function echo_time() {
        date +"%Y-%m-%d %H:%M:%S.%6N  $*"
}

function select_dataset() {
	dataset=1; #modify this variable to change the model
	if [ $1 -eq 1 ]; then
		dataset=1;
		dataset_str="encoder";
		echo_time "Python Encoder dataset selected";
	elif [ $1 -eq 2 ]; then
		dataset=2;
		dataset_str="decoder";
		echo_time "Assembly Decoder dataset selected";
	else
		echo "ERROR: Wrong machine";
	        echo "Usage: ./Launch.sh [DEVICE] [DATASET] [PREPROCESSING]"
		echo "DATASET: type 1 for the Encoder Python dataset, 2 for the Decoder Assembly Dataset."
		exit 0;
	fi
}

select_dataset $1;

python $SRC_DIR/model/eval_prep.py $dataset_str

python $SRC_DIR/utils/preproc/seq2seq_output_to_code.py $SRC_DIR/model/finetuned_model/$dataset_str/test_1.hyp $SRC_DIR/processed_dataset/$dataset_str-test.json.seq2seq $SRC_DIR/model/eval/$dataset_str_test_output.json

cp $SRC_DIR/processed_dataset/$dataset_str-test.json $SRC_DIR/model/eval/$dataset_str_test_gold.json
python $SRC_DIR/utils/eval/codegen_eval.py --strip_ref_metadata --input_ref $SRC_DIR/model/eval/$dataset_str_test_gold.json --input_hyp $SRC_DIR/model/eval/$dataset_str_test_output.json
