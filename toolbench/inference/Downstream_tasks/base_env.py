class base_env:

    def __init__(self):
        self.task_description = ""
        self.input_description = ""
        self.tool_names = []
        self.functions = []

    def restart(self):
        '''
        Restrat the environment
        '''
        raise NotImplementedError
    
    def get_score(self):
        '''
        Get the value of the current state
        A fake function, used to search in oracle mode, which is not actually used (and impossible to obtain)
        '''
        raise NotImplementedError

    def step(self, action, input_str):
        '''
        Perform an interaction in natural language mode
        return value (output str, status code)
        '''
        raise NotImplementedError
    
    def check_success(self):
        '''
        Returns 1 if successful, otherwise returns 0
        '''
        raise NotImplementedError
    
    def to_json(self):
        raise NotImplementedError