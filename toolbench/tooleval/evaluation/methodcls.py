from typing import Dict, List,Callable

class BaseToolMethod:
    def __init__(self):
        pass
    def convert_result_to_dict(self,result):
        '''Return Format
        --------
        {
            'method': 'method name',
            'total_steps': int,
            'final_answer': 'answer',
            'answer_details': [{
                "role": "system",
                "message": "",
                "next": [
                    {
                        "role": "user",
                        "message": "I am planning ...",
                        "next": [
                            {
                                "role": "tool",
                                "message": "{'name': 'Finish', 'arguments': '{\\n  \"return_type\": \"give_answer\",\\n  \"final_answer\": \"I encountere...",
                                "next": []
                            }
                        ]
                    }
                ]
            }]
        }
        
        '''
        pass
    def forward(self,query:str,tools:List[Dict],tool_func:Callable)->Dict:
        pass
    
    def __call__(self,query:str,tools:List[Dict],tool_func:Callable)->Dict:
        result = self.forward(query,tools,tool_func)
        return self.convert_result_to_dict(result)
    
