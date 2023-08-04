from tenacity import retry, wait_random_exponential, stop_after_attempt
import os

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
    def __init__(self, pool_json_file):
        self.api_key = os.environ.get('OPENAI_KEY')

    @retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(10),reraise=True)
    def request(self,messages,**kwargs):
        import openai
        kwargs['api_key'] = self.api_key
        return openai.ChatCompletion.create(messages=messages,**kwargs)
    
    def __call__(self,messages,**kwargs):
        return self.request(messages,**kwargs)
                
