#!/bin/bash

# Define parameters
query_file="./G1queryfile.json"
index_file="./G1indexfile.txt"
dataset_name="G1" # or G2, G3, G_combined

# Run split_dataset.py
python3 split_dataset.py $query_file $index_file $dataset_name

# split_dataset.py will generate two files: train.json and test.json
train_file="${dataset_name}_train.json"
test_file="${dataset_name}_test.json"

output_dir="./processed_dataset"

# Run data_preprocess.py
python3 data_preprocess.py $train_file $test_file $output_dir

# data_preprocess.py will process files and output to the specified directory

output_base_path="./saved_IR_model"
model_path="./bert-base-uncased" # or the path of your downloaded IR pretrained model

# Run train.py
python3 train.py --data_path $output_dir --output_base_path $output_base_path --model_path $model_path