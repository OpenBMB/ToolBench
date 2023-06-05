import json
import requests
import yaml
import argparse
from langchain import LLMChain
from langchain.agents import ZeroShotAgent, AgentExecutor
from bmtools.agent.apitool import RequestTool
from bmtools.agent.executor import Executor
from bmtools import get_logger
from bmtools.models.llama_model import LlamaModel
from bmtools.models.lora_model import LoraModel

logger = get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--tool_name', type=str, default="weather", required=True, help='tool name')
parser.add_argument('--model_path', type=str, default="your_model_path/", required=True, help='tool-llama model path')
parser.add_argument('--lora_path', type=str, default="", required=False, help='tool-llama lora model path')
args = parser.parse_args()


# basically copy the codes in BMTools/bmtools/agent/singletool.py
def import_all_apis(tool_json):
    '''import all apis that is a tool
    '''
    doc_url = tool_json['api']['url']
    response = requests.get(doc_url)

    logger.info("Doc string URL: {}".format(doc_url))
    if doc_url.endswith('yaml') or doc_url.endswith('yml'):
        plugin = yaml.safe_load(response.text)
    else:
        plugin = json.loads(response.text)

    server_url = plugin['servers'][0]['url']
    if server_url.startswith("/"):
        server_url = "http://127.0.0.1:8079" + server_url
    logger.info("server_url {}".format(server_url))
    all_apis = []
    for key in plugin['paths']:
        value = plugin['paths'][key]
        api = RequestTool(root_url=server_url, func_url=key, method='get', request_info=value)
        all_apis.append(api)
    return all_apis


def load_single_tools(tool_name, tool_url):
    get_url = tool_url +".well-known/ai-plugin.json"
    response = requests.get(get_url)
    if response.status_code == 200:
        tool_config_json = response.json()
    else:
        raise RuntimeError("Your URL of the tool is invalid.")
    return tool_name, tool_config_json


class STQuestionAnswerer:
    def __init__(self, stream_output=False, llm_model=None):
        self.llm = llm_model
        self.stream_output = stream_output

    def load_tools(self, name, meta_info, prompt_type="react-with-tool-description", return_intermediate_steps=True):

        self.all_tools_map = {}
        self.all_tools_map[name] = import_all_apis(meta_info)
        
        logger.info("Tool [{}] has the following apis: {}".format(name, self.all_tools_map[name]))

        tool_str = "; ".join([t.name for t in self.all_tools_map[name]])
        prefix = f"""Answer the following questions as best you can. Specifically, you have access to the following APIs:"""
        suffix = """Begin! Remember: (1) Follow the format, i.e,\nThought:\nAction:\nAction Input:\nObservation:\nFinal Answer:\n (2) Provide as much as useful information in your Final Answer. (3) Do not make up anything, and if your Observation has no link, DO NOT hallucihate one. (4) If you have enough information and want to stop the process, please use \nThought: I have got enough information\nFinal Answer: **your response. \n The Action: MUST be one of the following:""" + tool_str + """\nQuestion: {input}\n Agent scratchpad (history actions):\n {agent_scratchpad}"""
        format_instructions = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times, max 7 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""
        prompt = ZeroShotAgent.create_prompt(
            self.all_tools_map[name], 
            prefix=prefix, 
            suffix=suffix, 
            format_instructions=format_instructions,
            input_variables=["input", "agent_scratchpad"]
        )
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        logger.info("Full prompt template: {}".format(prompt.template))
        tool_names = [tool.name for tool in self.all_tools_map[name] ]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
        if self.stream_output:
            agent_executor = Executor.from_agent_and_tools(agent=agent, tools=self.all_tools_map[name] , verbose=True, return_intermediate_steps=return_intermediate_steps)
        else:
            agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.all_tools_map[name], verbose=True, return_intermediate_steps=return_intermediate_steps)
        return agent_executor
        
    
def main():
    NAME2URL = {
        'weather':  "http://127.0.0.1:8079/tools/weather/"
    }
    if args.tool_name not in NAME2URL:
        tool_url = f"http://127.0.0.1:8079/tools/{args.tool_name}/"
    else:
        tool_url = NAME2URL[args.tool_name]
    tools_name, tools_config = load_single_tools(args.tool_name, tool_url)
    if args.lora_path == "":
        customllm = LlamaModel(args.model_path)
    else:
        customllm = LoraModel(base_name_or_path=args.model_path, model_name_or_path=args.lora_path)
    qa =  STQuestionAnswerer(llm_model=customllm)
    agent = qa.load_tools(tools_name, tools_config)
    
    while True:
        query = input("Input your query: ")
        output = agent(inputs=query)
        # print(output)

if __name__=='__main__':
    main()