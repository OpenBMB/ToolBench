import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
from tqdm import tqdm
from evaluators import load_registered_automatic_evaluator
import os 
import numpy as np
import copy
from typing import List
from scipy.stats import pearsonr,spearmanr
import random
random.seed(42)

abs_dir = os.path.split(__file__)[0]
annotated_data = json.load(open(os.path.join(abs_dir,'dataset/human_cross_annotated_data.json')))
NUM_WORKERS=16

def get_most_preferred(d:list)->np.ndarray:
    if np.iterable(d):
        d = np.asanyarray(d)
        bins = np.bincount(d)
        max_val = np.max(bins)
        argmax = np.where(max_val==bins)[0]
        return argmax
    else:
        return np.asarray([d])
    
def agreement_score(x,ref:list)->float:
    majority_x = get_most_preferred(x)
    majority_ref = get_most_preferred(ref)
    score_unit = 1/len(majority_x)/len(majority_ref)
    score = 0.0
    for x in majority_x:
        if x in majority_ref:
            score += score_unit
    return score
def get_correlation(x,y):
    x= np.asarray(x)
    y = np.asarray(y)
    x = x+1
    y = y+1
    if np.var(x)==0 or np.var(y)==0:
        return float(random.choice(get_most_preferred(x))==random.choice(get_most_preferred(y)))
    return pearsonr(x,y)[0]

def test_on_annotated_data(evaluator_cfg)->List[List[int]]:
    evaluators = [load_registered_automatic_evaluator(evaluator_cfg) for _ in range(NUM_WORKERS)]
    def get_preference(idx):
        data = annotated_data[idx]
        def process_tools(tools:list):
            for tool in tools:
                tool.pop('description',None)
                tool.pop('parameters',None)
            return tools

        tools = process_tools(data['available_tools'])
        ret = evaluators[idx%NUM_WORKERS].annotate_preference(
            data['query'],
            tools,
            data['answers'],multisample=True)
        return idx,ret
    prefer_dict = {}
    with ThreadPoolExecutor(NUM_WORKERS) as pool:
        # future = [pool.submit(get_preference,idx) for idx in range(100)]
        future = [pool.submit(get_preference,idx) for idx in range(len(annotated_data))]
        for thd in tqdm(as_completed(future),total=len(future),ncols=100):
            if thd.exception() is not None:
                pool.shutdown(cancel_futures=True)
                raise thd.exception()
                exit(-1)
            idx,preference = thd.result()
            prefer_dict[idx] = preference
    prefer = [prefer_dict[idx] for idx in range(len(future))]
    return prefer

def get_popped_and_rest(d:list,index:int):
    l = copy.deepcopy(d)
    popped = l.pop(index)
    return popped,l

def calculate_human_performance():
    human_agreement = []
    variance = []
    for data in annotated_data:
        agreement_scores = [
            agreement_score(*get_popped_and_rest(data['preference'],idx))
            for idx in range(len(data['preference']))
        ]
        human_agreement.append(np.mean(agreement_scores))
        variance.append(np.var([1-agreement_scores[idx] for idx in range(len(agreement_scores))]))
        
            
    return {
        'human_agreement':np.mean(human_agreement),
        'bias':0,
        'variance':np.mean(variance)
    }

        
    
def calculate_evaluator_performance(evaluator_preference,human_preference):
    human_agreement = []
    bias = []
    variance = []
    assert len(evaluator_preference)==len(human_preference),'length of evaluator_preference and human_preference should be the same!'
    correlation = []
    for idx in range(len(evaluator_preference)):
        human_pref = human_preference[idx]
        evaluator_pref = evaluator_preference[idx]
        
        human_agreement.append([
            agreement_score(pref,human_pref) for pref in evaluator_pref
        ])
        bias.append(
            1 - agreement_score(human_pref,evaluator_pref)
        )
        variance.append(
            np.var([1-score for score in human_agreement[-1]])
        )
        correlation.append(get_correlation(human_pref,evaluator_pref))
        
    return{
        'correlation': np.mean(correlation),
        'human_agreement':np.mean(np.mean(human_agreement,axis=1)),
        'bias':np.mean(bias),
        'variance':np.mean(variance)
    }
    
if __name__=='__main__':
    evaluators = ['tooleval_gpt-3.5-turbo_normalized',]
    human_perference = [
        data['preference'] for data in annotated_data
    ]
    
    evaluator_performance = [calculate_human_performance()]
    for evaluator in evaluators:
        if not os.path.exists(os.path.join(abs_dir,'dataset',f'performance_{evaluator}.npy')):
            evaluator_cfg = {
                'evaluators_cfg_path':os.path.join(abs_dir,'evaluators'),
                'evaluator':evaluator
            }
            evaluator_perference = test_on_annotated_data(evaluator_cfg)
            np.save(os.path.join(abs_dir,'dataset',f'performance_{evaluator}.npy'),evaluator_perference)
        
        evaluator_perference = np.load(os.path.join(abs_dir,'dataset',f'performance_{evaluator}.npy'),allow_pickle=True)
        performance = calculate_evaluator_performance(evaluator_perference,human_perference)
        print(performance)
        evaluator_performance.append(performance)
    
    df = pd.DataFrame(evaluator_performance,index=['human']+evaluators)
    df.to_csv(os.path.join(abs_dir,'dataset','evaluator_performance.csv'))
    print(df)