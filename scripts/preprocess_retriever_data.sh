#!/bin/bash

export PYTHONPATH=./
export QUERY_FILE="data/query/queryG1_demo.json"
export INDEX_FILE="data/retriever/G1_instruction_test_ids.json"
export DATASET_NAME="G1"
export OUTPUT_DIR="data/retriever/G1_demo"

# data_preprocess.py will process files and output to the specified directory
python data/preprocess_retriever_data.py \
    --query_file $QUERY_FILE \
    --index_file $INDEX_FILE \
    --dataset_name $DATASET_NAME \
    --output_dir $OUTPUT_DIR
