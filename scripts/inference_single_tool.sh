#! /bin/bash
source BMTools/secret_keys.sh
export PYTHONPATH=BMTools
python toolfarm/inference/inference_single_tool.py \
    --tool_name weather \
    --model_path /path/to/tool-llama/weights
