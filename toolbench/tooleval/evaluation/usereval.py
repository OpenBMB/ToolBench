import requests
from tqdm import tqdm
from typing import Union, Dict, List, Optional,Tuple
from .methodcls import BaseToolMethod
from .dataclass import *
import json

class UserEvaluation:
    def __init__(self,
                 method:BaseToolMethod,
                 eval_server_addr='http://localhost:8000',
                 evalset='eval20230718'):
        self.eval_server_addr = eval_server_addr
        self.evalset = evalset
        self.method = method
        res = requests.post(self.eval_server_addr+'/neweval',json=self.evalset)
        if res.status_code != 200:
            raise Exception('Failed to obtain new evaluation id! Error: '+res.text)
        ret = res.json()
        self.eval_id = ret['evaluation_id']
        self.len = ret['len']

    def get_new_question(self)->Tuple[str,List]:
        res = requests.post(self.eval_server_addr+'/next_question',json=self.eval_id)
        if res.status_code == 204:
            raise EvalCompleted()
        if res.status_code != 200:
            raise Exception('Failed to obtain new question!')
        
        self.question = Question(**res.json())
        self.tool_name_to_id = {}
        tools = [tool.model_dump() for tool in self.question.available_tools]
        for tool in tools:
            self.tool_name_to_id[tool['name']] = tool.pop('tid')
        
        
        return self.question.query,tools
    def tool_func(self,tool_name:str,tool_args:str)->requests.Response:
        tid = self.tool_name_to_id[tool_name]
        # res = requests.post(self.eval_server_addr+'/api',json={
        #     'evaluation_id':self.eval_id,
        #     'tool_id':tid,
        #     'tool_args':tool_args
        # })
        res = requests.post(self.eval_server_addr+'/rapidapi',json={
            'evaluation_id':self.eval_id,
            'tool_id':tid,
            'tool_args':tool_args
        })
        
        return res
    def _forward(self,query:str,tools:List[Dict])->Dict:
        method_ret = self.method(query,tools,self.tool_func)
        
        return self.question.qid,{
            'query':query,
            'available_tools':tools,
            'answer':method_ret
        }
        
    
    def run(self)->Dict:
        results = {}
        for _ in tqdm(range(self.len),ncols=100):
            try:
                qid,ret = self._forward(*self.get_new_question())
            except EvalCompleted:
                return results
            results[qid] = ret
        return results
