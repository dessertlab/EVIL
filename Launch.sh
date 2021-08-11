#!/bin/bash


echo " ________      _______ _      ";
echo "|  ____\ \    / /_   _| |     ";
echo "| |__   \ \  / /  | | | |     ";
echo "|  __|   \ \/ /   | | | |     ";
echo "| |____   \  /   _| |_| |____ ";
echo "|______|   \/   |_____|______|";


#SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SRC_DIR=$PWD
timestamp=$(date +%Y-%m-%d-%H-%M)

function echo_time() {
	date +"%Y-%m-%d %H:%M:%S.%6N  $*"
}

function select_machine() {
	file="fine_tune.sh"; #modify this variable to change the model
	if [ $1 -eq 0 ]; then
		file="fine_tune.sh";    
		echo_time "Local machine selected";
	elif [ $1 -eq 1 ]; then
		file="fine_tune.slurm";    
		echo_time "SLURM machine selected";
	elif [ $1 -eq 2 ]; then
		file="fine_tune.pbs";    
		echo_time "TORQUE machine selected";   
	else 
		echo "ERROR: Wrong machine";
	        echo "Usage: ./Launch.sh [DEVICE] [DATASET] [PREPROCESSING]"
		echo "DEVICE: type 0 for local machine, 1 for HPC w/ SLURM, 2 for HPC w/ TORQUE."
		exit 0;
	fi
}



function select_dataset() {
	dataset=1; #modify this variable to change the model
	elif [ $2 -eq 1 ]; then
		dataset=1;
		echo_time "Python Encoder dataset selected";
	elif [ $2 -eq 2 ]; then
		dataset=2;
		echo_time "Assembly Deocder dataset selected";
	else
		echo "ERROR: Wrong machine";
	        echo "Usage: ./Launch.sh [DEVICE] [DATASET] [PREPROCESSING]"
		echo "DATASET: type 1 for the Encoder Python dataset, 2 for the Deocder Assembly Dataset."
		exit 0;
	fi
}


function select_preprocessing() {
	preproccessing=2; #modify this variable to change the model
	if [ $3 -eq 1 ]; then
		preprocessing=1;
		echo_time "Preprocessing without Intent Parser (IP) selected";
	elif [ $3 -eq 2 ]; then
		preprocessing=2;
		echo_time "Preprocessing with Intent Parser (IP) selected";
	else
		echo "ERROR: Wrong machine";
	        echo "Usage: ./Launch.sh [DEVICE] [DATASET] [PREPROCESSING]"
		echo "PREPROCESSING: type 1 preprocessing without the Intent Parser, 2 for preprocessing with the Intent Parser"
		exit 0;
	fi
}

echo "Welcome to EVIL's Launcher!";
rm -rf $SRC_DIR/model/finetuned_model $SRC_DIR/model/__pycache__ >/dev/null 2>&1;
echo "Checking if pretrained models are installed..."
python utils/model_prep.py
rm -rf $SRC_DIR/model/pretrained_models/codebert.zip
select_machine $1;


echo_time "Processing the selected dataset...";
bash $SRC_DIR/utils/test_split.sh $dataset $preprocessing

echo_time "Running $file...";
if [ $1 -eq 0 ]; then
	init_time=$(date '+%Y-%m-%d %H:%M:%S.%3N');
	cd $SRC_DIR/model
	bash $file    
	finish_time=$(date '+%Y-%m-%d %H:%M:%S.%3N');
	diff_time=$(date -d @$(( $(date -d "$finish_time" +%s) - $(date -d "$init_time" +%s) )) -u +'%H:%M:%S')
	echo "Duration of the experiment $i $j: " ${diff_time}     
	echo_time "finetuning completed!"
	cd $SRC_DIR
	bash $SRC_DIR/evaluate.sh
	exit 0;
elif [ $1 -eq 1 ]; then
	cd $SRC_DIR/model
	mkdir -p job_logs
	sbatch $file
	echo_time "Job submitted!"
	echo "Please run evaluate.sh from the ShellBe directory when the job is complete!"     
elif [ $1 -eq 2 ]; then
	cd $SRC_DIR/model
	mkdir -p job_logs
	qsub $file
	echo_time "Job submitted!"
	echo "Please run evaluate.sh from the ShellBe directory when the job is complete!"
	fi