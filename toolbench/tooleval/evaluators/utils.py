from tenacity import retry, wait_random_exponential, stop_after_attempt
import os


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
                
