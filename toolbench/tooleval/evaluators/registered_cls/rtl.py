import json
import re
import random
import math
from typing import List, Union, Dict, Any, Callable, Optional
from copy import deepcopy
from tenacity import retry, stop_after_attempt



from .utils import register_evaluator,OpenaiPoolRequest
from .tooleval import OpenAINormalizedEvaluator

from enum import Enum

class AnswerStatus(Enum):
    Unsure = "Unsure"
    Unsolved = "Unsolved"
    Solved = "Solved"
    
class TaskStatus(Enum):
    Unsure = "Unsure"
    Unsolvable = "Unsolvable"
    Solvable = "Solvable"
    
class AnswerPass(Enum):
    Unsure = "Unsure"
    Failed = "Failed"
    Passed = "Passed"
    

@register_evaluator
class ReinforceToolLearningEvaluator(OpenAINormalizedEvaluator):
    def check_has_hallucination(self,available_tools:List[Dict],answer:Dict[Any,Any])->bool:
        available_names = set([tool['name'] for tool in available_tools])
        
        def check_node_valid(node:Dict)->bool:
            # print(node)
            if node['role'] == "tool":
                if isinstance(node['message'], dict):
                    node['message'] = str(node['message'])
                name = re.findall(r"'name':\s*'(.*?)'",node['message'],re.DOTALL)[0]
                return name in available_names
            return True            
        
        def recurssive_check(nodes:Union[List,Dict])->bool:
            if isinstance(nodes,Dict):
                if not check_node_valid(nodes):
                    return False
                else:
                    return recurssive_check(nodes['next'])
            if isinstance(nodes,List):
                for node in nodes:
                    if not recurssive_check(node):
                        return False
                return True
            raise ValueError(f'Unknown node type {type(nodes)}')
            
        return recurssive_check(answer['answer_details'])
    
    def check_is_solved(self,
                        task_description:Dict,
                        answer:Dict[Any,Any],
                        return_reason=False,
                        ) -> Union[AnswerStatus,Optional[str]]:
        
        # empty situation
        if answer['final_answer']=='' or 'give_up_and_restart' in  answer['final_answer']:
            if return_reason:
                return AnswerStatus.Unsolved, "Empty final answer!"
            return AnswerStatus.Unsolved, ""
        
        ret = self.function_call(
            'check_answer_status',
            {
                'query':task_description['query'],
                'answer':answer['final_answer']
            },
            return_reason=return_reason
        )
        answer_status = AnswerStatus(ret['answer_status'])
        
        if answer_status == AnswerStatus.Unsure:
            # detailed check here
            ret = self.function_call(
                'parse_answer_status',
                {
                    'query':task_description['query'],
                    'answer':json.dumps(answer)
                },
                return_reason=return_reason
            )
            answer_status = AnswerStatus(ret['answer_status'])

        if return_reason:
            return answer_status,ret['reason']
        return answer_status, ""
    
    def check_task_solvable(self,
                            task_description:Dict,
                            has_been_solved=False,
                            return_reason=False,
                            )->Union[TaskStatus,Optional[str]]:
        if has_been_solved:
            if return_reason:
                return TaskStatus.Solvable, 'Task has been solved before.'
            return TaskStatus.Solvable, ''
        
        ret = self.function_call(
            'check_task_solvable',
            {
                'task':json.dumps(task_description)
            },
            return_reason=return_reason
        )
        task_status = TaskStatus(ret['task_status'])
        if return_reason:
            return task_status, ret['reason']
        return task_status, ''
        
    def is_passed(self,
                  task_description:Dict,
                  answer:Dict[Any,Any],
                  answer_status:AnswerStatus=None,
                  task_status:TaskStatus=None,
                  )->AnswerPass:
        
        if answer_status is None:
            answer_status, _ = self.check_is_solved(task_description,answer)
            
        if answer_status == AnswerStatus.Solved:
            return AnswerPass.Passed
        else:
            if task_status is None:
                task_status, _ = self.check_task_solvable(
                    task_description,
                    has_been_solved=answer_status==AnswerStatus.Solved)
            
            if answer_status == AnswerStatus.Unsolved:
                if task_status == TaskStatus.Solvable:
                    return AnswerPass.Failed
                if task_status == TaskStatus.Unsure:
                    return AnswerPass.Unsure
                if task_status == TaskStatus.Unsolvable:
                    return AnswerPass.Passed
            elif answer_status == AnswerStatus.Unsure:
                if task_status == TaskStatus.Solvable:
                    return AnswerPass.Unsure
                if task_status == TaskStatus.Unsure:
                    return AnswerPass.Unsure
                if task_status == TaskStatus.Unsolvable:
                    return AnswerPass.Passed
                                
        return AnswerPass.Failed
    
    def check_identity_answers(self,
                       answers:List[Dict[Any,Any]],
                       )->bool:
        ref_answer = answers[0]
        for ans in answers[1:]:
            if ans['final_answer']!=ref_answer['final_answer']:
                return False
            if str(ans['answer_details'])!=str(ref_answer['answer_details']):
                return False
        return True
    
    @retry(stop=stop_after_attempt(3),reraise=True)
    def select_better_answer(self,
                           task_description:Dict,
                           task_status:TaskStatus,
                           ans_idxs:List[int],
                           answers:List[Dict[Any,Any]],
                           answer_status:AnswerStatus,
                           *,
                           return_reason=True)->int:
        answers = deepcopy(answers)
        
        if self.check_identity_answers(answers):
            return random.choice(ans_idxs)
        
        judge_focus = {
            TaskStatus.Solvable:'Since query is solvable, you should select answer with smaller "total_steps" and informative, accurate "final_answer".',
            TaskStatus.Unsure:'Since query is unsure, you should select a more comprehensive exploration for possible solutions.',
            TaskStatus.Unsolvable:'Since query is unsolvable, you should select answer with smaller "total_steps" and detailed reasons for failure.'
        }
        
        ret = self.function_call(
            'select_better_answer', {
                'query':task_description['query'],
                'answer_0':json.dumps(answers[0]),
                'answer_1':json.dumps(answers[1]),
                # 'q_status':judge_focus[task_status],
            },
            return_reason=return_reason
        )
        index = int(ret['index'])
        if index in ans_idxs:
            return index
        else:
            raise ValueError(f'Index {index} not found!')
    
    def normalized_openai_completions(self,task_description:Dict, answers:List[Dict[Any,Any]], task_status:None, answer_statuss:[None, None])->int:
        if answer_statuss[0] is None:
            print("comparing from scratch...")
            status = [self.check_is_solved(task_description,ans)[0] for ans in answers]
        else:
            status = answer_statuss
        # check whether there are answers solve the task
        solves = [idx for idx,s in enumerate(status) if s==AnswerStatus.Solved]
        
        if len(solves)==1:
            return solves[0]
        elif len(solves)>1:
            # pick best one
            if task_status is None:
                task_status, _ = self.check_task_solvable(task_description,has_been_solved=True)
            else:
                task_status = task_status
            return self.select_better_answer(task_description,task_status,solves,[answers[idx] for idx in solves],AnswerStatus.Solved)
        
        # if no answer solves the task, check whether unsure answer exists
        unsures = [idx for idx,s in enumerate(status) if s==AnswerStatus.Unsure]
        
        if len(unsures) == 1:
            return unsures[0]
        elif len(unsures)>1:
            # pick best one
            if task_status is None:
                task_status, _ = self.check_task_solvable(task_description)
            else:
                task_status = task_status
            return self.select_better_answer(task_description,task_status,unsures,[answers[idx] for idx in unsures],AnswerStatus.Unsure)
        
        # if all failed
        # pick best one
        if task_status is None:
            task_status, _ = self.check_task_solvable(task_description)
        else:
            task_status = task_status
        return self.select_better_answer(task_description,task_status,list(range(len(answers))),answers,AnswerStatus.Unsolved)