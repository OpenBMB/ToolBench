import logging
import os
import json
import pandas as pd
from datetime import datetime
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer, models, InputExample, losses, LoggingHandler
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from api_evaluator import APIEvaluator
import argparse
import os

import os

# 命令行参数解析
parser = argparse.ArgumentParser()
parser.add_argument("--data_path", default=None, type=str, required=True,
                    help="The input data dir. Should contain the .tsv files for the task.")
parser.add_argument("--output_base_path", default=None, type=str, required=True,
                    help="The base path where the model output will be saved.")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[LoggingHandler()])
logger = logging.getLogger(__name__)

torch.manual_seed(42)
torch.cuda.manual_seed(42)

num_epochs = 5
train_batch_size = 32

data_path = args.data_path

output_path = args.output_base_path
os.makedirs(output_path, exist_ok=True)

model_save_path = os.path.join(output_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
os.makedirs(model_save_path, exist_ok=True)

tensorboard_name = 'name_desc'
logs_writer = SummaryWriter(os.path.join(output_path, 'tensorboard', tensorboard_name))


def log_callback_st(train_ix, global_step, training_steps, current_lr, loss_value):
    logs_writer.add_scalar('train_loss', loss_value, global_step)
    logs_writer.add_scalar('lr', current_lr[0], global_step)


# Model definition
word_embedding_model = models.Transformer('bert-base-uncased', max_seq_length=256)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

ir_train_queries = {}
ir_test_queries = {}
ir_corpus = {}
ir_relevant_docs = {}
train_samples = []

documents_df = pd.read_csv(os.path.join(data_path, 'corpus.tsv'), sep='\t')
for row in documents_df.itertuples():
    doc = json.loads(row.document_content)
    ir_corpus[row.docid] = (doc.get('category_name', '') or '') + ', ' + \
    (doc.get('tool_name', '') or '') + ', ' + \
    (doc.get('api_name', '') or '') + ', ' + \
    (doc.get('api_description', '') or '') + \
    ', required_params: ' + json.dumps(doc.get('required_parameters', '')) + \
    ', optional_params: ' + json.dumps(doc.get('optional_parameters', '')) + \
    ', return_schema: ' + json.dumps(doc.get('template_response', ''))

train_queries_df = pd.read_csv(os.path.join(data_path, 'train.query.txt'), sep='\t', names=['qid', 'query'])
for row in train_queries_df.itertuples():
    ir_train_queries[row.qid] = row.query
train_queries_df = pd.read_csv(os.path.join(data_path, 'test.query.txt'), sep='\t', names=['qid', 'query'])
for row in train_queries_df.itertuples():
    ir_test_queries[row.qid] = row.query

labels_df = pd.read_csv(os.path.join(data_path, 'qrels.train.tsv'), sep='\t', names=['qid', 'useless', 'docid', 'label'])
for row in labels_df.itertuples():
    sample = InputExample(texts=[ir_train_queries[row.qid], ir_corpus[row.docid]], label=row.label)
    train_samples.append(sample)
labels_df = pd.read_csv(os.path.join(data_path, 'qrels.test.tsv'), sep='\t', names=['qid', 'useless', 'docid', 'label'])
for row in labels_df.itertuples():
    ir_relevant_docs.setdefault(row.qid, set()).add(row.docid)

train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=train_batch_size, pin_memory=True)
train_loss = losses.MultipleNegativesRankingLoss(model)
ir_evaluator = APIEvaluator(ir_test_queries, ir_corpus, ir_relevant_docs)

# You may need to modify the .fit() method to ensure all data is moved to the correct device during parallel computations

model.fit(train_objectives=[(train_dataloader, train_loss)],
                evaluator=ir_evaluator,
                epochs=num_epochs,
                warmup_steps=500,
                optimizer_params={'lr': 2e-5},
                output_path=model_save_path
                )


