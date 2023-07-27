import json
import pandas as pd
from sklearn.utils import shuffle
from tqdm import tqdm
import argparse
import os

# 创建参数解析器并添加参数
parser = argparse.ArgumentParser()
parser.add_argument('train_file', help='The name of the train file')
parser.add_argument('test_file', help='The name of the test file')
parser.add_argument('output_dir', help='The directory to output the split files')

# 解析命令行参数
args = parser.parse_args()

# Load the train data
with open(args.train_file, 'r') as f:
    train_data = json.load(f)

# Load the test data
with open(args.test_file, 'r') as f:
    test_data = json.load(f)

doc_id_map = {}  # Create a mapping from doc to doc_id
query_id_map = {}  # Create a mapping from query to query_id

documents = []
train_pairs = []
test_pairs = []

def process_data(data, pairs):
    for doc in tqdm(data):
        for api in doc['api_list']:
            document_content = api
            doc_id = doc_id_map.setdefault(json.dumps(document_content), len(doc_id_map) + 1)
            documents.append([doc_id, json.dumps(document_content)])
            queries = doc['query'] if isinstance(doc['query'], list) else [doc['query']]
            for query in queries:
                query_id = query_id_map.setdefault(query, len(query_id_map) + 1)
                pairs.append(([query_id, query], [query_id, 0, doc_id, 1]))

process_data(train_data, train_pairs)
process_data(test_data, test_pairs)
            
# Shuffle the data using the shuffle function
train_pairs = shuffle(train_pairs, random_state=42)
test_pairs = shuffle(test_pairs, random_state=42)

# Split the shuffled data into queries and labels
train_queries, train_labels = zip(*train_pairs)
test_queries, test_labels = zip(*test_pairs)

documents_df = pd.DataFrame(documents, columns=['docid', 'document_content'])
train_queries_df = pd.DataFrame(train_queries, columns=['qid', 'query_text'])
train_labels_df = pd.DataFrame(train_labels, columns=['qid', 'useless', 'docid', 'label'])
test_queries_df = pd.DataFrame(test_queries, columns=['qid', 'query_text'])
test_labels_df = pd.DataFrame(test_labels, columns=['qid', 'useless', 'docid', 'label'])

## make sure the output_dir exists
os.makedirs(args.output_dir, exist_ok=True)

# Save as .tsv and .txt files
documents_df.to_csv(args.output_dir + '/corpus.tsv', sep='\t', index=False)
train_queries_df.to_csv(args.output_dir + '/train.query.txt', sep='\t', index=False, header=False)
test_queries_df.to_csv(args.output_dir + '/test.query.txt', sep='\t', index=False, header=False)
train_labels_df.to_csv(args.output_dir + '/qrels.train.tsv', sep='\t', index=False, header=False)
test_labels_df.to_csv(args.output_dir + '/qrels.test.tsv', sep='\t', index=False, header=False)