from termcolor import colored
import numpy as np
from copy import deepcopy
from utils import softmax_bias
import math

class my_tree:
    def __init__(self):
        self.root = tree_node()
        self.now_deal_node = self.root

    def get_former_trice(self,start_node,target_node,valid_types=["Thought","Action","Action Input","Observation"]):
        '''
        Get all operations from start_node node to target_node node, including target_node itself and start_node
        '''
        node = target_node
        now_str = ""
        while node != self.root and node != start_node.father:
            node_info = ""
            if node.node_type in valid_types:
                node_info = node_info + f"{node.node_type}: {node.description}\n"
            if node.observation != "" and "Observation" in valid_types:
                node_info = node_info + f"Observation: {node.observation}\n"
            now_str = node_info + now_str

            node = node.father
        
        return now_str

    def add_child(self,new_node):
        '''
        Add child nodes to the currently processed node
        '''
        new_node.father = self.now_deal_node
        self.now_deal_node.children.append(new_node)
        self.now_deal_node = new_node

    def backup(self):
        self.now_deal_node = self.now_deal_node.father


    def to_json_recursive(self,use_messages=False):
        tree_structure =  self.root.to_json_recursive(use_messages=use_messages)
        js_obj = {
            "size": self.root.get_size(),
            "max_length":self.root.get_max_depth(),
            "tree": tree_structure,
        }
        return js_obj

    def chain_tree_to_json(self):
        json_obj = []
        now_node = self.root
        while True:

            
            json_obj.append(now_node.to_json())

            
            if now_node.children != []:
                assert len(now_node.children) == 1
                now_node = now_node.children[0]
            else:
                break
        return json_obj
    
    def chain_tree_to_str(self):
        now_prefix = ""
        json_obj = self.chain_tree_to_json()
        for k,ins in enumerate(json_obj):
            if k != 0:
                now_prefix += f"\n{ins['node_type']}: "
            now_prefix += f"{ins['description']}"
            if 'observation' in ins.keys():
                now_prefix += f"\nObservation: {ins['description']}"
        return now_prefix


    @classmethod
    def from_chain_tree_json(self, js_obj):
        tree = my_tree()
        for k, ins in enumerate(js_obj):
            temp_node = tree_node.from_json(ins)
            if k == 0:
                tree.root = temp_node
                tree.now_deal_node = tree.root
            else:
                tree.add_child(temp_node)

        return tree
    
    def balence_Elo(self,temperature):
        '''
        Recalculate the Elo points for all nodes in the tree
        '''
        return self.root.compute_Elo(temperature)
    

class tree_node:

    def __init__(self):
        self.is_terminal = False
        self.pruned = False
        self.finished = False

        self.node_type = None
        self.description = ""
        self.observation = ""
        self.observation_code = None
        self.children = []

        self.father = None


        self.io_state = None

        self.reflection = []
        self.generated_reflection = ""

        self.expand_num = 0 # The number of visits to the node, 0 means it has not been visited


        '''
        UCT
        '''
        self.values = []
        self.vote_counts = []


        '''
        ETS
        '''
        self.Elo = 1000.0
        self.prior_score = 0
        self.matching_time = 0

        '''
        用于0613接口
        '''
        self.messages = []

    def compute_weight(self):
        '''
        Used in the UCT algorithm to calculate the node weight of each son during selection
        '''
        if self.pruned:
            return -10000
        
        if len(self.values) == 0:
            return 0.0
        else:
            return np.mean(np.array(self.values))
        
    def compute_Elo(self,temperature):
        '''
        A recursive algorithm. In theory, call the compute_Elo of the parent node, and the Elo of all subtrees should be calculated.
        '''
        if len(self.children) == 1:
            child_Elo = self.children[0].compute_Elo(temperature)
            self.Elo = float(child_Elo)
        elif len(self.children) > 1:
            for child in self.children:
                _ = child.compute_Elo(temperature)
            weights = [child.Elo for child in self.children]
            
            match_decrease = 1/ (math.ln(self.matching_time + 1))

            weights = softmax_bias(weights,temperature*match_decrease)
            elo = 0.0
            for weight,child in zip(weights,self.children):
                elo += (weight * child.Elo)
            self.Elo = float(elo)
        elif self.expand_num == 0:
            return 0.0

        return self.Elo

    def init_Elo(self):
        '''
            To give an initial score to newly added nodes:
            final_answer, does not include apologize: +100
            final_answer: +50
            give_up: unchanged
            Extra long: -50
        '''
        return 
        
    def randomly_select_to_terminal_node(self,temperature=1.0):
        if len(self.children) == 0:
            return self
        elif len(self.children) == 1:
            return self.children[0].randomly_select_to_terminal_node()
        else:
            elos = [-10000 if (child.expand_num == 0 or child.finished) else child.Elo for child in self.children]
            match_decrease = 1 / (math.ln(self.matching_time + 1))
            weights = softmax_bias(elos,temperature*match_decrease)
            result = np.random.multinomial(1,weights)
            return self.children[result].randomly_select_to_terminal_node()

    def get_max_depth(self):
        '''
        maximum depth of subtrees including self
        '''
        max_depth = 0
        for child in self.children:
            max_depth = max(max_depth,child.get_max_depth())
        return max_depth + 1

    def get_depth(self):
        if self.father == None:
            return 0
        return self.father.get_depth() + 1

    def get_size(self):
        '''
        subtree, including itself
        '''
        size = 1
        for child in self.children:
            size += child.get_size()
        return size
    
    def prune(self):
        '''
        pruning off the subtree
        '''
        self.pruned = True
        for child in self.children:
            child.prune()

    def print(self,process_id = 0):
        if process_id != 0:
            return
        color_converter = {"Thought":"red", "Action": "blue", "Action Input": "cyan","Final Answer": "green","Reflection":"blue"}
        print(colored(f"{self.node_type}: {self.description}",color = color_converter[self.node_type]))
        if self.observation != "":
            if len(self.observation) < 1536:
                print(colored(f"Observation: {self.observation}",color="yellow"))
            else:
                print(colored(f"Observation: {self.observation[:1536]}......(len={len(self.observation)})",color="yellow"))


    @classmethod
    def find_ancestor_intersection(cls, node1, node2):
        '''
        find the first common ancestor
        '''
        if node1 == None or node2 == None:
            return None
        if node1 == node2:
            return node1
        length1 = node1.get_depth()
        length2 = node2.get_depth()
        if length1 > length2:
            return tree_node.find_ancestor_intersection(node1.father,node2)
        else:
            return tree_node.find_ancestor_intersection(node1, node2.father)

    @classmethod
    def from_json(self,json_obj):
        node = tree_node()
        node.is_terminal = json_obj["is_terminal"]
        node.node_type = json_obj["node_type"]
        node.description = json_obj["description"]
        if "observation" in json_obj.keys():
            node.observation = json_obj["observation"]
        return node
    
    def have_brother(self):
        if self.father == None:
            return False
        return len(self.father.children) > 1

    def to_json_recursive(self,use_messages=False):
        js_obj = self.to_json(use_messages=use_messages)
        js_obj["children"] = []
        for child in self.children:
            js_obj["children"].append(child.to_json_recursive())
        return js_obj


    def make_finish(self,inter_val=1):
        '''
        Recursively marked as finish, until the above inter_val nodes of action_input type (including yourself)
        '''
        self.finished = True
        if self.node_type == "Action Input":
            inter_val -= 1
        if self.father != None and inter_val >= 0:
            self.father.make_finish(inter_val)


    def get_train_messages_from_this_node(self):
        '''
        Returns chained results, starting from this node up to the root node
        '''
        def sift_first_invalid_message(messages):
            use_messages = []
            flag = True
            for message_id in range(len(messages))[::-1]:
                if not ("valid" in messages[message_id].keys() and messages[message_id]["valid"] == False):
                    use_messages = [messages[message_id]] + use_messages
                elif flag:
                    flag = False
                    use_messages = [messages[message_id]] + use_messages
            return use_messages

        now_node = self
        result = []
        while now_node.father != None:
            if now_node.node_type == "Action Input":
                use_messages = deepcopy(now_node.messages)
                while use_messages[-1]["role"] != "assistant":
                    use_messages = use_messages[:-1]
                use_messages = sift_first_invalid_message(use_messages)
                result = [use_messages] + result
            elif now_node.node_type == "Thought":
                use_messages = deepcopy(now_node.messages)
                while use_messages[-1]["role"] == "user":
                    use_messages = use_messages[:-1]
                use_messages = sift_first_invalid_message(use_messages)
                if use_messages[-1]["role"] == "assistant":
                    result = [use_messages] + result
            now_node = now_node.father
        return result

    def get_chain_result_from_this_node(self,use_messages=False):
        '''
        Returns chained results, starting from this node up to the root node
        '''
        now_node = self
        result = []
        while now_node.father != None:
            result = [now_node.to_json(use_messages=use_messages)] + result
            now_node = now_node.father
        return result

    def get_former_trice_from_this_node(self,valid_types=["Thought","Action","Action Input","Observation"],end_node = None):
        '''
        Return path description from end_node -> self
        Does not contain end_node, never contains root node
        '''
        node = self
        output_str_list = []

        while node != end_node and node.father != None:
            now_node_des_list = []
            if node.node_type in valid_types:
                now_node_des_list.append(f"{node.node_type}: {node.description}\n")
            if node.observation != "" and "Observation" in valid_types:
                tuncated = node.observation
                if len(node.observation) > 1024:
                    tuncated = node.observation[:1024] + f"...(len={len(node.observation)})"
                now_node_des_list.append(f"Observation: {tuncated}\n")
            output_str_list = now_node_des_list + output_str_list
            node = node.father
        
        now_str = ""
        for k, cont in enumerate(output_str_list):
            now_str += f"step_{k+1}: {cont}\n"

        if now_str == "":
            now_str = "None"
        return now_str

    def to_json(self, use_messages=False):
        
        json_obj = {}
        json_obj["is_terminal"] = False
        json_obj["pruned"] = self.pruned
        json_obj["finished"] = self.finished

        json_obj["depth"] = self.get_depth()
        json_obj["node_type"] = self.node_type
        json_obj["description"] = self.description
        json_obj["Elo"] = self.Elo
        json_obj["matching_time"] = self.matching_time
        if self.observation != "":
            json_obj["observation"] = self.observation
        if self.observation_code != None:
            json_obj["observation_code"] = self.observation_code
        json_obj["child_count"] = len(self.children)
        json_obj["expand_num"] = self.expand_num

        if self.io_state != None and self.node_type == "Action Input":
            json_obj["io_state"] = self.io_state.to_json()

        if self.reflection != []:
            json_obj["reflection"] = self.reflection
        if self.generated_reflection != "":
            json_obj["generated_reflection"] = self.generated_reflection
        if self.values != []:
            json_obj["mean_value"] = np.mean(np.array(self.values))
            json_obj["mean_votes"] = np.mean(np.array(self.vote_counts))
            
        if use_messages:
            json_obj["messages"] = []
            for message in self.messages:
                if not ("valid" in message.keys() and message["valid"] == False):
                    json_obj["messages"].append(message["role"])
                else:
                    json_obj["messages"].append(message["role"] + "_invalid")

        return json_obj

    def describe_children(self):
        assert self.node_type == "Action Input"
        assert len(self.children) > 0
        des_str = ""
        for i in range(min(len(self.children),10)):
            thought_node = self.children[i]
            temp_str = f"<former_attempt_{i+1}>\nThought: {thought_node.description}\n"
            if len(thought_node.children) > 0:
                action_node = thought_node.children[0]
                temp_str = temp_str + f"Action: {action_node.description}\n"
                if len(action_node.children) > 0:
                    action_input_node = action_node.children[0]
                    temp_str = temp_str + f"Action Input: {action_input_node.description}\nObservation: {action_input_node.observation}\n"
            des_str = des_str + temp_str

        return des_str