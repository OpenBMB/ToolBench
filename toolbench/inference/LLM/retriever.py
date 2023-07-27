import time
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import json
import re
from toolbench.utils import standardize, standardize_category, change_name, process_retrieval_ducoment


class ToolRetriever:
    def __init__(self, corpus_tsv_path = "", model_path=""):
        self.corpus_tsv_path = corpus_tsv_path
        self.model_path = model_path
        self.corpus, self.corpus2tool = self.build_retrieval_corpus()
        self.embedder = self.build_retrieval_embedder()
        self.corpus_embeddings = self.build_corpus_embeddings()
        
    def build_retrieval_corpus(self):
        print("Building corpus...")
        documents_df = pd.read_csv(self.corpus_tsv_path, sep='\t')
        corpus, corpus2tool = process_retrieval_ducoment(documents_df)
        corpus_ids = list(corpus.keys())
        corpus = [corpus[cid] for cid in corpus_ids]
        return corpus, corpus2tool

    def build_retrieval_embedder(self):
        print("Building embedder...")
        embedder = SentenceTransformer(self.model_path)
        return embedder
    
    def build_corpus_embeddings(self):
        print("Building corpus embeddings with embedder...")
        corpus_embeddings = self.embedder.encode(self.corpus, convert_to_tensor=True)
        return corpus_embeddings

    def retrieving(self, query, top_k=5, excluded_tools={}):
        print("Retrieving...")
        start = time.time()
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.corpus_embeddings, top_k=10*top_k, score_function=util.cos_sim)
        retrieved_tools = []
        for rank, hit in enumerate(hits[0]):
            category, tool_name, api_name = self.corpus2tool[self.corpus[hit['corpus_id']]].split('\t') 
            category = standardize_category(category)
            tool_name = standardize(tool_name) # standardizing
            api_name = change_name(standardize(api_name)) # standardizing
            if category in excluded_tools:
                if tool_name in excluded_tools[category]:
                    top_k += 1
                    continue
            tmp_dict = {
                "category": category,
                "tool_name": tool_name,
                "api_name": api_name
            }
            retrieved_tools.append(tmp_dict)
        return retrieved_tools