from sklearn.metrics import ndcg_score
import numpy as np
import logging
import os
from typing import List, Dict, Set
from tqdm import trange
from tqdm import tqdm
import torch
from multiprocessing import Pool
import heapq
from sentence_transformers.evaluation import SentenceEvaluator
from sentence_transformers.util import cos_sim
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 配置logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个FileHandler来保存日志到文件中
log_file = "log_file.txt"
if os.path.exists(log_file):
    os.remove(log_file)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# 创建一个StreamHandler来将日志输出到控制台
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# 设置日志输出格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将FileHandler和StreamHandler添加到logger中
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def compute_ndcg_for_query(query_tuple):
    _, query_id, top_hits, relevant_docs, corpus_ids, k = query_tuple
    query_relevant_docs = relevant_docs[query_id]

    # Build the ground truth relevance scores and the model's predicted scores
    true_relevance = np.zeros(len(corpus_ids))
    predicted_scores = np.zeros(len(corpus_ids))

    for hit in top_hits:
        predicted_scores[corpus_ids.index(hit["corpus_id"])] = hit["score"]
        if hit["corpus_id"] in query_relevant_docs:
            true_relevance[corpus_ids.index(hit["corpus_id"])] = 1

    return ndcg_score([true_relevance], [predicted_scores], k=k)


class APIEvaluator(SentenceEvaluator):
    """
    This class evaluates an Information Retrieval (IR) setting.
    Given a set of queries and a large corpus set. It will retrieve for each query the top-k most similar document.
    """

    def __init__(
        self,
        queries: Dict[str, str],  # qid => query
        corpus: Dict[str, str],  # cid => doc
        relevant_docs: Dict[str, Set[str]],  # qid => Set[cid]
        corpus_chunk_size: int = 5,
        show_progress_bar: bool = True,
        batch_size: int = 1,
        write_csv: bool = True,
        score_function=cos_sim,  # Score function, higher=more similar
    ):
        self.queries_id = list(queries.keys())
        self.queries = [queries[qid] for qid in self.queries_id]
        self.corpus_ids = list(corpus.keys())
        self.corpus = [corpus[cid] for cid in self.corpus_ids]
        self.relevant_docs = relevant_docs
        self.corpus_chunk_size = corpus_chunk_size
        self.show_progress_bar = show_progress_bar
        self.batch_size = batch_size
        self.write_csv = write_csv
        self.score_function = score_function

        self.csv_file: str = "Information-Retrieval_evaluation_results.csv"
        self.csv_headers = [
            "epoch",
            "steps",
            "Average NDCG@1",
            "Average NDCG@3",
            "Average NDCG@5",
        ]

        # for k in accuracy_at_k:
        #     self.csv_headers.append("Accuracy@{}".format(k))

    def __call__(
        self,
        model,
        output_path: str = None,
        epoch: int = -1,
        steps: int = -1,
        *args,
        **kwargs
    ) -> float:
        if epoch != -1:
            out_txt = (
                " after epoch {}:".format(epoch)
                if steps == -1
                else " in epoch {} after {} steps:".format(epoch, steps)
            )
        else:
            out_txt = ":"
        logger.info("Information Retrieval Evaluation" + out_txt)

        # scores = self.compute_metrices(model)
        avg_ndcg = self.compute_metrices(model)

        # Write results to disc
        if output_path is not None and self.write_csv:
            csv_path = os.path.join(output_path, self.csv_file)
            if not os.path.isfile(csv_path):
                fOut = open(csv_path, mode="w", encoding="utf-8")
                fOut.write(",".join(self.csv_headers))
                fOut.write("\n")
            else:
                fOut = open(csv_path, mode="a", encoding="utf-8")

            output_data = [epoch, steps]
            output_data.append(avg_ndcg)
            # for k in self.accuracy_at_k:
            #     output_data.append(scores[k])

            fOut.write(",".join(map(str, output_data)))
            fOut.write("\n")
            fOut.close()

        return min(avg_ndcg)

    def compute_metrices(self, model) -> Dict[int, float]:
        # Compute embedding for the queries
        query_embeddings = model.encode(
            self.queries,
            show_progress_bar=self.show_progress_bar,
            batch_size=self.batch_size,
            convert_to_tensor=True,
        )

        queries_result_list = [[] for _ in range(len(query_embeddings))]

        # Iterate over chunks of the corpus
        for corpus_start_idx in trange(
            0,
            len(self.corpus),
            self.corpus_chunk_size,
            desc="Corpus Chunks",
            disable=not self.show_progress_bar,
        ):
            corpus_end_idx = min(
                corpus_start_idx + self.corpus_chunk_size, len(self.corpus)
            )

            # Encode chunk of corpus
            sub_corpus_embeddings = model.encode(
                self.corpus[corpus_start_idx:corpus_end_idx],
                show_progress_bar=False,
                batch_size=self.batch_size,
                convert_to_tensor=True,
            )

            # Compute cosine similarites
            pair_scores = self.score_function(query_embeddings, sub_corpus_embeddings)

            # Convert scores to list
            pair_scores_list = pair_scores.cpu().tolist()

            for query_itr in range(len(query_embeddings)):
                for sub_corpus_id, score in enumerate(pair_scores_list[query_itr]):
                    corpus_id = self.corpus_ids[corpus_start_idx + sub_corpus_id]
                    queries_result_list[query_itr].append(
                        {"corpus_id": corpus_id, "score": score}
                    )

        for query_itr in range(len(queries_result_list)):
            for doc_itr in range(len(queries_result_list[query_itr])):
                score, corpus_id = (
                    queries_result_list[query_itr][doc_itr]["score"],
                    queries_result_list[query_itr][doc_itr]["corpus_id"],
                )
                queries_result_list[query_itr][doc_itr] = {
                    "corpus_id": corpus_id,
                    "score": score,
                }

        logger.info("Queries: {}".format(len(self.queries)))
        logger.info("Corpus: {}\n".format(len(self.corpus)))

        # Compute scores
        scores = self.compute_metrics(queries_result_list)

        # Output
        logger.info("Average NDCG@1: {:.2f}".format(scores[0] * 100))
        logger.info("Average NDCG@3: {:.2f}".format(scores[1] * 100))
        logger.info("Average NDCG@5: {:.2f}".format(scores[2] * 100))
        return scores

    def compute_metrics(self, queries_result_list):
        # Init score computation values
        ndcg_scores = []

        # Compute scores on results using a pool of workers
        k_list = [1, 3, 5]
        scores = []

        for k in k_list:
            # Build a list of tuples, each containing the data needed for one query
            query_tuples = []
            for query_itr in range(len(queries_result_list)):
                query_id = self.queries_id[query_itr]
                top_hits = sorted(
                    queries_result_list[query_itr],
                    key=lambda x: x["score"],
                    reverse=True,
                )
                query_tuples.append(
                    (
                        query_itr,
                        query_id,
                        top_hits,
                        self.relevant_docs,
                        self.corpus_ids,
                        k,
                    )
                )  # add 'k' to each tuple

            ndcg_scores.clear()  # clear the list for each 'k'

            with Pool() as p:
                max_ = len(query_tuples)
                with tqdm(total=max_) as pbar:
                    for i, _ in tqdm(
                        enumerate(p.imap(compute_ndcg_for_query, query_tuples))
                    ):
                        pbar.update()
                        ndcg_scores.append(_)
            scores.append(np.mean(ndcg_scores))

        # Return the average NDCG@k of all queries for each 'k'
        return scores
