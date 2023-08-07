from .base import BaseEvaluator
from .utils import register_evaluator,get_evaluator_cls
from .example import ToolEvalEvaluator,OpenAIEvaluator,OpenAINormalizedEvaluator

__all__=['register_evaluator','get_evaluator_cls','BaseEvaluator','ToolEvalEvaluator','OpenAINormalizedEvaluator','load_registered_automatic_evaluator']



def load_registered_automatic_evaluator(config:dict={},evaluator_name=None,evaluators_cfg_path=None)->BaseEvaluator:
    import os
    import yaml
    
    evaluator_name = config['evaluator'] if evaluator_name is None else evaluator_name
    cfg_path = config['evaluators_cfg_path'] if evaluators_cfg_path is None else evaluators_cfg_path
    cfg_path = os.path.join(cfg_path,evaluator_name)
    
    cls_name = yaml.load(open(os.path.join(cfg_path,'config.yaml')),Loader=yaml.FullLoader)['registered_cls_name']
    
    evaluator:BaseEvaluator = get_evaluator_cls(cls_name)(cfg_path)
    return evaluator