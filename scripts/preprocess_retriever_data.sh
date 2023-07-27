#!/bin/bash

export PYTHONPATH=./
export QUERY_FILE="data/instruction/G1_query.json"
export INDEX_FILE="data/test_query_ids/G1_instruction_test_query_ids.json"
export DATASET_NAME="G1"
export OUTPUT_DIR="data/retrieval/G1"

# data_preprocess.py will process files and output to the specified directory
python preprocess/preprocess_retriever_data.py \
    --query_file $QUERY_FILE \
    --index_file $INDEX_FILE \
    --dataset_name $DATASET_NAME \
    --output_dir $OUTPUT_DIR
