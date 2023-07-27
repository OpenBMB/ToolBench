#!/bin/bash

TESTSET='G1_instruction'
ANS_DIR="data/toolllama/tooleval_answer/chatgpt_cot/$TESTSET"

python toolbench/tooleval/pass_rate.py --answer_dir $ANS_DIR