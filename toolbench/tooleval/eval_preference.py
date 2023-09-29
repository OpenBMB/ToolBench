# Evaluate a method outputs in different aspectes and update the leaderboard
# `result_folder` should contain the following 6 json files:
#   - `G1_category.json`: 
#           single-tool instruction;
#           test on unseen tools from unseen categories
#   - `G1_instruction.json`: 
#           single-tool instruction; 
#           test the model's instruction generalization ability
#   - `G1_tool.json`: 
#           single-tool instruction; 
#           test the model's generalization abilities on unseen tools from seen categories
#   - `G2_category.json`: 
#           intra-category multi-tool instruction
#           test on unseen tools from unseen categories
#   - `G2_instruction.json`: 
#           intra-category multi-tool instruction
#           test the model's instruction generalization ability
#   - `G3_instruction.json`: 
#           intra-collection multi-tool instruction
#           test the model's instruction generalization ability
from glob import glob
import os
import argparse
import json
import pandas as pd
import random
import numpy as np
from evaluators import load_registered_automatic_evaluator
from concurrent.futures import ThreadPoolExecutor,as_completed
from tqdm import tqdm
from utils import test_sets, get_steps, task_status_mapping, answer_status_mapping
import csv

abs_dir = os.path.split(__file__)[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--converted_answer_path', type=str, default="", required=True, help='result save path')
    parser.add_argument('--reference_model', type=str, default="gpt-4-0613_dfs", required=False, help='ref model predictions path')
    parser.add_argument('--output_model', type=str, default="toolllama-2-0830-thought", required=False, help='output model predictions path')
    parser.add_argument('--test_ids', type=str, default="", required=True, help='test query ids path')
    parser.add_argument('--save_path', type=str, default="preference_results", required=False, help='preference results save path')
    parser.add_argument('--pass_rate_result_path', type=str, default="pass_rate_results", required=False, help='pass rate results save path')
    parser.add_argument('--max_eval_threads', type=int, default=3, required=False, help='max threads nums')
    parser.add_argument('--evaluator',default='tooleval_gpt-3.5-turbo_default', required=False, help='which evaluator to use.')
    parser.add_argument('--use_pass_rate',default='false',help='to use existed pass rate result or compare preference from scratch.')
    parser.add_argument('--evaluate_times',default=2,help='how many times to predict with the evaluator for each solution path.')
    
    return parser.parse_args()

def get_pass_rate_results(filename: str) -> dict:
    csv_reader = csv.reader(open(filename), delimiter="\t")
    return_dict = {}
    line_cnt = 0
    for line in csv_reader:
        if line_cnt == 0:
            for index, item in enumerate(line):
                if item == "query":
                    query_index = index
                elif item == "solvable":
                    solvable_index = index
                elif item == "available_tools":
                    atools_index = index
                elif item == "model_intermediate_steps":
                    mid_steps_index = index
                elif item == "model":
                    modelname_index = index
                elif item == "model_final_step":
                    final_step_index = index
                elif item == "is_solved":
                    is_solved_index = index
                elif item == "pass_rate_label":
                    machine_label_index = index
                elif item == "query_id":
                    query_id_index = index
                elif item == "reason":
                    reason_index = index
                elif item == "not_hallucinate":
                    not_hallucinate_index = index
                else:
                    print(f"Unrecognized item: {item}")
                        
        line_cnt = 1
        query = line[query_index]
        query_id = line[query_id_index]
        solvable = line[solvable_index]
        atools = line[atools_index]
        mid_steps = line[mid_steps_index]
        modelname = line[modelname_index]
        final_step = line[final_step_index]
        is_solved = line[is_solved_index]
        machine_label = line[machine_label_index]
        return_dict[query_id] = {
            "query": query,
            "solvable": solvable,
            "atools": atools,
            "mid_steps": mid_steps,
            "modelname": modelname,
            "final_step": final_step,
            "is_solved": is_solved,
            "machine_label": machine_label
        }
    # print(return_dict.keys(), len(return_dict.keys()))
    return return_dict

def write_results(filename:str, prefer_dict: dict, reference_model: str, output_model: str, reference_examples: dict, output_examples: dict) -> None:
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["query", "available_tools", "ref_model_intermediate_steps", "ref_model_final_step", "output_model_intermediate_steps", "output_model_final_step", "preference_label", "query_id", "ref_model", "output_model"])
    
        for query_id in prefer_dict:
            ref_example = reference_examples[query_id]
            output_example = output_examples[query_id]
            tool_names = []
            for tool_dict in ref_example['available_tools']:
                tool_name = tool_dict["name"]
                tool_names.append(tool_name)
            ref_steps, ref_final_step = get_steps(ref_example)
            output_steps, output_final_step = get_steps(output_example)

            if prefer_dict[query_id][reference_model] > prefer_dict[query_id][output_model]:
                preference = 1
            elif prefer_dict[query_id][reference_model] < prefer_dict[query_id][output_model]:
                preference = 2
            else:
                preference = 3     
            writer.writerow([ref_example['query'], str(tool_names), ref_steps, ref_final_step, output_steps, output_final_step, str(preference), query_id, reference_model, output_model])
    return None


if __name__=='__main__':
    args = parse_args()
    evaluators = [load_registered_automatic_evaluator(evaluator_name=args.evaluator, evaluators_cfg_path=os.path.join(abs_dir,'evaluators')) for _ in range(args.max_eval_threads)]
    
    def get_preference(query_id, task_status, answer_statuss, ref_example, output_example):
        global evaluators
        evaluator = random.choice(evaluators)
        
        preference = evaluator.annotate_preference(
            ref_example['query'],
            ref_example['available_tools'],
            [ref_example['answer'], output_example['answer']],
            task_status=task_status, answer_statuss=answer_statuss
        )
        if preference == 0:
            return query_id, "ref"
        elif preference == 1:
            return query_id, "output"
        else:
            return query_id, "equal"
    
    reference_model = args.reference_model
    output_model = args.output_model

    for test_set in test_sets:
        test_ids = list(json.load(open(os.path.join(f"{args.test_ids}/{test_set}.json"), "r")).keys())
        reference_path = f"{args.converted_answer_path}/{reference_model}/{test_set}.json"
        output_path = f"{args.converted_answer_path}/{output_model}/{test_set}.json"
        reference_examples = json.load(open(reference_path, "r"))
        output_examples = json.load(open(output_path, "r"))
        print('Evaluating {}...'.format(test_set))
        pref = []
        if os.path.exists(f"{args.save_path}/{test_set}_{reference_model}_{output_model}.json"):
            prefer_dict = json.load(open(f"{args.save_path}/{test_set}_{reference_model}_{output_model}.json", "r"))
        else:
            prefer_dict = {}
        ref_pass_result_file = f"{args.pass_rate_result_path}/{test_set}_{reference_model}.csv"
        output_pass_result_file = f"{args.pass_rate_result_path}/{test_set}_{output_model}.csv"

        ref_pass_result_dict = get_pass_rate_results(ref_pass_result_file)
        output_pass_result_dict = get_pass_rate_results(output_pass_result_file)
        for i in range(int(args.evaluate_times)):
            with ThreadPoolExecutor(args.max_eval_threads) as pool:
                future = []
                for qid in test_ids:
                    if qid not in prefer_dict:
                        prefer_dict[qid] = {reference_model: 0, output_model: 0, f"round_{i}": "incomplete"}
                    elif prefer_dict[qid][f"round_{i}"] == "complete":
                        continue
                    if qid in ref_pass_result_dict and qid in output_pass_result_dict:
                        if ref_pass_result_dict[qid]["machine_label"] == "passed" and output_pass_result_dict[qid]["machine_label"] == "failed":
                            prefer_dict[qid][reference_model] += 1
                            continue
                        elif ref_pass_result_dict[qid]["machine_label"] == "failed" and output_pass_result_dict[qid]["machine_label"] == "passed":
                            prefer_dict[qid][output_model] += 1
                            continue
                    
                    if qid not in reference_examples:
                        prefer_dict[qid][output_model] += 1
                        continue
                    if qid not in output_examples:
                        print(f"Query {qid} not in output model converted answers!")
                        prefer_dict[qid][reference_model] += 1
                        continue

                    ref_example = reference_examples[qid]
                    output_example = output_examples[qid]
                    if args.use_pass_rate == 'true':
                        try:
                            task_status = task_status_mapping[ref_pass_result_dict[qid]["solvable"]]
                            answer_statuss = [answer_status_mapping[ref_pass_result_dict[qid]["is_solved"]],answer_status_mapping[output_pass_result_dict[qid]["is_solved"]]]
                        except:
                            task_status = None
                            answer_statuss = [None, None]
                    else:
                        task_status = None
                        answer_statuss = [None, None]

                    if i % 2 == 0 or i >= 0:
                        future.append(pool.submit(
                            get_preference,
                            qid,
                            task_status,
                            answer_statuss,
                            ref_example,
                            output_example
                        ))
                    else:
                        answer_statuss = answer_statuss[::-1]
                        future.append(pool.submit(
                            get_preference,
                            qid,
                            task_status,
                            answer_statuss,
                            output_example,
                            ref_example
                        ))
                    
                for thd in tqdm(as_completed(future),total=len(future),ncols=100):
                    qid, preference = thd.result()
                    
                    if i % 2 == 0 or i >= 0:
                        if preference == "ref":
                            prefer_dict[qid][reference_model] += 1
                        elif preference == "output":
                            prefer_dict[qid][output_model] += 1
                        prefer_dict[qid][f"round_{i}"] = "complete"
                    else:
                        if preference == "ref":
                            prefer_dict[qid][output_model] += 1
                        elif preference == "output":
                            prefer_dict[qid][reference_model] += 1
                        prefer_dict[qid][f"round_{i}"] = "complete"
                    json.dump(prefer_dict, open(f"{args.save_path}/{test_set}_{reference_model}_{output_model}.json", "w"), ensure_ascii=False, indent=4)
        
        json.dump(prefer_dict, open(f"{args.save_path}/{test_set}_{reference_model}_{output_model}.json", "w"), ensure_ascii=False, indent=4)
        filename = f"{args.save_path}/{test_set}_{reference_model}_{output_model}.csv"
        write_results(filename, prefer_dict, reference_model, output_model, reference_examples, output_examples)
        
        win_rate, lose_rate, tie_rate = 0, 0, 0
        for query_id in prefer_dict:
            if prefer_dict[query_id][reference_model] > prefer_dict[query_id][output_model]:
                preference = 1
                lose_rate += 1
            elif prefer_dict[query_id][reference_model] < prefer_dict[query_id][output_model]:
                preference = 2
                win_rate += 1
            else:
                preference = 3
                tie_rate += 1
        win_rate /= len(prefer_dict)
        lose_rate /= len(prefer_dict)
        tie_rate /= len(prefer_dict)
        print(f"Test set: {test_set}. Reference model: {reference_model}, Candidate model: {output_model}. Win rate: {str(win_rate)}, Tie rate: {str(tie_rate)}")
        