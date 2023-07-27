export PYTHONPATH=./
export DATA_DIR="data/retrieval/G1/"
export MODEL_NAME="bert-base-uncased"
export OUTPUT_PATH="retriever_model"

python toolbench/retrieval/train.py \
    --data_path $DATA_DIR \
    --model_name $MODEL_NAME \
    --output_path $OUTPUT_PATH \
    --num_epochs 5 \
    --train_batch_size 32 \
    --learning_rate 2e-5 \
    --warmup_steps 500 \
    --max_seq_length 256