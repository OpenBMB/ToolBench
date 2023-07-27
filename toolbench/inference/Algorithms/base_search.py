class base_search_method:

    def __init__(self):
        pass

    def to_json(self):
        '''
        "answer_generation": {
            "valid_data": bool,
            "final_answer": string,
            "chain": [
                {
                    "thought":string,
                    "action_name":string,
                    "action_input":string,
                    "observation": string,
                }
            ],
        }
        as answer data
        '''
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

