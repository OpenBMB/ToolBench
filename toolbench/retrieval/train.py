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
from toolbench.utils import process_retrieval_ducoment

import os

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", default=None, type=str, required=True,
                    help="The input data dir. Should contain the .tsv files for the task.")
parser.add_argument("--model_name", default=None, type=str, required=True,
                    help="The base model name.")
parser.add_argument("--output_path", default=None, type=str, required=True,
                    help="The base path where the model output will be saved.")
parser.add_argument("--num_epochs", default=5, type=int, required=True,
                    help="Train epochs.")
parser.add_argument("--train_batch_size", default=32, type=int, required=True,
                    help="Train batch size.")
parser.add_argument("--learning_rate", default=2e-5, type=float, required=True,
                    help="Learning rate.")
parser.add_argument("--warmup_steps", default=500, type=float, required=True,
                    help="Warmup steps.")
parser.add_argument("--max_seq_length", default=256, type=int, required=True,
                    help="Max sequence length.")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[LoggingHandler()])
logger = logging.getLogger(__name__)

torch.manual_seed(42)
torch.cuda.manual_seed(42)

num_epochs = args.num_epochs
train_batch_size = args.train_batch_size
lr = args.learning_rate
warmup_steps = args.warmup_steps
data_path = args.data_path
output_path = args.output_path
os.makedirs(output_path, exist_ok=True)

model_save_path = os.path.join(output_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
os.makedirs(model_save_path, exist_ok=True)

tensorboard_name = 'name_desc'
logs_writer = SummaryWriter(os.path.join(output_path, 'tensorboard', tensorboard_name))


def log_callback_st(train_ix, global_step, training_steps, current_lr, loss_value):
    logs_writer.add_scalar('train_loss', loss_value, global_step)
    logs_writer.add_scalar('lr', current_lr[0], global_step)


# Model definition
word_embedding_model = models.Transformer(args.model_name, max_seq_length=args.max_seq_length)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

ir_train_queries = {}
ir_test_queries = {}
ir_relevant_docs = {}
train_samples = []

documents_df = pd.read_csv(os.path.join(data_path, 'corpus.tsv'), sep='\t')
ir_corpus, _ = process_retrieval_ducoment(documents_df)

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
                warmup_steps=warmup_steps,
                optimizer_params={'lr': lr},
                output_path=model_save_path
                )


