"""
Data preprocessing
"""
import argparse
import json
import os
import random
from toolbench.utils import process_system_message
random.seed(0)
parser = argparse.ArgumentParser()
parser.add_argument('--tool_data_dir', type=str, default="", required=True, help='Original tool data path.')
parser.add_argument('--output_file', type=str, default="", required=True, help='Preprocessed tool data output path.')
parser.add_argument('--method', type=str, default="DFS_woFilter_w2", choices=["CoT@1", "DFS_woFilter_w2"], required=False, help='The method of data.')


def preprocess_rapidapi(tool_data_dir, method, output_file):
    def process_assistant_reply(message_dict: dict) -> str:
        content = message_dict["content"]
        if "function_call" in message_dict:
            function_call = message_dict["function_call"]
            reply = function_call # the whole dict containing action name and action input as target.
        elif content is not None:
            reply = content
        else:
            print(f"Wrong assistant reply: {message_dict}")
            return ""
        return reply

    def append_list(instances_list: list) -> list:
        return_list = []
        for instances in instances_list:
            return_list.extend(instances)
        return return_list

    print(f"Preprocessing data from {tool_data_dir} into {output_file}")
    out_list = []
    for data_file in os.listdir(os.path.join(tool_data_dir)):
        tmp_instances = []
        if method not in data_file:
            continue
        data_dict = json.load(open(os.path.join(tool_data_dir, data_file), "r"))
        answer_generation = data_dict["answer_generation"]
        is_valid = answer_generation["valid_data"]
        if not is_valid:
            continue
        train_messages = answer_generation["train_messages"]
        query = answer_generation["query"]
        functions = answer_generation["function"]
        for train_message in train_messages:
            conversations = []
            cur_react = ""
            for message_id, message_dict in enumerate(train_message):
                role = message_dict["role"]
                content = message_dict["content"]
                if role == "assistant":
                    inputs = process_assistant_reply(message_dict) 
                    
                    # process the last assistant message as target
                    if message_id + 1 == len(train_message):
                        if "function_call" not in message_dict:
                            cur_react = ""
                            break
                        else:
                            if cur_react == "":
                                cur_react += "\nThought: "
                            action = inputs["name"]
                            action_input = inputs["arguments"]
                            cur_react += f"\nAction: {action}"
                            cur_react += f"\nAction Input: {action_input}"
                            conversations.append({
                                "from": role,
                                "value": cur_react
                            })
                            cur_react = ""
                        tmp_dict = {
                            "id": f"Step {str(message_id)}: {query}",
                            "conversations":conversations
                        }
                        tmp_instances.append(tmp_dict)      
                        break

                    # process the former assistant messages into history conversations
                    else:
                        if "function_call" not in message_dict:
                            cur_react += f"\nThought: {inputs}"
                            continue
                        else:
                            if cur_react == "":
                                cur_react += "\nThought: "
                            action = inputs["name"]
                            action_input = inputs["arguments"]
                            cur_react += f"\nAction: {action}"
                            cur_react += f"\nAction Input: {action_input}"
                            conversations.append({
                                "from": role,
                                "value": cur_react
                            })
                            cur_react = ""
                else:
                    if role == "system":
                        inputs = process_system_message(content, functions)
                    else:
                        inputs = content
                    conversations.append({
                        "from": role,
                        "value": inputs
                    })
                    cur_react = ""
        out_list.append(tmp_instances)
    out_list = append_list(out_list)
    json.dump(out_list, open(output_file,"w"), indent=4, ensure_ascii=False)  
    print("Preprocessing done.")
        
if __name__=='__main__':
    args = parser.parse_args()
    preprocess_rapidapi(args.tool_data_dir, args.method, args.output_file)
    
