#!/bin/bash

SRC_DIR=$PWD
cd $PWD
python $SRC_DIR/model/eval_prep.py

python $SRC_DIR/utils/preproc/seq2seq_output_to_code.py $SRC_DIR/model/finetuned_model/Shellcode_IA32/test_1.hyp $SRC_DIR/processed_dataset/assembly-test.json.seq2seq $SRC_DIR/model/eval/assembly_test_output.json

cp $SRC_DIR/processed_dataset/assembly-test.json $SRC_DIR/model/eval/assembly_test_gold.json
python $SRC_DIR/utils/eval/codegen_eval.py --strip_ref_metadata --input_ref $SRC_DIR/model/eval/assembly_test_gold.json --input_hyp $SRC_DIR/model/eval/assembly_test_output.json