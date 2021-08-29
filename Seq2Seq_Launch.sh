#!/bin/bash

echo "                                                                                     ";
echo "                                                                                     ";
echo "EEEEEEEEEEEEEEEEEEEEEE                  PPPPPPPPPPPPPPPPP                            ";
echo "E::::::::::::::::::::E                  P::::::::::::::::P                           ";
echo "E::::::::::::::::::::E                  P::::::PPPPPP:::::P                          ";
echo "EE::::::EEEEEEEEE::::E                  PP:::::P     P:::::P                         ";
echo "  E:::::E       EEEEEEnnnn  nnnnnnnn      P::::P     P:::::Pyyyyyyy           yyyyyyy";
echo "  E:::::E             n:::nn::::::::nn    P::::P     P:::::P y:::::y         y:::::y ";
echo "  E::::::EEEEEEEEEE   n::::::::::::::nn   P::::PPPPPP:::::P   y:::::y       y:::::y  ";
echo "  E:::::::::::::::E   nn:::::::::::::::n  P:::::::::::::PP     y:::::y     y:::::y   ";
echo "  E:::::::::::::::E     n:::::nnnn:::::n  P::::PPPPPPPPP        y:::::y   y:::::y    ";
echo "  E::::::EEEEEEEEEE     n::::n    n::::n  P::::P                 y:::::y y:::::y     ";
echo "  E:::::E               n::::n    n::::n  P::::P                  y:::::y:::::y      ";
echo "  E:::::E       EEEEEE  n::::n    n::::n  P::::P                   y:::::::::y       ";
echo "EE::::::EEEEEEEE:::::E  n::::n    n::::nPP::::::PP                  y:::::::y        ";
echo "E::::::::::::::::::::E  n::::n    n::::nP::::::::P                   y:::::y         ";
echo "E::::::::::::::::::::E  n::::n    n::::nP::::::::P                  y:::::y          ";
echo "EEEEEEEEEEEEEEEEEEEEEE  nnnnnn    nnnnnnPPPPPPPPPP                 y:::::y           ";
echo "                                                                  y:::::y            ";
echo "                                                                 y:::::y             ";
echo "                                                                y:::::y              ";
echo "                                                               y:::::y               ";
echo "                                                              yyyyyyy                ";
echo "                                                                                     ";
echo "                                                                                     ";
  

#SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SRC_DIR=$PWD
RES_DIR=$SRC_DIR"/results"
LOG_DIR=$SRC_DIR"/logs"
ARCHIVE=$SRC_DIR"/archive"
timestamp=$(date +%Y-%m-%d-%H-%M)
exec > >(tee -ia $LOG_DIR/log_$timestamp.txt  | tee -ia >(grep -e 'bleu\|exact\|Duration' >> $LOG_DIR/shortLog_$timestamp.txt))
exec 2>&1

function echo_time() {
	date +"%Y-%m-%d %H:%M:%S.%6N  $*"
}

function select_dataset() {
	file_py="xnmt_model_shell.py"; #modify this variable to change the model
	if [ $1 -eq 1 ]; then
		file_json="annot.test.json";
		file_hyp="annot.test.hyp";
		file_answer="answer_annot.txt";
		dataset="annot";
		testset="conala-test";
		echo_time "You selected the annot dataset";
	elif [ $1 -eq 2 ]; then
		file_json="mined.test.json";
		file_hyp="mined.test.hyp";
		file_answer="answer_mined.txt";
		dataset="mined";
		testset="conala-test";
		echo_time "You selected mined dataset";
	elif [ $1 -eq 3 ]; then
		file_json="mined_prob50.test.json";
		file_hyp="mined_prob50.test.hyp";
		file_answer="answer_mined_prob50.txt";
		dataset="mined_prob50";
		testset="conala-test";
		echo_time "You selected mined_prob50 dataset";
	elif [ $1 -eq 4 ]; then
		file_json="mined_unique.test.json";
		file_hyp="mined_unique.test.hyp";
		file_answer="answer_mined_unique.txt";
		dataset="mined_unique";
		testset="conala-test";
		echo_time "You selected mined_unique dataset";
	elif [ $1 -eq 5 ]; then
		file_json="hs.test.json";
		file_hyp="hs.test.hyp";
		file_answer="answer_hs.txt";
		dataset="hs";
		testset="hs-test";
		echo_time "You selected the Heathstone dataset";
	elif [ $1 == 6 ]; then
		file_json="django.test.json";
		file_hyp="django.test.hyp";
		file_answer="answer_django.txt";
		dataset="django";
		testset="django-test";
		echo_time "You selected the django dataset";
	elif [ $1 == 7 ]; then
		file_json="assembly.test.json";
		file_hyp="assembly.test.hyp";
		file_answer="answer_assembly.txt";
		dataset="assembly";
		testset="assembly-test";
		echo_time "You selected the assembly dataset";
	elif [ $1 == 8 ]; then
		file_json="magic.test.json";
		file_hyp="magic.test.hyp";
		file_answer="answer_magic.txt";
		dataset="magic";
		testset="magic-test";
		echo_time "You selected the magic dataset";

	elif [ $1 == 9 ]; then
		file_json="encoder.test.json";
		file_hyp="encoder.test.hyp";
		file_answer="answer_encoder.txt";
		dataset="encoder";
		testset="encoder-test";
		echo_time "You selected the encoder dataset";

	elif [ $1 == 10 ]; then
		file_json="decoder.test.json";
		file_hyp="decoder.test.hyp";
		file_answer="answer_decoder.txt";
		dataset="decoder";
		testset="decoder-test";
		echo_time "You selected the decoder dataset";
	else
		echo "ERROR: Wrong model choice";
	        echo "Usage: ./Launch.sh dataset_choice"
		echo "dataset_choice: type 1 for annot, 2 for mined, 3 for mined_prob50, 4 for mined_unique, 5 for hearthstone, 6 for django, 7 for ShellcodeIA32, 8 for magic, 9 for Python Shell encoders, and 10 for Assembly Decoders."
		exit 0;
	fi
}
echo "Welcome to EnPy's Launcher!";

select_dataset $1;

#The outer preproc loop. 
for i in `seq 7 7`; do #Change based on preprocess options
	#bash $SRC_DIR/conala-baseline/test_split.sh $1 $i
	for j in `seq 0 0`; do #Change based on model options
                #Run the model using whatever you have defined for that number
		echo_time "Running $file_py with param $j";
		python $file_py $j $dataset
		echo_time "$file_py executed"
		python $SRC_DIR/conala-baseline/preproc/seq2seq_output_to_code.py $RES_DIR/$file_hyp $SRC_DIR/conala-corpus/$testset.json.seq2seq $RES_DIR/$file_json
		python $SRC_DIR/conala-baseline/eval/conala_eval.py --strip_ref_metadata --input_ref $SRC_DIR/conala-corpus/$testset.json --input_hyp $RES_DIR/$file_json
		cp $RES_DIR/$file_json $RES_DIR/$file_answer;        
		mv $RES_DIR $ARCHIVE/id-$timestamp-$i-$j
		#zip -r ~/bak_results/result_$i_$j_$(date '+%A_%W_%Y_%X').zip ~/NLP-Project/results
                #zip -r "bak_results/result_$i_$j_$(date '+%A_%W_%Y_%X').zip" results
		echo_time "Done!"
        done
done
