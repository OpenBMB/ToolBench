import os
import re
import json
import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--answer_dir',type=str, required=True,help='where the answers stored.')

if __name__=='__main__':
    args = parser.parse_args()
    input_dir = args.answer_dir
    test_count = "100"
    method2result = {}
    method2querycount = {}

    def get_size(node):
        size = 1
        if len(node["children"]) == 0:
            node["size"] = size
            return size
        else:
            for child in node["children"]:
                size += get_size(child)
            node["size"] = size
            return size
    def get_leaf_node_count(node):
        '''
        返回值：叶子节点数，最大Elo积分，总子节点树，Thought节点数, 选择最左数量，选择后几个数量
        '''
        thought_count = (1 if node["node_type"] == "Thought" else 0)
        if len(node["children"]) == 0:
            return (1 if node["expand_num"] != 0 else 0), node["Elo"], 1, thought_count
        else:
            result = 0
            max_elo = -1e7
            node_count = 1
            for child in node["children"]:
                child_left_node_count, child_max_elo, child_node_count, child_thought_count = get_leaf_node_count(child)
                result += child_left_node_count
                node_count += child_node_count
                thought_count += child_thought_count
                max_elo = max(max_elo,child_max_elo)
            return result, max_elo, node_count, thought_count

    def recursive_get_error_code(obj):
        result = []
        if type(obj) == dict:
            for key,value in obj.items():
                if key == "observation_code":
                    assert type(value) == int
                    # assert "observation" in obj.keys()
                    if "observation" in obj.keys() and "html" in str(obj["observation"]).lower():
                        result = result + ["html"]
                    else:
                        result = result + [value]

                    # if value == -1:
                    #     print(obj["description"])

                elif key == "description":
                    if "OpenAI service is unavailable" in value:
                        result = result + ["openai"]
                        # print("hello")
                else:
                    # print(f"in {key}")
                    result = result + recursive_get_error_code(value)
        elif type(obj) == list:
            for cont in obj:
                result = result + recursive_get_error_code(cont)
        return result


    def check_real_valid(string):
        fake_true_vocab = ["sorry","apologize","apology","unfortunately","couldn't"]
        for word in fake_true_vocab:
            if word in string.lower():
                return False
        return True

    for file in os.listdir(input_dir):
        if "result" in file:
            continue
        pattern = r"(\d+)_([^_]+)_(.+)\.json"
        re_result = re.match(pattern,file)
        if re_result == None or "DFS" in (re_result.group(3) + "_" + re_result.group(2)):
            pattern2 = r"(\d+)_(.+)\.json"
            re_result = re.match(pattern2,file)
            idx = re_result.group(1)
            method = re_result.group(2)
        else:
            idx = int(re_result.group(1))
            method = re_result.group(3) + "_" + re_result.group(2)

        if method2result.get(method,-1) == -1:
            method2result[method] = {
                "total_count": 0,
                "pass_at_acc": [0,0.0],
                "best_answer_acc": [0,0.0],
                "best_answer_is_real_valid": [],
                "query_count": [],
                "average_token_usage": [],
                "fake_valid": [0,0.0],
                "thought_node_rate": [],
                "give_answer_rate": [],
                "root/max_Elo": [],
                "valid_per_data": [],
                "vote_to_the_first_node": [],
                "hallucination_name": [0,0.0],
                "hallucination_name_error": [0,0.0],
                "valid_observation_count": [],
                "valid_answer_count": [],
                "leaf_node_count": [],
                "max_query_count_stopping": [0,0.0],
                "html_in_response": [0,0.0],
                "html_in_response_error": [0,0.0],
                "openai_llm_bug": [0,0.0],
                "give_up_and_restart": [0,0.0],
                "\"error\" in response": [0,0.0],
                "other_error": [0,0.0],
            }
        if method2querycount.get(method,-1) == -1:
            method2querycount[method] = []
        method2querycount[method].append(idx)
        
        reader =  open(os.path.join(input_dir,file),"r")
        try:
            json_data = json.load(reader)
        except:
            print(file)
            reader.close()
            continue
        reader.close()

        json_data["answer_generation"]["finish_type"] = "give_answer"
        if "CoT" in method or "Reflexion" in method:
            flatten_error_codes = recursive_get_error_code(json_data["trys"]) 
        else:
            flatten_error_codes = recursive_get_error_code(json_data["tree"])  
            get_size(json_data["tree"]["tree"])

        if -1 in flatten_error_codes:
            os.remove(os.path.join(input_dir,file))
            continue

        method2result[method]["total_count"] += 1
        method2result[method]["query_count"].append(json_data["answer_generation"]["query_count"]) #
        if "total_tokens" in json_data["answer_generation"].keys():
            method2result[method]["average_token_usage"].append(json_data["answer_generation"]["total_tokens"]) #


        if "CoT" in method or "Reflexion" in method:
            method2result[method]["leaf_node_count"].append(json_data["try_count"])
        else:
            leaf_node_count, max_elo, node_count, thought_count = get_leaf_node_count(json_data["tree"]["tree"])
            method2result[method]["leaf_node_count"].append(leaf_node_count)
            method2result[method]["thought_node_rate"].append(thought_count/node_count)
            # assert json_data["tree"]["tree"]["Elo"] >= 0, os.path.join(input_dir,file)
            if max_elo > 0:
                method2result[method]["root/max_Elo"].append(max_elo)
            else:
                method2result[method]["root/max_Elo"].append( max_elo)

        if "html" in flatten_error_codes: #html
            method2result[method]["html_in_response"][0] += 1
        if 1 in flatten_error_codes:
            method2result[method]["hallucination_name"][0] += 1
        if len(json_data["compare_candidates"]) > 0:
            method2result[method]["valid_answer_count"].append(len(json_data["compare_candidates"])) #
        
        if json_data["answer_generation"]["valid_data"] == True:
            if json_data["answer_generation"]["finish_type"] == "give_answer":
                method2result[method]["give_answer_rate"].append(1) #
            else:
                method2result[method]["give_answer_rate"].append(0) #

        valid = len(json_data["compare_candidates"]) > 0
        real_valid = False
        best_answer_real_valid = False

        for instance in json_data["compare_candidates"]: #只要有一个valid answer就算真阳
            assert instance[-1]["node_type"] == "Action Input", file
            real_valid = check_real_valid(instance[-1]["description"]) or real_valid #只要一个过，就算过
        
        if len(json_data["compare_candidates"]) > 0:
            best_id = -1
            max_elo = -1e7
            for k,cont in enumerate(json_data["compare_candidates"]):
                if cont[-1]["Elo"] > max_elo:
                    best_id = k
                    max_elo = cont[-1]["Elo"]

            best_answer_real_valid = check_real_valid(json_data["compare_candidates"][best_id][-1]["description"])
        if "ETS" in method:
            method2result[method]["valid_per_data"].append( 1 if best_answer_real_valid else 0 )
        else:
            method2result[method]["valid_per_data"].append( 1 if best_answer_real_valid else 0 )
        
        if best_answer_real_valid:
            method2result[method]["best_answer_acc"][0] += 1

        if valid and real_valid:
            method2result[method]["pass_at_acc"][0] += 1

            
            if json_data["answer_generation"]["valid_data"]:
                observation_length = 0
                for temp_node in json_data["answer_generation"]["train_messages"]:
                    assert temp_node[-1]["role"] == "assistant"
                    if "function_call" in temp_node[-1].keys():
                        observation_length += 1
                method2result[method]["valid_observation_count"].append(observation_length) #

        else: #生成失败
            if valid: # 假阳
                method2result[method]["fake_valid"][0] += 1

            # print(flatten_error_codes)
            if 1 in flatten_error_codes:
                method2result[method]["hallucination_name_error"][0] += 1

            if "forward_args" in json_data.keys() and "max_query_count" in json_data["forward_args"].keys() and json_data["forward_args"]["max_query_count"] <= json_data["answer_generation"]["query_count"]:
                method2result[method]["max_query_count_stopping"][0] += 1
            
            '''
            按错误的严重程度逐级判断
            '''
            if "html" in flatten_error_codes: #html
                method2result[method]["html_in_response_error"][0] += 1
            
            if -1 in flatten_error_codes: #接口挂了
                method2result[method]["openai_llm_bug"][0] += 1
            elif 4 in flatten_error_codes: #html
                method2result[method]["give_up_and_restart"][0] += 1
            elif 11 in flatten_error_codes: #error in message
                method2result[method]["\"error\" in response"][0] += 1
            else:
                method2result[method]["other_error"][0] += 1

        if valid and real_valid:
            method2result[method]["best_answer_is_real_valid"].append(1 if best_answer_real_valid else 0)

    for method in method2result.keys():
        for key,value in method2result[method].items():
            if key in ["valid_observation_count","query_count","leaf_node_count","thought_node_rate","valid_answer_count","average_token_usage","give_answer_rate","best_answer_is_real_valid","vote_to_the_first_node"]:
                method2result[method][key] = f"{np.mean(np.array(method2result[method][key])):.02f}"
            elif type(value) == list and len(value) == 2:
                method2result[method][key][1] = f"{method2result[method][key][0]*100 / method2result[method]['total_count']:.2f}\%"

    def classify_N(xs,yss,N):
        zip_value = list(zip(xs,yss[0]))
        zip_value.sort(key = lambda x: x[0])

        threshold =  []
        for i in range(N):
            threshold.append(zip_value[min(((i+1)*len(xs))//(N),len(zip_value)-1)][0])

        bucket = [[] for _ in range(N)]
        for cont in bucket:
            for i in range(len(yss)):
                cont.append([])
        for k,ys in enumerate(yss):
            for x,y in zip(xs,ys):
                for i in range(N):
                    if x < threshold[i]:
                        bucket[i][k].append(y)
                        break
        for i in range(len(bucket)):
            for k in range(len(bucket[i])):
                bucket[i][k] = np.mean(np.array(bucket[i][k]))
        return bucket

    def print_table(table):
        methods = list((table.keys()))
        methods.sort()
        column_names =  ["method"]+list(table[methods[0]].keys())
        for key in table.keys():
            table[key]["method"] = key

        key_length = {}
        for key in column_names:
            if key in ["root/max_Elo","valid_per_data"]:
                continue
            now_max = len(key)
            for method in methods:
                now_max = max(now_max, len(str(table[method][key])))
            key_length[key] = now_max
        
        for key in column_names:
            if key in ["root/max_Elo","valid_per_data"]:
                continue
            # print(key,end=" "*(key_length[key]- len(key))+"|")    

        mode = input_dir[len(input_dir[::-1][input_dir[::-1].find("/"):][::-1]):]
    
        for cnt, method in enumerate(methods):
            for cnt_key, key in enumerate(column_names):
                if key in ["root/max_Elo","valid_per_data"]:
                    continue
                if cnt == 0 and cnt_key == 0:
                    print(mode + "|" + str(table[method][key]),end=" "*(key_length[key]- len(str(table[method][key])))+"|")    
                else:
                    print(str(table[method][key]),end=" "*(key_length[key]- len(str(table[method][key])))+"|")    
            print("")

    print_table(method2result)
