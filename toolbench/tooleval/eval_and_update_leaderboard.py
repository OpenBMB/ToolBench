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
abs_dir = os.path.split(__file__)[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--leaderboard_folder',default=os.path.join(abs_dir,'results'))
    
    parser.add_argument('--evalset',default='default_evalset',help='the name of the evalset.')
    parser.add_argument('--method',default='',help='what\' the name of the method.')
    parser.add_argument('--result_folder',required=True,help='where the method result stored.')
    parser.add_argument('--ref_method',default='',help='what the reference method is.')
    parser.add_argument('--ref_result_folder',default=os.path.join(abs_dir,'results','default_evalset','gpt-3.5-turbo_CoT'),help='where the reference answer stored.')
    
    
    parser.add_argument('--evaluators_cfg_path',default=os.path.join(abs_dir,'evaluators'),help='where the evaluators config files are stored.')
    parser.add_argument('--evaluator',default='tooleval_gpt-3.5-turbo_normalized',help='which evaluator to use.')
    parser.add_argument('--max_eval_threads',default=16,type=int,help='how many threads to use for evaluation.')

    return parser.parse_args()


if __name__=='__main__':
    args = parse_args()
    if args.method =='':
        args.method = os.path.split(args.result_folder)[1]
    if args.ref_method =='':
        args.ref_method = os.path.split(args.ref_result_folder)[1]
    
    leaderboard_filename = '###'.join(['leaderboard',args.evalset,args.evaluator,args.ref_method]) + '.csv'
    leaderboard_filepath = os.path.join(args.leaderboard_folder,leaderboard_filename)

        
    # setting up eval set
    evalset = {(os.path.split(file)[1]).split('.json')[0]:json.load(open(file)) for file in glob(os.path.join(args.ref_result_folder,'*.json'))}
    
    # read the result
    result = {
        subset:json.load(open(os.path.join(args.result_folder,subset+'.json')))
        for subset in evalset.keys()
    }
    
    
    if os.path.exists(leaderboard_filepath):
        leaderboard = pd.read_csv(leaderboard_filepath)
    else:
        print('File {} not exists. Creating...'.format(leaderboard_filepath))
        leaderboard = pd.DataFrame(columns=['Method','WinRate','StdError',
                                            *[subset+'_WinRate' for subset in evalset.keys()],
                                            *[subset+'_StdError' for subset in evalset.keys()]])
    def print_and_save_leaderboard(leaderboard):
        leaderboard.sort_values(axis=0,by='WinRate',ascending=False,inplace=True)
        print('###### Leaderboard vs {} ######'.format(args.ref_method))
        print(leaderboard)
        leaderboard.to_csv(leaderboard_filepath,index=False)
    print_and_save_leaderboard(leaderboard)
    
    if args.method in leaderboard['Method'].values:
        print('Warning: The method {} has already been in the leaderboard. Overwrite? (y/n)'.format(args.method))
        if input()!='y':
            print('Abort.')
            exit(0)
        print('Replacing...')
        # adding the method to the leaderboard
    leaderboard.loc[len(leaderboard)] = {'Method':args.method}
    print(leaderboard.loc[leaderboard['Method']==args.method])
    # setting up evaluators
    evaluators = [load_registered_automatic_evaluator(evaluator_name=args.evaluator,evaluators_cfg_path=args.evaluators_cfg_path) for _ in range(args.max_eval_threads)]
    
    print('#####  Evaluation Info #####')
    print('Evalset: {}'.format(args.evalset))
    print('Evalset Subsets: {} '.format(list(evalset.keys())))
    print('Method: {}'.format(args.method))
    print('Reference Method: {}'.format(args.ref_method))
    print('Evaluator: {}'.format(args.evaluator))
    print('Result Folder: {}'.format(args.result_folder))
    print('Reference Result Folder: {}'.format(args.ref_result_folder))
    print('Leaderboard FilePath: {}'.format(leaderboard_filepath))
    print()
    
    
    def get_preference(qid,query,tools,ref_ans,ans,):
        global evaluators
        evaluator = random.choice(evaluators)
        ret = evaluator.annotate_preference(
            query,
            tools,
            [ref_ans,ans])
        return qid,ret
    def get_most_preferred(d:list)->np.ndarray:
        if np.iterable(d):
            d = np.asanyarray(d)
            bins = np.bincount(d)
            max_val = np.max(bins)
            argmax = np.where(max_val==bins)[0]
            return argmax
        else:
            return np.asarray([d])


    pref_dict_filepath = os.path.join(args.leaderboard_folder,'###'.join(['total_pref_dict',args.evalset,args.evaluator,args.ref_method,args.method])+'.npy')

    # evaluate each subset
    total_pref = []
    total_pref_dict = {}
    for subset in evalset.keys():
        print('Evaluating {}...'.format(subset))
        leaderboard.loc[leaderboard['Method']==args.method,subset+'_WinRate'] = 0
        leaderboard.loc[leaderboard['Method']==args.method,subset+'_StdError'] = 0
        pref = []
        prefer_dict = {}
        with ThreadPoolExecutor(args.max_eval_threads) as pool:
            future = []
            for qid in evalset[subset].keys():
                try:
                    future.append(pool.submit(
                        get_preference,
                        qid,
                        evalset[subset][qid]['query'],
                        evalset[subset][qid]['available_tools'],
                        evalset[subset][qid]['answer'],
                        result[subset][qid]['answer']
                    ))
                except KeyError as e:
                    print('Warning : Missing answer for query {} in answer file! '.format(e))
            
            for thd in tqdm(as_completed(future),total=len(future),ncols=100):
                qid,preference = thd.result()
                prefer_dict[qid] = get_most_preferred(preference)[0]
        pref = np.array(list(prefer_dict.values()))        
        # update the leaderboard
        leaderboard.loc[leaderboard['Method']==args.method,subset+'_WinRate'] = np.mean(pref)
        leaderboard.loc[leaderboard['Method']==args.method,subset+'_StdError'] = np.std(pref)/np.sqrt(len(pref))
        total_pref.extend(pref)
        total_pref_dict.update(prefer_dict)
    leaderboard.loc[leaderboard['Method']==args.method,'WinRate'] = np.mean(total_pref)
    leaderboard.loc[leaderboard['Method']==args.method,'StdError'] = np.std(total_pref)/np.sqrt(len(total_pref))
    
    # np.save(os.path.join(args.leaderboard_folder,'###'.join(['total_pref',args.evalset,args.evaluator,args.ref_method,args.method])+'.npy'),total_pref)
    np.save(pref_dict_filepath,total_pref_dict)

    print_and_save_leaderboard(leaderboard)