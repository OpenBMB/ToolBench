'''
Evaluate the score of a query corresponding to different candidates
'''

from Prompts.rank_prompts import LLM_PAIRWISE_RANK_SUBFIX_SYSTEM_PROMPT, LLM_PAIRWISE_RANK_USER_PROMPT
import random
from Tree.Tree import tree_node


def rank2symmetry(llm_interface, LLM_rank_args, cand1,cand2):
    '''
    Use llm to compare the height, due to the sequence, you need to compare each of the two in the front
    '''
    single_rank_func = LLM_rank_args["rank_func"]
    score = [0,0]
    bigger1,query_count1, total_tokens1 = single_rank_func(llm_interface, LLM_rank_args, cand1,cand2)
    score[1 - bigger1] += 1
    bigger2,query_count2, total_tokens2 = single_rank_func(llm_interface, LLM_rank_args, cand2,cand1)
    score[bigger2] += 1
    if score[0] > score[1]:
        return 1 , query_count1 + query_count2, total_tokens1 + total_tokens2
    elif score[0] < score[1]:
        return -1, query_count1 + query_count2, total_tokens1 + total_tokens2
    else:
        return 0, query_count1 + query_count2, total_tokens1 + total_tokens2



def rank2_subfix(llm_interface,LLM_rank_args, cand1,cand2):
    '''
    Assumed that the two candidates have a long common prefix
    '''
    anscestor_interesction = tree_node.find_ancestor_intersection(cand1,cand2)
    assert anscestor_interesction != None
    intersect_trice = anscestor_interesction.get_former_trice_from_this_node(end_node=None)
    trice_1 = cand1.get_former_trice_from_this_node(end_node=anscestor_interesction)
    trice_2 = cand2.get_former_trice_from_this_node(end_node=anscestor_interesction)

    system_message = LLM_PAIRWISE_RANK_SUBFIX_SYSTEM_PROMPT
    system_message = system_message.replace("{task_description}", LLM_rank_args["task_description"])
    system_message = system_message.replace("{intersect_trice}", intersect_trice)
    system_message = system_message.replace("{candidate_A}",trice_1)
    system_message = system_message.replace("{candidate_B}",trice_2)
    llm_interface.change_messages([{"role":"system","content":system_message},
                                   {"role":"user","content":LLM_PAIRWISE_RANK_USER_PROMPT},
                                   ])
    output,error_code, total_tokens = llm_interface.parse(functions=LLM_rank_args["functions"],function_call="none",process_id=LLM_rank_args["process_id"])
    if output["content"].strip().lower()[-1] == "a":
        return 1, 1, total_tokens
    else:
        return 0, 1, total_tokens
    
def sum_based_rankn(llm_interface,LLM_rank_args, candidates):
    '''
    All pairs are sorted pairwise, sum the total points, and choose the best
    '''
    total_querys = 0
    total_tokens = 0
    scores = [0]*len(candidates)
    for i in range(len(candidates)-1):
        for j in range(i+1,len(candidates)):
            pairwise_rank,query_count,rank2_tokens = rank2symmetry(llm_interface,LLM_rank_args, candidates[i],candidates[j])
            total_querys += query_count
            total_tokens += rank2_tokens
            if pairwise_rank > 0:
                scores[i] += 1
            elif pairwise_rank < 0:
                scores[j] += 1
            else:
                scores[i] += 0.5
                scores[j] += 0.5
    return scores, total_querys, total_tokens



if __name__ ==  "__main__":
    random.seed(42)
    # candidates = [
    #     "234",
    #     "66.5",
    #     "77.1",
    #     "88.967",
    #     "pi",
    #     # "e",
    #     # "ln(2)"
    # ]
    candidates = [
        "77.1",
        "88.967",
        "pi",
        "66.5",
        "234",
        "ln(2)"
    ]
    '''
    starting_delta:
    50 -> 42.85%
    100 -> 35.99%
    150 -> 29.66%
    200 -> 24.03%
    '''
