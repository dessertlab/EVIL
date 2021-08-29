#!/bin/bash
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

lang=$dataset_str
lr=5e-5
batch_size=32 # or 64
beam_size=10
source_length=256
target_length=128
data_dir=../processed_dataset/ #change when changing dataset version
output_dir=finetuned_model/$lang
train_file=$data_dir/$dataset_str-train.json.seq2seq #change when changing dataset
dev_file=$data_dir/$dataset_str-dev.json.seq2seq #change when changing dataset
test_file=$data_dir/$dataset_str-test.json.seq2seq #change when changing dataset
eval_steps=320 
train_steps=2800 
pretrained_model=pretrained_models/pytorch_model.bin #CodeBERT: path to CodeBERT. Roberta: roberta-base

python run.py --do_train --do_eval --model_type roberta --model_name_or_path $pretrained_model --config_name roberta-base --tokenizer_name roberta-base --train_filename $train_file --dev_filename $dev_file --output_dir $output_dir --max_source_length $source_length --max_target_length $target_length --beam_size $beam_size --train_batch_size $batch_size --eval_batch_size $batch_size --learning_rate $lr --train_steps $train_steps --eval_steps $eval_steps --nl2code True

batch_size=128 
test_model=$output_dir/checkpoint-best-bleu/pytorch_model.bin #checkpoint for test
python run.py --do_test --model_type roberta --model_name_or_path roberta-base --config_name roberta-base --tokenizer_name roberta-base  --load_model_path $test_model --dev_filename $dev_file --test_filename $test_file --output_dir $output_dir --max_source_length $source_length --max_target_length $target_length --beam_size $beam_size --eval_batch_size $batch_size --nl2code True
