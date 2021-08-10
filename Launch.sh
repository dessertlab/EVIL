#!/bin/bash

echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "   SSSSSSSSSSSSSSS hhhhhhh                                lllllll lllllll BBBBBBBBBBBBBBBBB                       ";
echo " SS:::::::::::::::Sh:::::h                                l:::::l l:::::l B::::::::::::::::B                      ";
echo "S:::::SSSSSS::::::Sh:::::h                                l:::::l l:::::l B::::::BBBBBB:::::B                     ";
echo "S:::::S     SSSSSSSh:::::h                                l:::::l l:::::l BB:::::B     B:::::B                    ";
echo "S:::::S             h::::h hhhhh           eeeeeeeeeeee    l::::l  l::::l   B::::B     B:::::B    eeeeeeeeeeee    ";
echo "S:::::S             h::::hh:::::hhh      ee::::::::::::ee  l::::l  l::::l   B::::B     B:::::B  ee::::::::::::ee  ";
echo " S::::SSSS          h::::::::::::::hh   e::::::eeeee:::::eel::::l  l::::l   B::::BBBBBB:::::B  e::::::eeeee:::::ee";
echo "  SS::::::SSSSS     h:::::::hhh::::::h e::::::e     e:::::el::::l  l::::l   B:::::::::::::BB  e::::::e     e:::::e";
echo "    SSS::::::::SS   h::::::h   h::::::he:::::::eeeee::::::el::::l  l::::l   B::::BBBBBB:::::B e:::::::eeeee::::::e";
echo "       SSSSSS::::S  h:::::h     h:::::he:::::::::::::::::e l::::l  l::::l   B::::B     B:::::Be:::::::::::::::::e ";
echo "            S:::::S h:::::h     h:::::he::::::eeeeeeeeeee  l::::l  l::::l   B::::B     B:::::Be::::::eeeeeeeeeee  ";
echo "            S:::::S h:::::h     h:::::he:::::::e           l::::l  l::::l   B::::B     B:::::Be:::::::e           ";
echo "SSSSSSS     S:::::S h:::::h     h:::::he::::::::e         l::::::ll::::::lBB:::::BBBBBB::::::Be::::::::e          ";
echo "S::::::SSSSSS:::::S h:::::h     h:::::h e::::::::eeeeeeee l::::::ll::::::lB:::::::::::::::::B  e::::::::eeeeeeee  ";
echo "S:::::::::::::::SS  h:::::h     h:::::h  ee:::::::::::::e l::::::ll::::::lB::::::::::::::::B    ee:::::::::::::e  ";
echo " SSSSSSSSSSSSSSS    hhhhhhh     hhhhhhh    eeeeeeeeeeeeee llllllllllllllllBBBBBBBBBBBBBBBBB       eeeeeeeeeeeeee  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
echo "                                                                                                                  ";
  

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
	        echo "Usage: ./Launch.sh machine_choice"
		echo "machine_choice: type 0 for local machine, 1 for HPC w/ SLURM, 2 for HPC w/ TORQUE."
		exit 0;
	fi
}

echo "Welcome to EVIL's Launcher!";
rm -rf $SRC_DIR/model/finetuned_model $SRC_DIR/model/__pycache__ >/dev/null 2>&1;
select_machine $1;
		echo_time "Processing the Shellcode_IA32 dataset...";
bash $SRC_DIR/utils/test_split.sh 1

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