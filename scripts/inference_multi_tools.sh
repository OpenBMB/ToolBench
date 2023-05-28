#! /bin/bash
source BMTools/secret_keys.sh
export PYTHONPATH=BMTools
python toolfarm/inference/inference_multi_tools.py --model_path /path/to/tool-llama/weights
