# Guidance for LLM Tool Usage (ToolBench)

This document provides guidance on how current Large Language Models (LLMs) like LLaMA-2, GPT-3.5, and GPT-4 can leverage the ToolBench dataset to learn how to effectively use tools.

## Introduction
ToolBench provides a large-scale, high-quality instruction tuning dataset. The dataset includes real-world API documentation, complex multi-tool queries, and complete reasoning traces using methods like ReAct or Depth-First Search-based Decision Trees (DFSDT).

## 1. Defining Tools in the System Prompt
To enable an LLM to use tools, the available functions must be explicitly defined in the system prompt. ToolBench uses a standard JSON schema format to define tools.

### Example Tool Definition
```json
{
  "name": "transitaire_for_transitaires",
  "description": "This is the subfunction for tool \"transitaires\", you can use this tool.The description of this function is: \"R\u00e9cup\u00e8re un transitaire donn\u00e9e\"",
  "parameters": {
    "type": "object",
    "properties": {
      "is_id": {
        "type": "string",
        "description": "",
        "example_value": "DOUANE_AGENCE_GONDRAND"
      }
    },
    "required": ["is_id"],
    "optional": []
  }
}
```

### Prompt Engineering
Your system prompt should instruct the model to use the tools effectively. A common structure is:
1. Define the persona (e.g., "You are an AI assistant that can use tools...").
2. Provide the tools schema as shown above.
3. Enforce an execution format (e.g., "Output your thought process, followed by an Action, and then the Action Input in JSON format").
4. Specify a "Finish" tool or action when the task is complete.

## 2. Using the Dataset for Supervised Fine-Tuning (SFT)
The provided script `scripts/copy_datasets_to_jsonl.py` extracts the `query`, `function` schemas, and `train_messages` from the ToolBench annotations.

### Data Structure
The `training_data.jsonl` output contains each instance as a JSON record with the conversational trace. To fine-tune an LLM, this must be mapped to your chosen chat format (e.g., ChatML).

**Example Mapping (ChatML Style):**
- **System Role**: Inject the tool schemas (`function` key) and instructions here.
- **User Role**: The human's `query`.
- **Assistant Role**: The model's reasoning (`Thought`), tool selection (`Action`), and parameters (`Action Input`), or the `final_answer`.
- **Function/Tool Role**: The simulated response from the API.

By training on these complete trajectories, the LLM learns to reason (CoT/ReAct) and output valid JSON for function calls.

## 3. The Inference Loop
During inference, the model cannot execute tools itself; it relies on an execution loop:

1. **Prompt the Model:** Provide the user query and the available tools in the system prompt.
2. **Model Generates Action:** The LLM outputs a `function_call` (or text indicating an action and parameters).
3. **Execution:** Your system parses the action, calls the real API or mocked environment, and receives a result.
4. **Provide Result:** Append the result as a new message (role: `function` or `tool`) to the conversation history.
5. **Iterate:** Feed the updated history back to the model. It will either take another action or use the `Finish` tool to return the `final_answer`.

## 4. Advanced: DFSDT vs ReAct
ToolBench uses DFSDT (Depth-First Search-based Decision Tree) which allows the model to explore multiple paths and backtrack if an API fails or returns poor results. While simple fine-tuning often uses standard ReAct (Thought -> Action -> Observation), more advanced setups can use tree-search algorithms at inference time to evaluate multiple candidate actions using the model's self-evaluation capabilities.
