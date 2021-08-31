#!/bin/bash

echo " ________      _______ _      ";
echo "|  ____\ \    / /_   _| |     ";
echo "| |__   \ \  / /  | | | |     ";
echo "|  __|   \ \/ /   | | | |     ";
echo "| |____   \  /   _| |_| |____ ";
echo "|______|   \/   |_____|______|";

#SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SRC_DIR=$PWD
RES_DIR=$SRC_DIR"/seq2seq/results"
LOG_DIR=$SRC_DIR"/seq2seq/logs"
ARCHIVE=$SRC_DIR"/seq2seq/archive"
mkdir -p seq2seq
mkdir -p $RES_DIR
mkdir -p $LOG_DIR
mkdir -p $ARCHIVE
timestamp=$(date +%Y-%m-%d-%H-%M)
exec > >(tee -ia $LOG_DIR/log_$timestamp.txt  | tee -ia >(grep -e 'bleu\|exact\|Duration' >> $LOG_DIR/shortLog_$timestamp.txt))
exec 2>&1

function echo_time() {
	date +"%Y-%m-%d %H:%M:%S.%6N  $*"
}

function select_dataset() {
	file_py="xnmt_model_shell.py"; #modify this variable to change the model
	if [ $1 == 1 ]; then
		file_json="encoder.test.json";
		file_hyp="encoder.test.hyp";
		file_answer="answer_encoder.txt";
		dataset="encoder";
		testset="encoder-test";
		echo_time "You selected the encoder dataset";

	elif [ $1 == 2 ]; then
		file_json="decoder.test.json";
		file_hyp="decoder.test.hyp";
		file_answer="answer_decoder.txt";
		dataset="decoder";
		testset="decoder-test";
		echo_time "You selected the decoder dataset";
	else
		echo "ERROR: Invalid dataset";
	        echo "Usage: ./Seq2Seq_Launch.sh [DATASET] [PREPROCESSING]"
		echo "DATASET: type 1 for the Encoder Python dataset, 2 for the Decoder Assembly Dataset."
		exit 0;
	fi
}


function select_preprocessing() {
	preproccessing=2; #modify this variable to change the model
	if [ $1 -eq 1 ]; then
		preprocessing=1;
		echo_time "Preprocessing without Intent Parser (IP) selected";
	elif [ $1 -eq 2 ]; then
		preprocessing=2;
		echo_time "Preprocessing with Intent Parser (IP) selected";
	else
		echo "ERROR: Invalid preprocessing";
	        echo "Usage: ./Seq2Seq_Launch.sh [DATASET] [PREPROCESSING]"
		echo "PREPROCESSING: type 1 preprocessing without the Intent Parser, 2 for preprocessing with the Intent Parser"
		exit 0;
	fi
}


echo "Welcome to EVIL's Seq2Seq Launcher!";

select_dataset $1;
select_preprocessing $2;
echo_time "Processing the selected dataset...";
bash $SRC_DIR/utils/test_split.sh $1 $2

echo_time "Running $file_py";
python $file_py $dataset
echo_time "$file_py executed"

python $SRC_DIR/utils/preproc/seq2seq_output_to_code.py $RES_DIR/$file_hyp $SRC_DIR/processed_dataset/$testset.json.seq2seq $RES_DIR/$file_json $dataset_str
python $SRC_DIR/utils/eval/codegen_eval.py --strip_ref_metadata --input_ref $SRC_DIR/processed_dataset/$testset.json --input_hyp $RES_DIR/$file_json
cp $RES_DIR/$file_json $RES_DIR/$file_answer;
mv $RES_DIR $ARCHIVE/id-$timestamp
echo_time "Done!"
