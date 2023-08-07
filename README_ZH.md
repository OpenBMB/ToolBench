<div align= "center">
    <h1> 🛠️ToolBench🤖</h1>
</div>

<div align="center">

![Dialogues](https://img.shields.io/badge/Tool\_Num-3451-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/API\_Num-16464-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Current\_Dataset\_Size-12K-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Total\_API\_Call-37K-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Average\_Reasoning\_Traces-4.1-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Tool\_LLaMA-Released-green?style=flat-square)

</div>

<p align="center">
  <a href="#model">Model</a> •
  <a href="#data">Data Release</a> •
  <a href="#web-ui">Web Demo</a> •
  <a href="#tool-eval">Tool Eval</a> •
  <a href="assets/paper.pdf">Paper</a> •
  <a href="#citation">Citation</a>

</p>

</div>

<div align="center">
<img src="https://cdn.discordapp.com/attachments/941582479117127680/1111543600879259749/20230526075532.png" width="350px">
</div>

🔨这个项目(ToolLLM)旨在构建**开源、大规模、高质量**的指令调整 SFT 数据，以促进构建具有通用工具使用能力的强大LLMs。我们的目标是赋予开源 LLMs 掌握成千上万多样的真实世界API能力。我们通过收集高质量的指令调整数据集来实现这一目标。该数据集使用最新的ChatGPT（gpt-3.5-turbo-16k）自动构建，该版本升级了增强的函数调用功能。我们提供数据集、相应的训练和评估脚本，以及在ToolBench上经过微调的强大模型ToolLLaMA。

**💁‍♂️💁💁‍♀️在 [Discord](https://discord.gg/asjtEkAA) 加入我们!**

*英文[README](README.md)链接.*

## 最新支持

- **[2023/8/4]** 我们提供RapidAPI后端服务，以免您使用自己的RapidAPI私钥去订阅API。填写[表单](https://forms.gle/oCHHc8DQzhGfiT9r6)后，我们会尽快审核并给您发送ToolBench key去请求该后端服务! 

- **[2023/8/1]** 我们的[论文](https://arxiv.org/abs/2307.16789)正式发布.

- **[2023/7/27]** 新版本ToolBench更新.

✨以下是数据集构建方法、模型训练、评测的整体概览

<br>
<div align="center">
<img src="assets/overview.png" width="800px">
</div>
<br>

✨✨特点:
 - API收集: 我们从 RapidAPI 收集了 16464 个API。RapidAPI 是一个托管开发者提供的大规模真实世界API的平台。

 - 指令生成: 我们生成了涉及单工具和多工具场景的指令。

 - 答案标注: 我们设计了一种新颖的深度优先搜索决策树方法（DFSDT），以增强LLMs的规划和推理能力。这显著提高了标注效率，并成功地对那些不能用CoT或ReACT回答的复杂指令进行了标注。我们提供的回答不仅包括最终答案，还包括模型的推理过程、工具执行和工具执行结果。

 - API Retriever: 我们整合了API检索模块，为ToolLLaMA提供了开放域的工具使用能力。

 - 所有数据均由OpenAI API自动生成并由我们筛选，整个数据创建过程易于扩展。

<br>
<div align="center">
<img src="assets/comparison.png" width="800px">
</div>
<br>

以下是**ToolLLaMA的demo展示**

<div align="center">

https://github.com/OpenBMB/ToolBench/assets/25274507/f1151d85-747b-4fac-92ff-6c790d8d9a31

</div>

目前，我们的ToolLLaMA已经达到了和ChatGPT（turbo-16k）接近的工具使用能力，未来*我们将不断进行数据的后处理与清洗，以提高数据质量并增加真实世界工具的覆盖范围。*

<div align="center">
<img src="assets/performance.png" width="300px">
</div>

这是*[老版本](https://github.com/OpenBMB/ToolBench/tree/legacy)*的ToolBench。
<!-- 💁‍♂️💁💁‍♀️**We need your help!** Curating large-scale real-world APIs and their corresponding tool-use SFT data is not easy, we sincerely invite you to join us in building and refining ToolBench. We will list all participants as co-authors in the final paper. Please contact and join [us](mailto:yujiaqin16@gmail.com) if you're interested. -->

## 🗒️数据

👐ToolBench仅用于研究和教育目的，不应被视为反映此数据集的创作者、所有者或贡献者的观点或意见。该数据集以 CC BY NC 4.0许可证 进行分发。以下是数据集的统计信息:

| 工具数量 | API数量 | 实例数量 | 真实API调用数量 | 平均Reasoning步数 |
|-----------|----------|---------------|---------------|------------------|
| 3451      | 16464    | 12657         | 37204         | 4.1              |

我们从[RapidAPI](https://rapidapi.com/hub)爬取了超过16000个API，并且为之构造了真实的人类指令。以下是RapidAPI的架构信息与指令构造的方式。

<br>
<div align="center">
<img src="assets/instructiongeneration.png" width="800px">
</div>
<br>


ToolBench包含单工具和多工具场景。多工具场景可以进一步分为类别内多工具和集合内多工具。我们在数据创建过程中使用DFSDT方法。以下是使用DFSDT方法进行数据创建的说明：

<div align="center">

<img src="assets/answer_anno.png" width="800px">

</div>

### 数据发布

 请使用以下链接下载我们的数据集：[Google Drive](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J)或者[清华云盘](https://cloud.tsinghua.edu.cn/f/c9e50625743b40bfbe10/).

 - `G1`，`G2`，`G3` 数据分别代表单工具数据，类别内多工具数据和集合内多工具数据。我们在 G1、G2 和 G3 数据内分别划分出训练集、验证集和测试集，并将训练集合并，作为我们的主要实验的训练数据。`toolllama_G123_dfs_train.json` 文件代表合并后的训练集数据。同时我们也给出了基于Atlas的数据可视化结果：[Atlas Explorer](https://atlas.nomic.ai/map/58aca169-c29a-447a-8f01-0d418fc4d341/030ddad7-5305-461c-ba86-27e1ca79d899) for visualization。
 - 与工具环境相关的数据位于 `toolenv` 目录下。
 - 我们从每个测试集中抽样 100 个实例。`test_query_ids` 目录包含每个测试集中测试实例的query id。
 - 用于工具检索的数据也包含在 `retrieval` 目录中。


## 🤖模型
我们发布了全参数微调版本[ToolLLaMA-7b](https://huggingface.co/ToolBench/ToolLLaMA-7b)和lora版本[ToolLLaMA-7b-LoRA](https://huggingface.co/ToolBench/ToolLLaMA-7b-LoRA)，都是在发布的数据集上以多任务方式训练的。我们也发布在实验设置下训练的[tool retriever](https://huggingface.co/ToolBench/ToolBench_IR_bert_based_uncased).
## 🚀精调
### 安装
克隆这个仓库并进入ToolBench文件夹。
```bash
git clone git@github.com:OpenBMB/ToolBench.git
cd ToolBench
```
安装包 (python>=3.9)
```bash
pip install -r requirements.txt
```
或者仅安装ToolEval需要的包
```bash
pip install -r toolbench/tooleval/requirements.txt
```

准备数据和工具环境:
```bash
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Vis-RxBstXLKC1W1agIQUJNuumPJrrw0&confirm=yes' -O data.zip
unzip data.zip
```


### 训练Retriever
- 数据预处理:
```bash
export PYTHONPATH=./
python data/preprocess_retriever_data.py \
    --query_file data/instruction/G1_query.json \
    --index_file data/test_query_ids/G1_instruction_test_query_ids.json \
    --dataset_name G1 \
    --output_dir data/retrieval/G1
```
- 使用以下命令训练Retriever:
```bash
export PYTHONPATH=./
python toolbench/retrieval/train.py \
    --data_path data/retrieval/G1/ \
    --model_name bert-base-uncased \
    --output_path retrieval_model \
    --num_epochs 5 \
    --train_batch_size 32 \
    --learning_rate 2e-5 \
    --warmup_steps 500 \
    --max_seq_length 256
```

### 训练ToolLLaMA
我们的训练代码基于[FastChat](https://github.com/lm-sys/FastChat)开发.您可以使用以下命令用两张A100（80G）训练ToolLLaMA-7b, 训练数据是我们已经处理好的[数据](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J):
```bash
export PYTHONPATH=./
torchrun --nproc_per_node=2 --master_port=20001 toolbench/train/train_long_seq.py \
    --model_name_or_path huggyllama/llama-7b  \
    --data_path  data/toolllama_G123_dfs_train.json \
    --eval_data_path  data/toolllama_G123_dfs_eval.json \
    --conv_template tool-llama-single-round \
    --bf16 True \
    --output_dir toolllama \
    --num_train_epochs 2 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 8 \
    --evaluation_strategy "epoch" \
    --prediction_loss_only \
    --save_strategy "epoch" \
    --save_total_limit 8 \
    --learning_rate 5e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.04 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --fsdp "full_shard auto_wrap" \
    --fsdp_transformer_layer_cls_to_wrap 'LlamaDecoderLayer' \
    --tf32 True \
    --model_max_length 8192 \
    --gradient_checkpointing True \
    --lazy_preprocess True \
    --report_to none
```

您也可以用以下命令用您自己的方式去预处理并划分数据:
```bash
export PYTHONPATH=./
python preprocess/preprocess_toolllama_data.py \
    --tool_data_dir data/answer/G1_answer \
    --method DFS_woFilter_w2 \
    --output_file data/answer/toolllama_G1_dfs.json
```


训练lora版本:
```bash
export PYTHONPATH=./
deepspeed --master_port=20001 toolbench/train/train_long_seq_lora.py \
    --model_name_or_path huggyllama/llama-7b  \
    --data_path  data/toolllama_G123_dfs_train.json \
    --eval_data_path  data/toolllama_G123_dfs_eval.json \
    --conv_template tool-llama-single-round \
    --bf16 True \
    --output_dir toolllama_lora \
    --num_train_epochs 5 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 2 \
    --evaluation_strategy "epoch" \
    --prediction_loss_only \
    --save_strategy "epoch" \
    --save_total_limit 8 \
    --learning_rate 5e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.04 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --model_max_length 8192 \
    --gradient_checkpointing True \
    --lazy_preprocess True \    
    --deepspeed ds_configs/stage2.json \
    --report_to none
```


## 用我们的RapidAPI服务进行推理
请先填写[问卷](https://forms.gle/oCHHc8DQzhGfiT9r6)，我们会尽快审核然后给您发送toolbench key。然后初始化您的toolbench key:
```bash
export TOOLBENCH_KEY="your_toolbench_key"
```
### ToolLLaMA
用以下命令用ToolLLaMA做推理:
```bash
export PYTHONPATH=./
python toolbench/inference/qa_pipeline.py \
    --tool_root_dir data/toolenv/tools/ \
    --backbone_model toolllama \
    --model_path /path/to/your/toolllama \
    --max_observation_length 1024 \
    --observ_compress_method truncate \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo.json \
    --output_answer_file data/answer/toolllama_dfs \
    --toolbench_key $TOOLBENCH_KEY
```

**lora**版本的inference:
```bash
export PYTHONPATH=./
python toolbench/inference/qa_pipeline.py \
    --tool_root_dir data/toolenv/tools/ \
    --backbone_model toolllama \
    --model_path huggyllama/llama-7b \
    --lora \
    --lora_path /path/to/your/toolllama_lora \
    --max_observation_length 1024 \
    --observ_compress_method truncate \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo.json \
    --output_answer_file data/answer/toolllama_lora_dfs \
    --toolbench_key $TOOLBENCH_KEY
```

lora版本的**开放域**, 用以下命令:
```bash
export PYTHONPATH=./
python toolbench/inference/qa_pipeline_open_domain.py \
    --tool_root_dir data/toolenv/tools/ \
    --corpus_tsv_path data/retrieval/G1/corpus.tsv \
    --retrieval_model_path /path/to/your/retrival_model \
    --retrieved_api_nums 5 \
    --backbone_model toolllama \
    --model_path huggyllama/llama-7b \
    --lora \
    --lora_path /path/to/your/toolllama_lora \
    --max_observation_length 1024 \
    --observ_compress_method truncate \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo_open_domain.json \
    --output_answer_file data/answer/toolllama_lora_dfs_open_domain \
    --toolbench_key $TOOLBENCH_KEY
```
### OpenAI模型
用ChatGPT:
```bash
export TOOLBENCH_KEY=""
export OPENAI_KEY=""
export PYTHONPATH=./
python toolbench/inference/qa_pipeline.py \
    --tool_root_dir data/toolenv/tools/ \
    --backbone_model chatgpt_function \
    --openai_key $OPENAI_KEY \
    --max_observation_length 1024 \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo.json \
    --output_answer_file data/answer/chatgpt_dfs \
    --toolbench_key $TOOLBENCH_KEY
```

用Text-Davinci-003:
```bash
export TOOLBENCH_KEY=""
export OPENAI_KEY=""
export PYTHONPATH=./
python toolbench/inference/qa_pipeline.py \
    --tool_root_dir data/toolenv/tools/ \
    --backbone_model davinci \
    --openai_key $OPENAI_KEY \
    --max_observation_length 1024 \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo.json \
    --output_answer_file data/answer/davinci_dfs \
    --toolbench_key $TOOLBENCH_KEY
```

## 用您自己的RapidAPI账号做推理
要用定制化的RapidAPI账号进行推理，请在脚本中传入您的**rapidapi key**并指定`use_rapidapi_key`参数:
```bash
export RAPIDAPI_KEY=""
export OPENAI_KEY=""
export PYTHONPATH=./
python toolbench/inference/qa_pipeline.py \
    --tool_root_dir data/toolenv/tools/ \
    --backbone_model chatgpt_function \
    --openai_key $OPENAI_KEY \
    --max_observation_length 1024 \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo.json \
    --output_answer_file data/answer/chatgpt_dfs \
    --rapidapi_key $RAPIDAPI_KEY \
    --use_rapidapi_key
```

## Setting up and running the interface

ToolBench包含一个基于[Chatbot UI](https://github.com/mckaywrigley/chatbot-ui)的Web UI，经过修改以包含在界面中使用工具的功能。它包含两个部分：后端服务器和[chatbot-ui-toolllama](https://github.com/lilbillybiscuit/chatbot-ui-toolllama)。这是一个[视频演示](assets/toolbench-demo.mp4)。

### Web UI
```bash
git clone https://github.com/lilbillybiscuit/chatbot-ui-toolllama
cd chatbot-ui-toolllama
npm install
npm run dev
```

应用将在 http://localhost:3000/ 上可用

### Backend server
```bash
export PYTHONPATH=./
python toolbench/inference/toolbench_server.py \
    --tool_root_dir data/toolenv/tools/ \
    --corpus_tsv_path data/retrieval/G1/corpus.tsv \
    --retrieval_model_path /path/to/your/retrival_model \
    --retrieved_api_nums 5 \
    --backbone_model toolllama \
    --model_path huggyllama/llama-7b \
    --lora \
    --lora_path /path/to/your/toolllama_lora \
    --max_observation_length 1024 \
    --method DFS_woFilter_w2 \
    --input_query_file data/instruction/inference_query_demo_open_domain.json \
    --output_answer_file data/answer/toolllama_lora_dfs_open_domain \
    --rapidapi_key $RAPIDAPIKEY
```

This server will be available on `http://localhost:5000/`. To start a request, call `http://localhost:5000/stream` with a GET or POST request containing a JSON object with the following fields:
```json
{
    "text": "What is the weather in New York today?",
    "top_k": 5,
    "method": "DFS_woFilter_w2"
}
```


## ToolEval

通过在ToolBench上对LLaMA进行微调，我们得到了**ToolLLaMA**。考虑到人工评估非常耗时，我们借鉴[AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/)开发了一个高效的机器自动评估**ToolEval**，其中包含两个评估指标：

- **通过率**：计算在有限的OpenAI API调用次数内成功完成指令的比例。

- **偏好**：通过比较给定指令的两个答案（动作序列）来衡量。我们预先定义了一组更好答案的标准，这些标准被组织成ChatGPT的提示。我们向评估器提供测试指令和两个候选答案，并获得其偏好。我们对每个答案对进行多次评估以提高系统的可靠性。然后，我们计算**优胜率**（被评估器选择为更优的百分比）和**标准差**（优胜率的标准误差）。有关详细信息，请参阅我们的论文。

为了验证偏好指标的有效性，我们从三种不同方法（ChatGPT+ReACT、GPT4+ReACT和ChatGPT+DFSDT）中随机抽样获得600个测试指令的答案对。然后，我们邀请人工标注人员对它们进行人工偏好注释（每个答案对4个注释，总共2400个注释）。我们使用ChatGPT开发的自动评估器与人工标注者呈现出显著的**75.8%**相关性。我们还获得了不同人工标注者之间的一致性为**83.54%**，与我们的评估器和人类标注者之间的一致性为**80.21%**。

有关ToolEval的更多细节，请参阅我们的论文。


### Evaluation with ToolEval
要在测试集（如G1-Inst.）上评估模型，可以执行以下命令：
- 通过率:
```bash
python toolbench/tooleval/pass_rate.py --answer_dir data/answer/toolllama_dfs/G1_instruction
```
- 优胜率 (参考模型: ChatGPT-ReACT):
```bash
export OPENAI_KEY=""
export REF_MODEL_DATA="data/answer/chatgpt_cot/G1_instruction"
export REF_MODEL_METHOD="CoT"
export TEST_MODEL_DATA="data/answer/toolllama_dfs/G1_instruction"
export TEST_MODEL_METHOD="DFS"
python ./toolbench/tooleval/convert_to_answer_format.py \
    --method CoT \
    --answer_dir $REF_MODEL_DATA \
    --output ${REF_MODEL_DATA}_converted

python ./toolbench/tooleval/convert_to_answer_format.py \
    --method DFS \
    --answer_dir $TEST_MODEL_DATA \
    --output ${TEST_MODEL_DATA}_converted

python ./toolbench/tooleval/automatic_eval_sample.py \
    --output ${REF_MODEL_DATA}_converted \
    --ref_output ${TEST_MODEL_DATA}_converted \
    --method $REF_MODEL_METHOD \
    --use_existed_output
```

### Model Experiment

在我们的主要实验中，ToolLLaMA展现了处理单一工具和复杂多工具指令的引人注目的能力。
以下是与ChatGPT和Text-Davinci-003相比的主要结果。

**通过率**
| model                   | I1-Inst. | I1-Tool. | I1-Cat. | I2-Inst. | I2-Cat. | I3-Inst. | Average  |
|-------------------------|----------|----------|---------|----------|---------|----------|----------|
| ChatGPT-DFSDT           | **78**   | **84**   | **89**  | **51**   | **58**  | **57**   | **69.6** |
| ChatGPT-ReACT           | 56       | 62       | 66      | 28       | 22      | 30       | 44.0     |
| Text-Davinci-003-DFSDT  | 53       | 58       | 61      | 38       | 38      | 39       | 47.8     |
| Text-Davinci-003-ReACT  | 19       | 25       | 30      | 12       | 11      | 14       | 18.5     |
| ToolLLaMA               | 68       | 80       | 75      | 47       | 56      | 40       | 61.0     |
| ToolLLaMA-LoRA          | 51       | 63       | 61      | 38       | 42      | 45       | 50.0     |
| ToolLLaMA-API Retriever | 62       | 62       | 72      | 45       | 55      | 47       | 57.2     |

**优胜率** (参考模型: ChatGPT-DFSDT)
| model                  | I1-Inst. | I1-Tool. | I1-Cat. | I2-Inst. | I2-Cat. | I3-Inst. | Average |
|------------------------|----------|----------|---------|----------|---------|----------|---------|
| ChatGPT-DFSDT | 50       | 50       | 50      | 50       | 50      | 50       | 50.0    |
| ChatGPT-ReACT | 38       | 32       | 41      | 43       | 22      | 23       | 30.7    |
| Text-Davinci-003-ReACT | 14       | 21       | 18      | 8       | 7      | 12       | 13.3    |
| Text-Davinci-003-DFSDT | 38       | 34       | 43      | 25       | 20      | 28       | 31.3    |
| ToolLLaMA              | **50**       | 45       | 45      | **59**       | 48      | 46       | 48.8    |
| ToolLLaMA-LoRA              | 43       | 36.4       | 30      | 42       | 45      | **51**       | 41.2    |
| ToolLLaMA-API Retriever              | **51**       | 39       | 44      | 49       | 49      | **55**       | 47.8    |


## TODO
- [ ] ToolLLaMA将达到GPT-4的工具使用能力。
- [ ] 我们将训练一个ToolLLaMa-2。

## 工具学习相关链接

鉴于基础模型的强大能力，我们期待看到它们在操纵各种工具中的应用。更多的资源，请参考以下内容：

- **BMTools**. [[Project](https://github.com/OpenBMB/BMTools)]

- **Tool Learning Survey**. [[Paper](https://arxiv.org/abs/2304.08354)]
  
- **Tool Learning Paper List**. [[Project](https://github.com/thunlp/ToolLearningPapers)]

- **WebCPM**. [[Paper](https://github.com/thunlp/WebCPM)]

## Citation
如果您对ToolBench感兴趣，欢迎引用我们的工作。

```bibtex
@misc{qin2023tool,
      title={Tool Learning with Foundation Models}, 
      author={Yujia Qin and Shengding Hu and Yankai Lin and Weize Chen and Ning Ding and Ganqu Cui and Zheni Zeng and Yufei Huang and Chaojun Xiao and Chi Han and Yi Ren Fung and Yusheng Su and Huadong Wang and Cheng Qian and Runchu Tian and Kunlun Zhu and Shihao Liang and Xingyu Shen and Bokai Xu and Zhen Zhang and Yining Ye and Bowen Li and Ziwei Tang and Jing Yi and Yuzhang Zhu and Zhenning Dai and Lan Yan and Xin Cong and Yaxi Lu and Weilin Zhao and Yuxiang Huang and Junxi Yan and Xu Han and Xian Sun and Dahai Li and Jason Phang and Cheng Yang and Tongshuang Wu and Heng Ji and Zhiyuan Liu and Maosong Sun},
      year={2023},
      eprint={2304.08354},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
