from .evaluator import AutomaticEvaluator

def load_automatic_evaluator(config:dict={},evaluator_name=None,evaluators_cfg_path=None)->AutomaticEvaluator:
    import os
    import yaml
        
    evaluator_name = config['evaluator'] if evaluator_name is None else evaluator_name
    cfg_path = config['evaluators_cfg_path'] if evaluators_cfg_path is None else evaluators_cfg_path
    config_path = os.path.join(cfg_path,evaluator_name)
    eval_config = yaml.load(open(os.path.join(config_path,'config.yaml')),Loader=yaml.FullLoader)[evaluator_name]
    template = open(os.path.join(config_path,eval_config['prompt_template'])).read()
    evaluator = AutomaticEvaluator(eval_config,template)
    return evaluator