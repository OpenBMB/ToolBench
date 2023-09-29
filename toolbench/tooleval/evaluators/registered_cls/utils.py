import os
import json
from typing import List,Dict
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

import openai
import random

__registered_evaluators__ = {}

def register_evaluator(cls):
    """
    Decorator function to register classes with the registered_evaluators list.
    """
    __registered_evaluators__[cls.__name__] = cls
    return cls

def get_evaluator_cls(clsname):
    """
    Return the evaluator class with the given name.
    """
    try:
        return __registered_evaluators__.get(clsname)
    except:
        raise ModuleNotFoundError('Cannot find evaluator class {}'.format(clsname))


class OpenaiPoolRequest:
    def __init__(self, pool_json_file=None):
        self.pool:List[Dict] = []
        __pool_file = pool_json_file
        if os.environ.get('API_POOL_FILE',None) is not None:
            __pool_file = os.environ.get('API_POOL_FILE')
            self.now_pos = random.randint(-1, len(self.pool))
        if os.path.exists(__pool_file):
            self.pool = json.load(open(__pool_file))
            self.now_pos = random.randint(-1, len(self.pool))
        print(__pool_file)
        if os.environ.get('OPENAI_KEY',None) is not None:
            self.pool.append({
                'api_key':os.environ.get('OPENAI_KEY'),
                'organization':os.environ.get('OPENAI_ORG',None),
                'api_type':os.environ.get('OPENAI_TYPE',None),
                'api_version':os.environ.get('OPENAI_VER',None)
            })

    # @retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(10),reraise=True)
    def request(self,messages,**kwargs):
        self.now_pos = (self.now_pos + 1) % len(self.pool)
        key_pos = self.now_pos
        item = self.pool[key_pos]
        print(len(self.pool))
        kwargs['api_key'] = item['api_key']
        if item.get('organization',None) is not None:
            kwargs['organization'] = item['organization'] 
        return openai.ChatCompletion.create(messages=messages,**kwargs)
    
    def __call__(self,messages,**kwargs):
        return self.request(messages,**kwargs)
   