import argparse
import os
import requests
import faiss
from bmtools.agent.apitool import Tool
from bmtools.agent.singletool import STQuestionAnswerer
from bmtools import get_logger
from bmtools.models.llama_model import LlamaModel
from bmtools.models.lora_model import LoraModel
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from bmtools.agent.autogptmulti.agent import AutoGPT
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    ChatGeneration,
    ChatMessage,
    ChatResult,
    HumanMessage,
    SystemMessage,
)

logger = get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--model_path', type=str, default="your_model_path/", required=True, help='tool-llama model path')
parser.add_argument('--lora_path', type=str, default="", required=False, help='tool-llama lora model path')
args = parser.parse_args()


# basically copy the codes in BMTools/bmtools/agent/tools_controller.py
def load_valid_tools(tools_mappings):
    tools_to_config = {}
    for key in tools_mappings:
        get_url = tools_mappings[key]+".well-known/ai-plugin.json"
        
        response = requests.get(get_url)

        if response.status_code == 200:
            tools_to_config[key] = response.json()
        else:
            logger.warning("Load tool {} error, status code {}".format(key, response.status_code))

    return tools_to_config
    

class MTQuestionAnswerer:
    """Use multiple tools to answer a question. Basically pass a natural question to 
    """
    def __init__(self, all_tools, stream_output=False, customllm=None):
        openai_api_key = os.environ.get('OPENAI_API_KEY', "")
        if len(openai_api_key) < 3: # not valid key (TODO: more rigorous checking)
            raise RuntimeError("Please set OPENAI_API_KEY environment variable.")
        self.openai_api_key = openai_api_key
        self.stream_output = stream_output
        self.llm = customllm
        self.load_tools(all_tools)
    
    def load_tools(self, all_tools):
        logger.info("All tools: {}".format(all_tools))
        self.all_tools_map = {}
        self.tools_pool = []
        for name in all_tools:
            meta_info = all_tools[name]

            question_answer = STQuestionAnswerer(self.openai_api_key, stream_output=self.stream_output)
            question_answer.llm = self.llm
            subagent = question_answer.load_tools(name, meta_info, prompt_type="react-with-tool-description", return_intermediate_steps=False)
            tool_logo_md = f'<img src="{meta_info["logo_url"]}" width="32" height="32" style="display:inline-block">'
            for tool in subagent.tools:
                tool.tool_logo_md = tool_logo_md
            tool = Tool(
                name=meta_info['name_for_model'],
                description=meta_info['description_for_model'].replace("{", "{{").replace("}", "}}"),
                func=subagent,
            )
            tool.tool_logo_md = tool_logo_md
            self.tools_pool.append(tool)
        
    def build_runner(self, ):
        embeddings_model = OpenAIEmbeddings()
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
        customllm = self.llm
        class MyChatAI(ChatOpenAI):
            def _create_chat_result(self, response):
                generations = []
                for res in response["choices"]:
                    message = self._convert_dict_to_message(res["message"])
                    gen = ChatGeneration(message=message)
                    generations.append(gen)
                llm_output = {"token_usage": response["usage"], "model_name": "tool-llama"}
                return ChatResult(generations=generations, llm_output=llm_output)
            
            def _generate(self, messages, stop):
                message_dicts, params = self._create_message_dicts(messages, stop)
                
                #TODO need to align prompts to training
                prompt = ''
                for prompt_dict in message_dicts:
                    if prompt_dict["role"] == "system":
                        prompt += ("System: " + prompt_dict["content"]) 
                    else:
                        prompt += ("Human: " + prompt_dict["content"])
                
                response = customllm(prompt)
                response_dict = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response
                        }
                    }],
                    "usage": {'prompt_tokens': -1, 'completion_tokens': -1, 'total_tokens': -1}
                }
                return self._create_chat_result(response_dict)
            
            def _convert_dict_to_message(self, _dict: dict):
                role = _dict["role"]
                if role == "user":
                    return HumanMessage(content=_dict["content"])
                elif role == "assistant":
                    return AIMessage(content=_dict["content"])
                elif role == "system":
                    return SystemMessage(content=_dict["content"])
                else:
                    return ChatMessage(content=_dict["content"], role=role)

        agent_executor = AutoGPT.from_llm_and_tools(
            ai_name="Jerry",
            ai_role="Assistant",
            tools=self.tools_pool,
            llm=MyChatAI(temperature=0),
            memory=vectorstore.as_retriever()
        )
        return agent_executor


if __name__ == "__main__":
    # vacation plan tools mappings
    tools_mappings = {
        "google_places": "http://127.0.0.1:8079/tools/google_places/",
        "wikipedia": "http://127.0.0.1:8079/tools/wikipedia/",
        "weather": "http://127.0.0.1:8079/tools/weather/",
        "bing_search": "http://127.0.0.1:8079/tools/bing_search/",
    }
    tools = load_valid_tools(tools_mappings)
    if args.lora_path == "":
        customllm = LlamaModel(args.model_path)
    else:
        customllm = LoraModel(base_name_or_path=args.model_path, model_name_or_path=args.lora_path)
    qa =  MTQuestionAnswerer(all_tools=tools, customllm=customllm)
    agent = qa.build_runner()
    while True:
        query = input("Input your query: ")
        output = agent(query)
        # print(output)
    

