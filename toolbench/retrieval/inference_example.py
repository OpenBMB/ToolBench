from sentence_transformers import SentenceTransformer, util
import json
import pandas as pd
from collections import defaultdict
import torch
from tqdm import tqdm
import argparse
import os

# 创建参数解析器并添加参数
parser = argparse.ArgumentParser()
parser.add_argument('model_path', type=str, required=True, help='Your trained model path')
parser.add_argument('dataset_path', help='The processed dataset files path')

# 解析命令行参数
args = parser.parse_args()

# Check if a GPU is available and if not, use a CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model_path = args.model_path

# Load the trained model
model = SentenceTransformer(model_path).to(device)

# Load test data
documents_df = pd.read_csv(os.path.join(args.dataset_path, 'corpus.tsv'), sep='\t')
test_queries_df = pd.read_csv(os.path.join(args.dataset_path, 'test.query.txt'), sep='\t', names=['qid', 'query_text'])
test_labels_df = pd.read_csv(os.path.join(args.dataset_path, 'qrels.test.tsv'), sep='\t', names=['qid', 'useless', 'docid', 'label'])

# Create mappings, get 'tool_name' and 'api_name' from the document_content
ir_corpus = {row.docid: (json.loads(row.document_content)['tool_name'], json.loads(row.document_content)['api_name']) for _, row in documents_df.iterrows()}
ir_test_queries = {row.qid: row.query_text for _, row in test_queries_df.iterrows()}

# Create query-doc mapping from the test set
ir_relevant_docs = defaultdict(list)
for _, row in test_labels_df.iterrows():
    ir_relevant_docs[row.qid].append(row.docid)

# Convert queries and documents to embeddings
test_query_embeddings = model.encode(list(ir_test_queries.values()), convert_to_tensor=True).to(device)
corpus_embeddings = model.encode(list(map(' '.join, ir_corpus.values())), convert_to_tensor=True).to(device)

# Compute cosine similarity between queries and documents
cos_scores = util.pytorch_cos_sim(test_query_embeddings, corpus_embeddings)

# Get the top_k most similar documents for each query
top_k = 5
top_results = {}
for query_index, (query_id, query) in enumerate(ir_test_queries.items()):
    relevant_docs_indices = cos_scores[query_index].topk(top_k).indices
    relevant_docs_scores = cos_scores[query_index].topk(top_k).values
    relevant_docs = [(list(ir_corpus.keys())[index], list(ir_corpus.values())[index]) for index in relevant_docs_indices]
    relevant_docs_with_scores = {str((doc_id, tool_name_api_name)): {'score': float(score)} for (doc_id, tool_name_api_name), score in zip(relevant_docs, relevant_docs_scores)}

    # Count the number of successful matches
    matches = len(set([doc_id for doc_id, _ in relevant_docs]) & set(ir_relevant_docs[query_id]))
    
    # Save query, original docs, top 5 docs with scores, and successful match count
    top_results[query] = {
        'original_docs': [' '.join(ir_corpus[doc_id]) for doc_id in ir_relevant_docs[query_id]],
        'top_docs': relevant_docs_with_scores,
        'successful_matches': matches
    }

# Save the results to a json file
with open('top5_results_with_matches.json', 'w') as f:
    json.dump(top_results, f, indent=4)