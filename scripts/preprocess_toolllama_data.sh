export PYTHONPATH=./
export TOOL_DATA_DIR="data/answer/G1_answer/"
export METHOD="DFS_woFilter_w2"
export OUTPUT_FILE="data/answer/toolllama_G1_dfs.json"

python preprocess/preprocess_toolllama_data.py \
    --tool_data_dir $TOOL_DATA_DIR \
    --method $METHOD \
    --output_file $OUTPUT_FILE