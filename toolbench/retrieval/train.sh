#!/bin/bash

# Define parameters
query_file="path/to/your/query/file"
index_file="path/to/your/index/file"
dataset_name="your_dataset_name"

# Run split_dataset.py
python3 split_dataset.py $query_file $index_file $dataset_name

# split_dataset.py will generate two files: train.json and test.json
train_file="${dataset_name}_train.json"
test_file="${dataset_name}_test.json"

output_dir="path/to/your/output/directory"

# Run data_preprocess.py
python3 data_preprocess.py $train_file $test_file $output_dir

# data_preprocess.py will process files and output to the specified directory

output_base_path="path/to/your/output/base/path"
model_path="./bert-base-uncased" # or the path of your downloaded IR pretrained model

# Run train.py
python3 train.py --data_path $output_dir --output_base_path $output_base_path --model_path $model_path