from typing import Any, Dict, List, Union
import queue
class ServerEventCallback():
    """Base callback handler"""

    def __init__(self, queue: queue.Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.llm_block_id = 0
        self.tool_block_id = 0
        self.tool_descriptions = {}

    def add_to_queue(self, method_name: str, block_id, **kwargs: Any):
        data = {
            "method_name": method_name,
            "block_id": block_id,
        }
        data.update(kwargs)
        self.queue.put(data)

    def on_tool_retrieval_start(self):
        # tools should be of the form
        # {tool_name, tool_desc}
        self.add_to_queue(
            "on_tool_retrieval_start",
            "recommendation-1",
        )
        print("on_tool_retrieval_start method called")

    def on_tool_retrieval_end(self, tools):
        # tool should be of the form
        # {tool_name, tool_desc}
        self.add_to_queue(
            "on_tool_retrieval_end",
            "recommendation-1",
            recommendations=tools
        )
        self.tool_descriptions = {
            tool["name"]: tool for tool in tools
        }
        print("on_tool_retrieval_end method called")
    def on_request_start(self, user_input: str, method: str) -> Any:
        self.tool_block_id = 0
        self.llm_block_id = 0
        self.add_to_queue(
            "on_request_start",
            block_id="start",
            user_input=user_input,
            method=method
        )
    def on_request_end(self, outputs: str, chain: List[Any]):
        self.add_to_queue(
            "on_request_end",
            block_id="end",
            output=outputs,
            chain=chain
        )
    def on_request_error(self, error: str):
        self.add_to_queue(
            "on_request_error",
            block_id="error",
            error=error
        )

    # keep
    def on_chain_start(self, inputs: str, depth: int) -> Any:
        """Run when chain starts running."""
        print("on_chain_start method called")
        self.llm_block_id += 1
        block_id = "llm-" + str(self.llm_block_id)
        self.add_to_queue(
            "on_chain_start",
            block_id=block_id,
            messages=inputs,
            depth=depth
        )
        return block_id

    # this one needs the block_id memorized
    def on_chain_end(self, block_id: str, depth: int) -> Any:
        self.add_to_queue(
            "on_chain_end",
            block_id=block_id,
            # output=output,
            depth=depth
        )
        print("on_chain_end method called")

    def on_chain_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        method_name = "on_chain_error"
        self.add_to_queue(method_name, error=error, **kwargs)
        print("on_chain_error method called")

    def on_llm_start(
            self, messages: str, depth: int
    ) -> Any:
        """Run when LLM starts running."""
        self.add_to_queue(
            "on_llm_start",
            block_id="llm-" + str(self.llm_block_id),
            messages=messages,
            depth=depth
        )
        print("on_llm_start method called")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        method_name = "on_llm_new_token"
        self.add_to_queue(method_name, token=token, **kwargs)
        print("on_llm_new_token method called")

    def on_llm_end(self, response: str, depth: int) -> Any:
        """Run when LLM ends running."""
        self.add_to_queue(
            "on_llm_end",
            block_id="llm-" + str(self.llm_block_id),
            response=response,
            depth=depth
        )
        print("on_llm_end method called")

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt]) -> Any:
        """Run when LLM errors."""
        self.add_to_queue(
            "on_llm_error",
            block_id="llm-" + str(self.llm_block_id),
            message=str(error),
            error=error
        )
        print("on_llm_error method called")

    def on_agent_action(self, action, action_input, depth: int) -> str:
        self.tool_block_id += 1
        block_id="tool-" + str(self.tool_block_id)
        self.add_to_queue(
            "on_agent_action",
            block_id=block_id,
            action=action,
            action_input = action_input,
            depth=depth
        )
        print("on_agent_action method called")
        return block_id

    def on_tool_start(self, tool_name: str, tool_input: str,  depth: int) -> Any:
        method_name = "on_tool_start"
        tool_description = "Tool not found in tool descriptions"
        if tool_name in self.tool_descriptions:
            tool_description = self.tool_descriptions[tool_name]
        else:
            print(self.tool_descriptions)
            print("Key", tool_name, "not found in tool descriptions")
        self.add_to_queue(
            method_name,
            block_id="tool-" + str(self.tool_block_id),
            tool_name=tool_name,
            tool_description=tool_description,
            tool_input=tool_input,
            depth=depth
        )
        print("on_tool_start method called")

    def on_tool_end(self, output: str, status:int, depth: int) -> Any:
        method_name = "on_tool_end"
        self.add_to_queue(
            method_name,
            block_id="tool-" + str(self.tool_block_id),
            output=output,
            status= status,
            depth=depth
        )
        print("on_tool_end method called")

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt]) -> Any:
        method_name = "on_tool_error"
        self.add_to_queue(
            method_name,
            error=error
        )
        print("on_tool_error method called")

    def on_agent_end(self, block_id:str, depth: int):
        self.add_to_queue(
            "on_agent_end",
            block_id=block_id,
            depth=depth
        )
        print("on_agent_end method called")