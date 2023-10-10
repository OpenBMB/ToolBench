"""
Utils for tooleval.
"""
from evaluation import ExecutionGraph,ExecutionNode
import random
random.seed(42)
from evaluators.registered_cls.rtl import AnswerStatus, TaskStatus

task_status_mapping = {
    "TaskStatus.Solvable": TaskStatus.Solvable,
    "TaskStatus.Unsolvable": TaskStatus.Unsolvable,
    "TaskStatus.Unsure": TaskStatus.Unsure
}
answer_status_mapping = {
    "AnswerStatus.Solved": AnswerStatus.Solved,
    "AnswerStatus.Unsolved": AnswerStatus.Unsolved,
    "AnswerStatus.Unsure": AnswerStatus.Unsure
}
test_sets = ["G1_instruction", "G1_category", "G1_tool", "G2_instruction", "G2_category", "G3_instruction"]

def get_steps(example):
    answer_details = example["answer"]["answer_details"][0]
    answer_steps = []
    step_cnt = 1
    final_step = ""

    while "next" in answer_details:
        answer_str = answer_details["message"]
        role_str = answer_details["role"]

        if answer_str and role_str == "tool":
            step_text = f"Step {step_cnt}: {answer_str}"
            answer_steps.append(step_text)
            final_step = f"Final step: {answer_str}"
            step_cnt += 1

        if not answer_details["next"]:
            break

        answer_details = answer_details["next"][0]

    return "\n".join(answer_steps), final_step


def generate_init_message_node(eg:ExecutionGraph,functions,query):
    init_node = ExecutionNode(role='system', message="You are AutoGPT, you can use many tools(functions) to do the following task.\nFirst I will give you the task description, and your task start.\nAt each step, you need to give your thought to analyze the status now and what to do next, with a function call to actually excute your step.\nAfter the call, you will get the call result, and you are now in a new state.\nThen you will analyze your status now, then decide what to do next...\nAfter many (Thought-call) pairs, you finally perform the task, then you can give your finial answer.\nRemember: \n1.the state change is irreversible, you can't go back to one of the former state, if you want to restart the task, say \"I give up and restart\".\n2.All the thought is short, at most in 5 sentence.\n3.You can do more then one trys, so if your plan is to continusly try some conditions, you can do one of the conditions per try.\nLet's Begin!\nTask description: You should use functions to help handle the real time user querys. Remember to ALWAYS call \"Finish\" function at the end of the task. And the final answer should contain enough information to show to the user.\nSpecifically, you have access to the following functions: " + str(functions))
    eg.set_init_node(init_node)
    
    node = ExecutionNode(role='user', message=query)
    eg.add_node(node)
    eg[init_node,node] = None
    return node

def process_valid_data(method,answer_generation):
    conversation = answer_generation['train_messages'][-1]
    functions = answer_generation['function']
    query = answer_generation['query']
    eg = ExecutionGraph()
    last_node = generate_init_message_node(eg,functions,query)
    
    index = 2
    while index < len(conversation):
        message = conversation[index]
        role = message['role']
        if role == 'system' or role == 'user' or role == 'function':
            index = index + 1
            continue
        elif role == 'assistant':
            if 'function_call' in message :
                node = ExecutionNode(role='tool', message={
                    'name':message['function_call']['name'],
                    'arguments':message['function_call']['arguments'],
                    'response':conversation[index+1]['content'] if message['function_call']['name']!='Finish' else ''
                    })
                index = index + 1
            else:
                node = ExecutionNode(role='assistant',
                                        message=message['content'])
                
        else:
            raise NotImplementedError(f'Unkown role {role}')
        
        index = index + 1
        eg.add_node(node)
        eg[last_node,node] = None
        last_node = node
    
    eg = eg.reduce_graph_to_sequence()
    
    return {
        'query':query,
        'available_tools':functions,
        'answer':{
            'method':method,
            'total_steps': eg.node_count,
            'final_answer': answer_generation['final_answer'],
            'answer_details': eg.convert_to_dict()
        }
    }

def process_invalid_data(method,data_dict):
    answer_generation = data_dict['answer_generation']
    functions = answer_generation['function']
    query = answer_generation['query']
    eg = ExecutionGraph()
    last_node = generate_init_message_node(eg,functions,query)
    if 'CoT' in method:
        trail = random.choice(data_dict["trys"])
        index = 0
        while index < len(trail['chain']):
            message = trail['chain'][index]
            if message['node_type'] == 'Action':
                node = ExecutionNode(role='tool', message={
                    'name':message['description'],
                    'arguments':(trail['chain'][index+1]['description']),
                    'response':(trail['chain'][index+1]['observation'])})
            
                index = index + 1
            elif message['node_type'] == 'Thought':
                node = ExecutionNode(role='assistant',
                                        message=message['description'])
            else:
                raise NotImplementedError(f"Unknown node_type: {message['node_type']}")
            index = index + 1

            eg.add_node(node)
            eg[last_node,node] = None
            last_node = node
        eg = eg.reduce_graph_to_sequence()
   
    elif 'DFS' in method:

        def DFS(root):
            if len(root['children']) == 0:
                node = ExecutionNode(role=root['node_type'],message=root)
                eg.add_node(node)
                return node
            else:
                child_nodes = [DFS(node) for node in root['children']]
                root['children'] = None
                root_node = ExecutionNode(role=root['node_type'],message=root)
                eg.add_node(root_node)
                for child_node in child_nodes:
                    eg.add_edge(root_node,child_node)
                return root_node
        for node in data_dict['tree']['tree']['children']:
            eg[last_node,DFS(node)] = None

        
        # purify the graph
        def purify_graph(node:ExecutionNode):
            if node.role == 'Action':
                adj_nodes = eg.get_adjacent_node(node)
                for adj_node in adj_nodes:
                    adj_node = eg[adj_node]
                    if adj_node.role == 'Action Input':
                        node.role = 'tool'
                        node.message = {
                            'name':node.message['description'],
                            'arguments':(adj_node.message['description']),
                            'response':(adj_node.message['observation'])
                            
                        }
                        # remove adj_node
                        adj_node = eg.pop_node(adj_node)
                        to_nodes = eg.edges.pop(adj_node.node_id,{})
                        eg.edges[node.node_id].update(to_nodes)
                        eg.edges[node.node_id].pop(adj_node.node_id)
                        node.out_degree += len(to_nodes)
                        break
            elif node.role == 'Thought':
                node.role = 'assistant'
                node.message = node.message['description']
            elif node.role == 'Action Input':
                print('Founding Extra Action Input Node')
                pass
            elif node.role =='system' or node.role=='user':
                pass
            else:
                raise Exception('Unknown role {}'.format(node.role))
            adj_nodes = eg.get_adjacent_node(node)
            for adj_node in adj_nodes:
                purify_graph(eg[adj_node])
            
        purify_graph(last_node)
        eg = eg.reduce_graph_to_sequence()
    else:
        raise NotImplementedError(f'Unknown method {method}')
    return {
        'query':query,
        'available_tools':functions,
        'answer':{
            'method':method,
            'total_steps': eg.node_count,
            'final_answer': answer_generation['final_answer'],
            'answer_details': eg.convert_to_dict()
        }
    }
