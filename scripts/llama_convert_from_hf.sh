export MODEL_NAME="meta-llama/Llama-2-7b-hf"
export SAVE_DIR="/ssd/data/xihaocheng/ToolBench/converted_models/llama-2-7b"

COAT_PATH=$(pip show coat | grep "Editable project location" | awk -F': ' '{print $2}')
echo "COAT package is located at: $COAT_PATH"

python $COAT_PATH/coat/activation/models/coat_llama_convert_from_hf.py \
    --model_name $MODEL_NAME \
    --save_path $SAVE_DIR \
    --quantize_model true \
    --fabit E4M3 \
    --fwbit E4M3 \
    --fobit E4M3 \
    --bwbit E5M2 \
    --babit E5M2 \
    --bobit E5M2 \
    --group_size 16
