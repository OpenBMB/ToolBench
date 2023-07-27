import json
import argparse
import os
from tqdm import tqdm

# Create an argument parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument('query_file', help='The name of the query file')
parser.add_argument('index_file', help='The name of the index file')
parser.add_argument('dataset_name', help='The name of the output dataset')
# Parse command line arguments
args = parser.parse_args()

# Read the query file
with open(args.query_file, 'r') as f:
    query_data = json.load(f)

# Read the index file
with open(args.index_file, 'r') as f:
    test_index_data = json.load(f)

# Create a set of test set indices using set operations
test_index_set = set(map(int, test_index_data.keys()))

# Initialize the lists for the training set and test set
query_train = []
query_test = []

# Allocate the data from query_data to the training set and test set based on the index
for index, item in tqdm(enumerate(query_data)):
    if index in test_index_set:
        query_test.append(item)
    else:
        query_train.append(item)

# Create the names of the output files
output_file_base = args.dataset_name
train_file = output_file_base + '_train.json'
test_file = output_file_base + '_test.json'

# Write the training set and test set into their corresponding json files
with open(train_file, 'w') as f:
    json.dump(query_train, f)

with open(test_file, 'w') as f:
    json.dump(query_test, f)
