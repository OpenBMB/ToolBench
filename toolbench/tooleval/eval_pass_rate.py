from evaluators import load_registered_automatic_evaluator
import os
import json
import csv
from evaluators.registered_cls.rtl import AnswerStatus, TaskStatus, AnswerPass
import random
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse
from tqdm import tqdm
from utils import test_sets, get_steps

abs_dir = os.path.split(__file__)[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--converted_answer_path', type=str, default="", required=True, help='converted answer path')
    parser.add_argument('--save_path', type=str, default="", required=False, help='result save path')
    parser.add_argument('--reference_model', type=str, default="", required=False, help='model predictions path')
    parser.add_argument('--test_ids', type=str, default="", required=True, help='model predictions path')
    parser.add_argument('--evaluator', type=str, default="tooleval_gpt-3.5-turbo_default", required=False, help='which evaluator to use.')
    parser.add_argument('--max_eval_threads', type=int, default=30, required=False, help='max threads nums')
    parser.add_argument('--evaluate_times', type=int, default=4, required=False, help='how many times to predict with the evaluator for each solution path.')
    return parser.parse_args()

def write_results(filename: str, reference_model: str, label_cnt: dict) -> None:
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["query", "solvable", "available_tools", "model_intermediate_steps", "model_final_step", "model", "query_id", "is_solved", "pass_rate_label", "reason", "not_hallucinate"])
        for query_id in label_cnt:
            if label_cnt[query_id]["passed"] > label_cnt[query_id]["failed"]:
                final_label = "passed"
            elif label_cnt[query_id]["passed"] < label_cnt[query_id]["failed"]:
                final_label = "failed"
            else:
                if random.random() < 0.5: # if tie, random choose
                    final_label = "passed"
                else:
                    final_label = "failed"
            query = label_cnt[query_id]["query"]
            task_solvable = label_cnt[query_id]["task_solvable"]
            tool_names = label_cnt[query_id]["tool_names"]
            answer_steps = label_cnt[query_id]["answer_steps"]
            final_step = label_cnt[query_id]["final_step"]
            is_solved = label_cnt[query_id]["is_solved"]
            reason = label_cnt[query_id]["reason"]
            not_hallucinate = label_cnt[query_id]["not_hallucinate"]
            writer.writerow([query, task_solvable, tool_names, answer_steps, final_step, reference_model, query_id, is_solved, final_label, reason, not_hallucinate])
            

if __name__ == "__main__":
    args = parse_args()
    evaluators = [load_registered_automatic_evaluator(evaluator_name=args.evaluator, evaluators_cfg_path=os.path.join(abs_dir,'evaluators')) for _ in range(args.max_eval_threads)]
    
    def compute_pass_rate(query_id, example):
        global evaluators
        evaluator = random.choice(evaluators)
        try:
            not_hallucinate = evaluator.check_has_hallucination(
            example['available_tools'],
            example['answer']
            )
        except:
            not_hallucinate = True
        answer_steps, final_step = get_steps(example)
        
        if "'name': 'Finish'" not in final_step:
            return query_id, TaskStatus.Solvable, AnswerStatus.Unsolved, "failed", "No answer", not_hallucinate
        
        is_solved, is_solved_reason = evaluator.check_is_solved(
            {
                'query':example['query'],
                'available_tools':example['available_tools'],
            },
            example['answer'],
            return_reason=True
        )
        if is_solved == AnswerStatus.Solved:
            is_solved_flag = True
        elif is_solved == AnswerStatus.Unsolved:
            is_solved_flag = False
        else:
            is_solved_flag = False

        task_solvable, task_solvable_reason = evaluator.check_task_solvable(
            {
                'query':example['query'],
                'available_tools':example['available_tools'],
            },
            has_been_solved=is_solved_flag,
            return_reason=True
        )

        is_passed = evaluator.is_passed(
            {
                'query':example['query'],
                'available_tools':example['available_tools'],
            },
            example['answer'],
            answer_status=is_solved,
            task_status=task_solvable
        )

        reason = f"Is solved: {is_solved_reason}\nTask solvable: {task_solvable_reason}"
        if is_passed == AnswerPass.Passed:
            label = "passed"
        elif is_passed == AnswerPass.Failed:
            label = "failed"
        else:
            if random.random() < 0.5: # if unsure, random choose
                label = "passed"
            else:
                label = "failed"
        return query_id, task_solvable, is_solved, label, reason, not_hallucinate
        
    reference_model = args.reference_model
    output_list = []
    for test_set in test_sets:
        reference_path = f"{args.converted_answer_path}/{reference_model}/{test_set}.json"
        test_ids = list(json.load(open(os.path.join(args.test_ids, test_set+".json"), "r")).keys())
        reference_examples = json.load(open(reference_path, "r"))
        if os.path.exists(f"{args.save_path}/{test_set}_{reference_model}.json"):
            existed_ids = list(json.load(open(f"{args.save_path}/{test_set}_{reference_model}.json", "r")).keys())
            label_cnt = json.load(open(f"{args.save_path}/{test_set}_{reference_model}.json", "r"))
        else:
            existed_ids = []
            label_cnt = {}
        
        with ThreadPoolExecutor(args.max_eval_threads) as pool:
            future = []
            for query_id in reference_examples:
                if str(query_id) not in test_ids:
                    continue
                if query_id in existed_ids:
                    continue
                for i in range(args.evaluate_times):
                    example = reference_examples[query_id]
                    future.append(pool.submit(
                        compute_pass_rate,
                        query_id,
                        example
                    ))

            for thd in tqdm(as_completed(future),total=len(future),ncols=100):
                query_id, task_solvable, is_solved, machine_label, reason, not_hallucinate = thd.result()
                example = reference_examples[query_id]
                query = example["query"]
                tool_names = []
                for tool_dict in example["available_tools"]:
                    tool_name = tool_dict["name"]
                    tool_names.append(tool_name)
                answer_steps, final_step = get_steps(example)
                if query_id not in label_cnt:
                    label_cnt[query_id] = {"passed":0, "failed":0}
                if machine_label == "passed":
                    label_cnt[query_id]["passed"] += 1
                else:
                    label_cnt[query_id]["failed"] += 1
                label_cnt[query_id]["query"] = query
                label_cnt[query_id]["task_solvable"] = str(task_solvable)
                label_cnt[query_id]["tool_names"] = tool_names
                label_cnt[query_id]["answer_steps"] = answer_steps
                label_cnt[query_id]["final_step"] = final_step
                label_cnt[query_id]["is_solved"] = str(is_solved)
                label_cnt[query_id]["reason"] = reason
                label_cnt[query_id]["not_hallucinate"] = not_hallucinate
                json.dump(label_cnt, open(f"{args.save_path}/{test_set}_{reference_model}.json", "w"), ensure_ascii=False, indent=4)
        json.dump(label_cnt, open(f"{args.save_path}/{test_set}_{reference_model}.json", "w"), ensure_ascii=False, indent=4)
        
        filename = f"{args.save_path}/{test_set}_{reference_model}.csv"
        write_results(filename, reference_model, label_cnt)
        pass_rate = 0
        for query_id in label_cnt:
            if label_cnt[query_id]["failed"] <= label_cnt[query_id]["passed"]:
                pass_rate += 1
        pass_rate /= len(label_cnt)
        print(f"Test set: {test_set}. Model: {reference_model}. Pass rate: {str(pass_rate)}")
        

        
