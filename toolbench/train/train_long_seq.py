# Make it more memory efficient by monkey patching the LLaMA model with FlashAttn.

# Need to call this before importing transformers.

from toolbench.train.llama_condense_monkey_patch import (
    replace_llama_with_condense,
)
# ratio = 4 means the sequence length is expanded by 4, remember to change the model_max_length to 8192 (2048 * ratio) for ratio = 4
replace_llama_with_condense(ratio=4)

from toolbench.train.llama_flash_attn_monkey_patch import (
    replace_llama_attn_with_flash_attn,
)
replace_llama_attn_with_flash_attn()

from toolbench.train.train import train

if __name__ == "__main__":
    train()
