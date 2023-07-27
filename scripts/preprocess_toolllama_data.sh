export PYTHONPATH=./
export TOOL_DATA_DIR="data/toolllama/raw_answer/G1_demo/"
export METHOD="DFS_woFilter_w2"
export OUTPUT_FILE="data/toolllama/processed_answer/G1_demo_DFS_woFilter_w2.json"

python data/preprocess_toolllama_data.py \
    --tool_data_dir $TOOL_DATA_DIR \
    --method $METHOD \
    --output_file $OUTPUT_FILE