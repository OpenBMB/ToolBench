#!/bin/bash

export OPENAI_KEY=""
TESTSET='G1_instruction'

ANS_DIR="data/answer/"

MODEL_1="chatgpt_cot"
METHOD_1='CoT'

MODEL_2="toolllama_dfsdt"
METHOD_2='DFS'

ANS_DIR_1="$ANS_DIR/$MODEL_1"
ANS_DIR_2="$ANS_DIR/$MODEL_2"

mkdir "$ANS_DIR/converted_answer"
OUTPUT_DIR_1="$ANS_DIR/converted_answer/$MODEL_1_$TESTSET_$METHOD_1"
OUTPUT_DIR_2="$ANS_DIR/converted_answer/$MODEL_2_$TESTSET_$METHOD_2"

python ./toolbench/tooleval/convert_to_answer_format.py \
    --method $METHOD_1 \
    --answer_dir "$ANS_DIR_1/$TESTSET" \
    --output $OUTPUT_DIR_1

python ./toolbench/tooleval/convert_to_answer_format.py \
    --method $METHOD_2 \
    --answer_dir "$ANS_DIR_2/$TESTSET" \
    --output $OUTPUT_DIR_2

python ./toolbench/tooleval/automatic_eval_sample.py \
    --output $OUTPUT_DIR_1 \
    --ref_output $OUTPUT_DIR_2 \
    --method $METHOD_1 \
    --use_existed_output