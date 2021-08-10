#!/bin/bash
set -e

if [ $# -ne 1 ]; then
    echo "Usage: ./utils/test_split.sh [PRE-PROCESSING]"
    echo "[PRE-PROCESSING]: is the number associated with a pre-processing option"
    echo "Preprocessing Options:"
    echo "0 - used for raw corpus token counts"
    echo "1 - Preprocessing for the Python Encoder dataset"
    echo "2 - Preprocessing for the Asembly Decoder dataset"
    exit 1
fi;

SDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WDIR=$SDIR"/../"
DATASET=$WDIR"/datasets/"

#echo "sdir $SDIR"
#echo "wdir $WDIR"
rm -rf $WDIR/processed_dataset
mkdir $WDIR/processed_dataset

function echo_time() {
    date +"%Y-%m-%d %H:%M:%S.%6N  $*"
}

# Assumes running from
# home directory.

echo_time "You selected the Decoder dataset"
# Convert Assembly Dataset to JSON
echo_time "Converting and moving the dataset ..."
python text_to_json.py $DATASET/assembly/assembly-dev.in $DATASET/assembly/assembly-dev.out
python text_to_json.py $DATASET/assembly/assembly-train.in $DATASET/assembly/assembly-train.out
python text_to_json.py $DATASET/assembly/assembly-test.in $DATASET/assembly/assembly-test.out
mv $WDIR/assembly-*.json $WDIR/processed_dataset/

#double check this
echo_time "Exctracting raw data ..."
cd $WDIR/processed_dataset/
python $SDIR/preproc/our_extract_raw_data.py $1 # > raw_data.txt
# Preprocess Assembly Dataset
echo_time "Preprocessing ..."
python $SDIR/preproc/json_to_seq2seq.py assembly-train.json.seq2seq assembly-train.intent assembly-train.snippet
python $SDIR/preproc/json_to_seq2seq.py assembly-test.json.seq2seq assembly-test.intent assembly-test.snippet
python $SDIR/preproc/json_to_seq2seq.py assembly-dev.json.seq2seq assembly-dev.intent assembly-dev.snippet

    
cd $WDIR

echo "Done!"









