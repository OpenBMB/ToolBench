#!/usr/bin/env python
# coding=utf-8
import time
from termcolor import colored
from typing import Optional, List
from peft import PeftModel
import torch
from typing import Optional
import torch
from transformers import (
    AutoTokenizer,
    LlamaForCausalLM,
)
from toolbench.utils import process_system_message
from toolbench.model.model_adapter import get_conversation_template
from toolbench.inference.utils import SimpleChatIO, generate_stream, react_parser


class ToolLLaMALoRA:
    def __init__(self, base_name_or_path: str, model_name_or_path: str, template:str="tool-llama-single-round", device: str="cuda", cpu_offloading: bool=False, load_8bit: bool=False) -> None:
        super().__init__()
        self.model_name = model_name_or_path
        self.template = template
        self.tokenizer = AutoTokenizer.from_pretrained(base_name_or_path, use_fast=False, model_max_length=8192, padding_side="right")
        model = LlamaForCausalLM.from_pretrained(
            base_name_or_path,
            load_in_8bit=load_8bit,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model = PeftModel.from_pretrained(
            model,
            model_name_or_path,
            torch_dtype=torch.float16,
        )
        self.tokenizer.pad_token = self.tokenizer.unk_token
        
        self.use_gpu = (True if device == "cuda" else False)
        if (device == "cuda" and not cpu_offloading) or device == "mps":
            self.model.to(device)
        self.chatio = SimpleChatIO()

    def prediction(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        gen_params = {
            "model": "",
            "prompt": prompt,
            "temperature": 0.5,
            "max_new_tokens": 512,
            "stop": "</s>",
            "stop_token_ids": None,
            "echo": False
        }
        generate_stream_func = generate_stream
        output_stream = generate_stream_func(self.model, self.tokenizer, gen_params, "cuda", 8192, force_generate=True)
        outputs = self.chatio.return_output(output_stream)
        prediction = outputs.strip()
        return prediction
        
    def add_message(self, message):
        self.conversation_history.append(message)

    def change_messages(self,messages):
        self.conversation_history = messages

    def display_conversation(self, detailed=False):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        print("before_print"+"*"*50)
        for message in self.conversation_history:
            print_obj = f"{message['role']}: {message['content']} "
            if "function_call" in message.keys():
                print_obj = print_obj + f"function_call: {message['function_call']}"
            print_obj += ""
            print(
                colored(
                    print_obj,
                    role_to_color[message["role"]],
                )
            )
        print("end_print"+"*"*50)

    def parse(self,functions,process_id,**args):
        conv = get_conversation_template(self.template)
        if self.template == "tool-llama":
            roles = {"human": conv.roles[0], "gpt": conv.roles[1]}
        elif self.template == "tool-llama-single-round" or self.template == "tool-llama-multi-rounds":
            roles = {"system": conv.roles[0], "user": conv.roles[1], "function": conv.roles[2], "assistant": conv.roles[3]}

        self.time = time.time()
        conversation_history = self.conversation_history
        prompt = ''
        prompt_parts = []
        for message in conversation_history:
            role = roles[message['role']]
            content = message['content']
            if role == "System" and functions != []:
                content = process_system_message(content, functions)
            prompt_parts.append(f"{role}: {content}")
        prompt = '\n'.join(prompt_parts) + "\nAssistant:\n"

        if functions != []:
            predictions = self.prediction(prompt)
        else:
            predictions = self.prediction(prompt)

        decoded_token_len = len(self.tokenizer(predictions))
        if process_id == 0:
            print(f"[process({process_id})]total tokens: {decoded_token_len}")
        
        # react format prediction
        thought, action, action_input = react_parser(predictions)
        message = {
            "role": "assistant",
            "content": thought,
            "function_call": {
                "name": action,
                "arguments": action_input
            }
        }
        return message, 0, decoded_token_len


if __name__ == "__main__":
    # can accept all huggingface LlamaModel family
    llm = ToolLLaMALoRA("decapoda-research/llama-7b-hf")
    messages = [
        {'role': 'system', 'content': '''You are AutoGPT, you can use many tools(functions) to do
the following task.\nFirst I will give you the task description, and your task start.\nAt each step, you need to give your thought to analyze the status now and what to do next, with a function call to actually excute your step.\nAfter the call, you will get the call result, and you are now in a new state.\nThen you will analyze your status now, then decide what to do next...\nAfter many (Thought-call) pairs, you finally perform the task, then you can give your finial answer.\nRemember: \n1.the state change is , you can\'t go
back to the former state, if you want to restart the task, say "I give up and restart".\n2.All the thought is short, at most in 5 sentence.\nLet\'s Begin!\nTask description: Use numbers and basic arithmetic operations (+ - * /) to obtain exactly one number=24. Each
step, you are only allowed to choose two of the left numbers to obtain a new number. For example, you can combine [3,13,9,7] as 7*9 - 3*13 = 24.\nRemember:\n1.all of the number must be used , and must be used ONCE. So Only when left numbers is exact 24, you will win. So you don\'t succeed when left number = [24, 5]. You succeed when left number = [24]. \n2.all the try takes exactly 3 steps, look
at the input format'''}, 
{'role': 'user', 'content': '\nThe real task input is: [1, 2, 4, 7]\nBegin!\n'}
]
    functions = [{'name': 'play_24', 'description': '''make your current conbine with the format "x operation y = z (left: aaa) " like "1+2=3, (left: 3 5 7)", then I will tell you whether you win. This is the ONLY way
to interact with the game, and the total process of a input use 3 steps of call, each step you can only combine 2 of the left numbers, so the count of left numbers decrease from 4 to 1''','parameters':{'type': 'object', 'properties':{}}}]#, 'parameters': {'type': 'object', 'properties': {'input': {'type': 'string', 'description': 'describe what number you want to conbine, and how to conbine.'}}, 'required': ['input']}}]

    llm.change_messages(messages)
    output = llm.parse(functions=functions)
    print(output)
