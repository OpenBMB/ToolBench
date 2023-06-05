#! /bin/bash
source BMTools/secret_keys.sh
export PYTHONPATH=BMTools
python toolbench/inference/inference_single_tool.py \
    --tool_name weather \
    --model_path /path/to/llama/weights \
    --lora_path /path/to/lora/weights
