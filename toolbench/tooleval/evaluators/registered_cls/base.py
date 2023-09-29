import random
from typing import List, Union, Dict, Any, Callable
import os
import yaml
from .utils import register_evaluator

def process_answer(answer: Dict):
    answer['final_answer'] = answer['final_answer'][:1000]
    answer['answer_details'] = answer['answer_details'][:3000]
    answer.pop('method', None)
    return answer


def process_tools(tools: List[Dict]):
    for tool in tools:
        tool.pop('description', None)
        tool.pop('parameters', None)
    return tools

@register_evaluator
class BaseEvaluator:
    """Base class for evaluators.
    
    Attributes:
    ----------
        fn_completions : Callable[[Dict,List[Dict]],int]
            The completion function of the evaluator, used to get annotated results.
            This function should take two arguments: `task_description`:Dict and `answers`:List[Dict], return a int stand for the index of best answer.
    
    Functions:
    ---------
        annotate_preference : Callable
            Annotate and return the index of the preferred answer.
        
    """
    def __init__(self,
                 fn_completions: Callable[[Dict,List[Dict]],int] = None,
                 *args,
                 **kwargs):
        self.fn_completions = fn_completions
    def annotate_preference(self,
                            query: str,
                            available_tools: List[Dict[Any, Any]],
                            answers:List[Dict],
                            multisample=False,
                            sample_n=4,
                            task_status=None,
                            answer_statuss=[None, None]) -> Union[List[int], int]:
        """Annotate and return the index of the preferred answer.
        
        For given query, available tools, and two answers, return the index of the preferred answer by calling function `fn_completions` of the evaluator.
        
        Parameters:
        ----------
            query : str
                The query of the task.
            available_tools : List[Dict[Any, Any]]
                The list of available tools for the task. The specific format of the tool is defined in `tooleval/evaluation/dataclass.py`
            answers : List[Dict]
                The list of answers for comparison.
            multisample : bool, optional
                Whether to use multisample to get the preference. If True, the function will return a list of preferences, otherwise return a single preference.
            sample_n : int, optional
                The number of samples to get the preference.

        Returns:
        -------
            preference : Union[List[int], int]
                The index of the preferred answer. If `multisample` is True, return a list of preferences, otherwise return a single preference.
        
        Raise:
        -----
        
        """
        answers_processed = [process_answer(ans) for ans in answers]
        available_tools = process_tools(available_tools)
        
        def shuffle_run() -> int:
            indexs = list(range(len(answers_processed)))
            random.shuffle(indexs)
            
            answers_projected = [answers[idx] for idx in indexs]
            
            preferred_index = self.fn_completions(
                {
                    'query':query,
                    'available_tools':available_tools,
                },
                answers_projected,
                task_status,
                answer_statuss
            )
            if preferred_index in indexs:
                return indexs.index(preferred_index)
            raise ValueError(f'Preferred index {preferred_index} is invalid!')
        
        if not multisample:
            return shuffle_run()
        else:
            prefers = [shuffle_run() for _ in range(sample_n)]
            return prefers

@register_evaluator
class ToolEvalEvaluator(BaseEvaluator):
    """ToolEval common evaluator class.
    
    Attributes:
    ----------
        cfg_path : str
            A path store the configuration of the evaluator.  

        
    """
    def __init__(self,
                 cfg_path: str = None,
                ):
        eval_config = yaml.load(open(os.path.join(cfg_path,'config.yaml')),Loader=yaml.FullLoader)
        template = open(os.path.join(cfg_path,eval_config['prompt_template'])).read()
        
        super().__init__(
            fn_completions=getattr(self,eval_config['fn_completions'])
            )
        self.eval_config = eval_config
        self.template = template