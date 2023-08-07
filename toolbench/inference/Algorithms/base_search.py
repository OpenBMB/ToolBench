from Downstream_tasks.base_env import base_env

class base_search_method:
    """For the base tree search method, you need to support the following functions"""
    
    def __init__(self,llm,io_func: base_env, process_id=0, callbacks = None):
        """Args:
            llm: The interface of the LLM 
            io_func(base_env): Interface to the environment,
            process_id (int, optional): In multiprocessing annotation, this describes the process id. Defaults to 0.
            callbacks (_type_, optional): _description_. Defaults to None.
        """
        pass

    def to_json(self,answer=False,process=True):
        '''
        return a json object, 
        If "answer" = True. must have the following field to make answer annotation
        If "process" = True. You need provide the full information of the tree searching process

        "answer_generation": {
            "valid_data": bool,
            "final_answer": string,
            "finish_type": enum["give_up","give_answer"]
            "train_messages": [ [openAI-message] ],
        }
        '''
        raise NotImplementedError

    def start(self, **args):
        """This is the entry point of the searching process"""
        raise NotImplementedError

