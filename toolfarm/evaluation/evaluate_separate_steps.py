from rouge import Rouge
import jsonlines
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--prediction_file', type=str, default="", required=True, help='Prediction file path. Should be a jsonl file, and contains both targets and predictions')
args = parser.parse_args()


def parse(text: str):
    action_regex = r"Action: (.*)\n"
    input_regex = r"Action Input: (.*)\n"
    text += "\n"
    action = re.findall(action_regex, text)
    action_input = re.findall(input_regex, text)
    return action, action_input

def evaluate_rougel(cand_list: list, ref_list: list):
    rouge = Rouge()
    rouge_score = rouge.get_scores(hyps=cand_list, refs=ref_list, avg=True)
    rougel = rouge_score["rouge-l"]["f"]
    return rougel

def evaluate_em(cand_list: list, ref_list: list):
    em = 0
    for cand, ref in zip(cand_list, ref_list):
        em += (1 if cand == ref else 0)
    return em/len(cand_list)


if __name__=='__main__':
    
    fa_cand_list, fa_ref_list = [], []
    ac_cand_list, ac_ref_list = [], []
    inp_cand_list, inp_ref_list = [], []

    for data in jsonlines.open(args.prediction_file, "r"):
        tmp_em, tmp_rougel = 0.0, 0.0
        candidate = data["prediction"]
        reference = data["target"]
        if "Final Answer" in reference:
            if candidate == "":
                continue
            fa_cand_list.append(candidate)
            fa_ref_list.append(reference)
            
        if "Action" in reference and "Action Input" in reference:
            cand_action, cand_action_input = parse(candidate)
            ref_action, ref_action_input = parse(reference)
            ac_cand_list.append(cand_action)
            ac_ref_list.append(ref_action)
            inp_cand_list.append(cand_action_input)
            inp_ref_list.append(ref_action_input)

    rougel = round(evaluate_rougel(fa_cand_list, fa_ref_list), 2)
    action_em = round(evaluate_em(ac_cand_list, ac_ref_list), 2)
    action_input_em = round(evaluate_em(inp_cand_list, inp_ref_list), 2)
    print(rougel, action_em, action_input_em)

