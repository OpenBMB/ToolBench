import json
import random
import re
import math
from typing import List,Union,Dict,Any
from copy import deepcopy
from .utils import OpenaiPoolRequest

def process_answer(answer:Dict):
    answer['final_answer'] = answer['final_answer'][:1000]
    answer['answer_details'] = answer['answer_details'][:3000]
    answer.pop('method',None)
    return answer
def process_tools(tools:List[Dict]):
    for tool in tools:
        tool.pop('description',None)
        tool.pop('parameters',None)
    return tools

class AutomaticEvaluator:
    def __init__(self,eval_config,template):
        self.eval_config = eval_config
        self.template = template
        self.completions_fn = getattr(self,eval_config['fn_completions'])

    def annotate_preference(self,query:str,available_tools:List[Dict[Any,Any]],ans1:Dict,ans2:Dict,multisample=False,sample_n=4)->Union[List[int],int]:
        
        ans1,ans2 = process_answer(ans1),process_answer(ans2)
        available_tools = process_tools(available_tools)
        if not multisample:
            if random.random()<0.5:
                return random.choice(self.completions_fn({'query':query,'available_tools':available_tools},[ans1,ans2]))
            else:
                return 1 - random.choice(self.completions_fn({'query':query,'available_tools':available_tools},[ans2,ans1]))
        else:
            prefers = []
            for i in range(sample_n):
                if random.random()<0.5:
                    prefers.append(random.choice(self.completions_fn({'query':query,'available_tools':available_tools},[ans1,ans2])))
                else:
                    prefers.append(1 - random.choice(self.completions_fn({'query':query,'available_tools':available_tools},[ans2,ans1])))
            return prefers
        


    def openai_completions(self,task_description:Dict,answers:Dict)->List[int]:
        if not hasattr(self,'opr'):
            self.opr = OpenaiPoolRequest(self.eval_config['apis_json'])
            
        conversation = []        
        for message in re.findall(r"<message>(.*?)</message>", self.template,re.DOTALL):
            message = {
                    'role': next(re.finditer(r"<role>(.*?)</role>",message,re.DOTALL)).group().replace('</role>','').replace('<role>',''),
                    'content': next(re.finditer(r"<content>(.*?)</content>",message,re.DOTALL)).group().replace('</content>','').replace('<content>','')
                }
            if message['role']=='user':
                message['content'] = message['content'].format(
                    task_description=json.dumps(task_description),
                    answers=json.dumps(answers))
            conversation.append(message)
        res = self.opr(messages=conversation,**self.eval_config['completions_kwargs'])
        prefers = []
        for choice in res.choices:
            prefers.append(int(json.loads(choice.message.function_call.arguments)['preference']))
        return  prefers
    
    def normalized_openai_completions(self,task_description:Dict,answers:List[Dict[Any,Any]])->List[int]:
        if not hasattr(self,'parsed_function_templates'):
            self.parsed_function_templates = {}
            for function in re.findall(r"<function>(.*?)</function>", self.template,re.DOTALL):
                name = re.findall(r"<name>(.*?)</name>",function,re.DOTALL)[0]
                description = re.findall(r"<description>(.*?)</description>",function,re.DOTALL)[0]
                self.parsed_function_templates[name] = description
        if not hasattr(self,'opr'):
            self.opr = OpenaiPoolRequest(self.eval_config['apis_json'])
        
        def call_openai_completions_with_function_call(function_call,format_str:Dict):
            completion_kwargs = deepcopy(self.eval_config['completions_kwargs'])
            completion_kwargs['function_call'] = {'name':function_call}
            for function in self.eval_config['completions_kwargs']['functions']:
                if function['name']==function_call:
                    completion_kwargs['functions'] = [function]
                    break
            completion_kwargs['messages'] = [{
                'role':'user',
                'content':str(self.parsed_function_templates[function_call]).format(**format_str)
            }]
            res = self.opr.request(**completion_kwargs)
            return json.loads(res.choices[0].message.function_call.arguments)
            
        def select_best_final_answer(query,final_answers:List[str])->int:
            hashed_ans = list(map(hash,final_answers))
            all_same = True
            for item in hashed_ans[1:]:
                if item != hashed_ans[0]:
                    all_same = False
            if all_same:
                return random.choice(range(len(final_answers)))
            while True:
                selected = int(call_openai_completions_with_function_call('select_best_final_answer',{'query':query,'final_answers':final_answers})['best_answer_index'])
                if selected<len(final_answers) and selected>=0:
                    break
            return selected
        def check_solve_query(query,final_answer:str)->bool:
            return bool(call_openai_completions_with_function_call('check_solve_query',{'query':query,'final_answer':final_answer})['is_solved'])
        
        def compare_answer_details(answer:List)->List[int]:         
            parsed_answers = []
            
            for ans in answer:
                parsed_ans = call_openai_completions_with_function_call('parse_answer_details',{'answer_details':ans['answer_details']})
                parsed_ans['total_steps'] = ans['total_steps']
                parsed_answers.append(parsed_ans)

            # calculate socre and return one with highest score
            scores = []
            for ans in parsed_answers:
                score = 0
                score += int(ans['succeed_tool_calling'])*10
                score += int(ans['used_tool_types'])*5
                if int(ans['total_steps'])<=0:
                    score -= int(1e5)
                else:
                    score += -5*math.log(ans['total_steps'])
                scores.append(score)
            # return index of highest score

            highest_idx = [0]
            highest_score = scores[0]
            for idx in range(1,len(scores)):
                score = scores[idx]
                if score>highest_score:
                    highest_idx = [idx]
                    highest_score = score
                else:
                    highest_idx.append(idx)             
            return highest_idx
        
        all_empty = True
        all_nonempty = True
        is_nonempty = []
        for ans in answers:
            status = ans['final_answer']!=''
            if status:
                all_empty = False
            else:
                all_nonempty = False
            is_nonempty.append(status)
        # print(is_nonempty)
        if all_nonempty:
            all_solved = True
            all_failed = True
            is_solved = []
            for ans in answers:
                status = check_solve_query(task_description['query'],ans['final_answer'])
                # print(ans['final_answer'])
                if status:
                    all_failed = False
                else:
                    all_solved = False
                is_solved.append(status)
            
            # print(is_solved)
            if all_solved:
                shortest = int(answers[0]['total_steps'])
                ans_idxs = [0]
                for idx in range(1,len(answers)):
                    ans = answers[idx]
                    if int(ans['total_steps'])<shortest:
                        shortest = int(ans['total_steps'])
                        ans_idxs = [idx]
                    elif int(ans['total_steps'])==shortest:
                        ans_idxs.append(idx)
                # print(ans_idxs)
                # return only one idx
                if len(ans_idxs)>1:
                    return [ans_idxs[select_best_final_answer(
                        task_description['query'],
                        [answers[idx]['final_answer'] for idx in ans_idxs]
                        )]]
                else:
                    return ans_idxs
                
            elif all_failed:
                return compare_answer_details(answers)
            else:
                return [index for index,solve in enumerate(is_solved) if solve]
        elif all_empty:
            return compare_answer_details(answers)
        else:
            return [index for index,nonempty in enumerate(is_nonempty) if nonempty]
        

    
