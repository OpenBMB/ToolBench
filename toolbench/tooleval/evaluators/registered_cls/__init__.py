from .base import BaseEvaluator
from .utils import register_evaluator,get_evaluator_cls

__all__ = ['register_evaluator','get_evaluator_cls','BaseEvaluator']

import os
import importlib
current_dir = os.path.dirname(__file__)

for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)
    
    if os.path.isfile(item_path) and item != '__init__.py' and item.endswith('.py'):
        module_name = item[:-3]
        
        full_module_path = f"{__name__}.{module_name}"
        
        imported_module = importlib.import_module(full_module_path)
        
        globals()[module_name] = imported_module
