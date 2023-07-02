1<div align= "center">
    <h1> 🛠️ToolBench🤖</h1>
</div>

<div align="center">

![Dialogues](https://img.shields.io/badge/Tool\_Num-29-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/API\_Num-86-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Current\_Dataset\_Size-98K-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Total\_API\_Call-312K-red?style=flat-square)
![Dialogues](https://img.shields.io/badge/Tool\_LLaMA-Released-green?style=flat-square)

</div>

<p align="center">
  <a href="#model">Model</a> •
  <a href="#data">Data Release</a> •
  <a href="https://github.com/OpenBMB/BMTools">Toolkit</a> •
  <a href="https://arxiv.org/abs/2304.08354">Paper</a> •
  <a href="https://github.com/thunlp/ToolLearningPapers">Paper List</a> •
  <a href="#citation">Citation</a> •

</p>

</div>


🔨本项目旨在构建**开源、大规模、高质量**的指令调优SFT数据，以促进构建具有通用**工具使用**能力的强大LLM。我们提供数据集，相应的训练和评估脚本，以及在ToolBench上进行了ToolLLaMA微调的可靠模型。

<div align="center">
<img src="https://cdn.discordapp.com/attachments/941582479117127680/1111543600879259749/20230526075532.png" width="400px">
</div>

✨✨特点：
 - ToolBench 支持**单工具**和**多工具**场景。单工具设置遵循[LangChain](https://github.com/hwchase17/langchain)风格的提示模版，而多工具设置则遵循[AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT)风格的提示模版。
 - ToolBench 提供的响应不仅包括最终答案，还融合了模型的**思维链路过程、工具执行和工具执行结果**。
 - ToolBench 接受现实世界场景的复杂性，支持**多步**工具调用。
 - 另一个显著优势是我们API的**多样性**，它专为诸如天气信息、搜索功能、股票更新和PowerPoint自动化等**现实世界场景**而设计。
 - 所有数据都是由OpenAI API自动生成并由我们进行筛选，整个数据创建过程易于扩展。


<br>
<div align="center">
<img src="https://cdn.discordapp.com/attachments/941582479117127680/1111210433307750451/ToolLLaMA.png" width="800px">
</div>
<br>

*请注意，当前发布的数据仍然不是最终版本。我们正在进行广泛的后处理工作，以提高数据质量并增加对现实世界工具的覆盖范围。*

<!-- 💁‍♂️💁💁‍♀️**我们需要您的帮助!** 策划大规模的现实世界API及其相应的工具使用SFT数据并非易事，我们真诚邀请您加入我们，共同建设和完善ToolBench。我们将在最终论文中将所有参与者列为共同作者。如果您有兴趣，请联系并加入[我们](mailto:yujiaqin16@gmail.com)。 -->

## 🗒️数据

👐ToolBench仅供研究和教育目的，并不反映此数据集的创建者、所有者或贡献者的观点或意见。它在[CC BY NC 4.0 License](https://creativecommons.org/licenses/by-nc/4.0/)许可证下进行分发。

ToolBench包含单工具和多工具场景，以下是单工具场景的统计数据：

| Tool           | Query Num | Chains Num | Chains/Query |
|----------------|-----------|------------|------------------|
| Weather        | 9827      | 23740      | 2.4              |
| Chemical       | 8585      | 29916      | 3.5              |
| Translation    | 10267     | 23011      | 2.2              |
| Map            | 7305      | 23325      | 3.2              |
| Stock          | 11805     | 32550      | 2.8              |
| Meta analysis  | 2526      | 15725      | 6.2              |
| Bing search    | 31089     | 102088     | 3.3              |
| Wolfram        | 16130     | 56169      | 3.5              |
| Database       | 1264      | 6347       | 5                |

以下是多工具场景的统计数据：

| Scenario      | Tools                                                                          | Query num | Sub-Query num | Chains num | Chains per Query |
|---------------|--------------------------------------------------------------------------------|-----------|---------------|------------|------------------|
| Meta_file     | chemical-prop/meta_analysis/Slides Making/Wikipedia/file_operation/Bing_search | 331       | 1197          | 5899       | 17.8             |
| Multi_film    | Wolfram/Film Search/Slides Making/Wikipedia/file_operation/Bing_search         | 795       | 2703          | 12445      | 15.7             |
| Vacation_plan | google_places/wikipedia/weather/bing search                                    | 191       | 654           | 2742       | 14.4             |

### 数据发布
对于单工具数据，我们发布了每个工具的1000个实例，而对于多工具数据，我们发布了全部数据。请使用以下链接下载我们的数据集：[数据](https://drive.google.com/drive/folders/1OaB-hM7eRiWi3TeqHij24VT9MAqgvC0H?usp=drive_link)。

### 数据格式
下载的数据文件中的每一行都是一个包含用于数据创建的模板化提示、人类指令（查询）用于工具使用、中间思考/工具执行循环以及最终答案的JSON字典。以下是单工具数据生成的示例：

```
Tool Descrition:
BMTools Tool_name: translation
Tool action: get_translation
action_input: {"text": target texts, "tgt_lang": target language}

Generated Data:
{
    "prompt": "Answer the following questions as best you can. Specifically, you have access to the following APIs:\n\nget_translation: . Your input should be a json (args json schema): {{\"text\" : string, \"tgt_lang\" : string, }} The Action to trigger this API should be get_translation and the input parameters should be a json dict string. Pay attention to the type of parameters.\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [get_translation]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times, max 7 times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin! Remember: (1) Follow the format, i.e,\nThought:\nAction:\nAction Input:\nObservation:\nFinal Answer:\n (2) Provide as much as useful information in your Final Answer. (3) Do not make up anything, and if your Observation has no link, DO NOT hallucihate one. (4) If you have enough information and want to stop the process, please use \nThought: I have got enough information\nFinal Answer: **your response. \n The Action: MUST be one of the following:get_translation\nQuestion: {input}\n Agent scratchpad (history actions):\n {agent_scratchpad}",
    "query": "My intention is to convert the data provided in ما هي الأقسام الثلاثة للقوات المسلحة؟ into Arabic(ara).\n",
    "chains": [
        {
            "thought": "I need to use the get_translation API to convert the text into Arabic.",
            "action": "get_translation",
            "action_input": "{\"text\": \"What are the three branches of the military?\", \"tgt_lang\": \"ara\"}",
            "observation": "\"ما هي الفروع الثلاثة للجيش ؟\""
        }
    ],
    "answer": "The translation of \"What are the three branches of the military?\" into Arabic is \"ما هي الفروع الثلاثة للجيش ؟\"."
}

```

多工具示例：

```
Here is an example of using Bing_Search tool, and PPT tool in BMTools:

{
        "query": "Can you find me examples of successful renewable energy projects in Africa? Please compile a list of case studies with details on the technologies used, costs, and environmental impact.\n",
        "steps": [
            {
                "assistant_reply": "{\n    \"thoughts\": {\n        \"text\": \"I think I should use the Bing_search command to look for successful renewable energy projects in Africa.\",\n        \"reasoning\": \"As an Assistant with legal background, I do not have enough knowledge to list out these projects. Therefore, I think it's a good idea to research and find some project examples on the internet. Bing_search is a suitable command for me since I can use it to perform searches on the internet.\"\n    },\n    \"command\": {\n        \"name\": \"Bing_search\",\n        \"args\": {\n            \"goal\": \"Find successful renewable energy projects in Africa\"\n        }\n    }\n}",
                "chains": [
                    {
                        "thought": "I need to search for examples of successful renewable energy projects in Africa.",
                        "action": "search_top3",
                        "action_input": "{\"key_words\": \"successful renewable energy projects Africa\"}",
                        "observation": "\"page: 1\\ntitle: This is the state of renewable energy in Africa right now\\nsummary: Africa. In 2020, 9% of all energy generated in Africa came from renewable sources, reports Statista. North Africa is the current leader on the continent in terms of renewable energy capacity. While Southern Africa is lagging behind, with just over 4,000 MW capacity.\\npage: 2\\ntitle: Lighting Up Africa: Bringing Renewable, Off-Grid Energy to Communities\\nsummary: Lighting Up Africa: Bringing Renewable, Off-Grid Energy to Communities. Photo credit: John Deyegbe/Resolution Ltd. This story is the first in a series to showcase the tools, approaches, evidence, and results of more than 300 projects in pursuit of climate-smart development under the Africa Climate Business Plan.\\npage: 3\\ntitle: The Renewable Energy Transition in Africa\\nsummary: Promote access to energy; De-risk and promoting private sector investments; Strengthen and modernise the grid; Support systemic innovation. The study also explores the transformational potential of the electricity sector in five Africa countries: Ghana, Ivory Coast, Morocco, Rwanda and South Africa.\\n\""
                    },
                    .....
                ],
                "answer": "Tool Bing_search returned: {'input': '{\"goal\": \"Find successful renewable energy projects in Africa\", \"history context\": \"[]\"}', 'output': 'The top 3 search results for \"successful renewable energy projects Africa\" do not provide specific information about successful renewable energy projects in Africa, but rather provide general information about the state of renewable energy in Africa and initiatives to promote it.'}"
            },
            .....
            {
                "assistant_reply": "{\n    \"thoughts\": {\n        \"text\": \"I think I should use the Slides Making command to create a presentation on renewable energy projects in Africa based on the information that we have collected so far.\",\n        \"reasoning\": \"Since I have not been able to find any specific information on successful renewable energy projects in Africa, I believe that creating a presentation using the information that we have collected so far might be a good idea. Slides Making is a suitable command for creating professional-looking presentations with text, paragraphs, and images, thereby allowing us to summarize and present the information that we have found in an effective manner.\"\n    },\n    \"command\": {\n        \"name\": \"Slides Making\",\n        \"args\": {\n            \"goal\": \"Create a presentation on renewable energy projects in Africa\"\n        }\n    }\n}",
                "chains": [
                    {
                        "thought": "We need to create a pptx file with a specific theme first before adding content to it.",
                        "action": "create_file",
                        "action_input": "{\"theme\":\"green\"}",
                        "observation": "\"created a ppt file.\""
                    },
                    ...
                ],
                "answer": "Tool Slides Making returned: {'input': '{\"goal\": \"Create a presentation on renewable energy projects in Africa\", \"history context\": \"[\\\\\"Tool Bing_search returned: {\\\\\\\\\\\\\"input\\\\\\\\\\\\\": \\\\\\\\\\\\\"{\"goal\": \"Find successful renewable energy projects in Africa\", \"history context\": \"[]\"}\\\\\\\\\\\\\", \\\\\\\\\\\\\"output\\\\\\\\\\\\\": \\\\\\\\\\\\\"The top 3 search results for \"successful renewable energy projects Africa\" do not provide specific information about successful renewable energy projects in Africa, but rather provide general information about the state of renewable energy in Africa and initiatives to promote it.\\\\\\\\\\\\\"}\\\\\"]\"}', 'output': 'The final pptx presentation can be found at the file path: /Users/ava/Downloads/BMTools-zzn0513_copy/cache/1684750606.0464199Renewable Energy Projects in Africa.pptx'}"
            }
        ]
    },

```




以下是使用BMTools进行数据创建过程的示例：

<div align="center">

<img src="assets/meta0423.gif" width="700px">

</div>

## 🤖Model

我们发布了 ToolLLaMA 的 7b Lora 版本，[单工具](https://huggingface.co/pooruss-lsh/tool-llama7b-single-tool-lora)以及[多工具](https://huggingface.co/pooruss-lsh/tool-llama7b-multi-tool-lora)，都是基于发布的工具数据集进行训练。模型都以多任务方式在单工具数据上进行训练。

## 🚀精调
### 安装
克隆这个仓库并进入ToolLLaMA文件夹。
```bash
git clone git@github.com:OpenBMB/ToolBench.git
cd ToolLLaMA
```
安装包 (python>=3.9)
```bash
pip install -r requirements.txt
```

### 数据预处理
请下载我们新发布的工具数据，并将其放置在 data/original/ 目录下。对于单工具数据的预处理，您可以使用以下命令来为精调准备数据：

```bash
python data/preprocess.py \
    --tool_mode single
    --tool_data_path data/original/weather_demo.json \
    --output_path data/processed/weather_demo.json
```
对于多工具数据的预处理，您可以使用以下命令：
```bash
python data/preprocess.py \
    --tool_mode multi
    --tool_data_path data/original/meta_file_demo.json \
    --output_path data/processed/meta_file_demo.json
```

### 训练
我们的代码基于FastChat。您可以使用以下命令来使用 4 个 A100（40GB）训练 ToolLLaMA-7b：
```bash
export PYTHONPATH=./
torchrun --nproc_per_node=4 --master_port=20001 toolbench/train/train_mem.py \
    --model_name_or_path huggyllama/llama-7b  \
    --data_path  data/processed/weather_processed.json \
    --bf16 True \
    --output_dir output \
    --num_train_epochs 3 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 8 \
    --evaluation_strategy "steps" \
    --eval_steps 1500 \
    --save_strategy "steps" \
    --save_steps 1500 \
    --save_total_limit 8 \
    --learning_rate 5e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.04 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --fsdp "full_shard auto_wrap" \
    --fsdp_transformer_layer_cls_to_wrap 'LlamaDecoderLayer' \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --lazy_preprocess True
```

## 推理

### 安装BMTools
工具执行由[BMTools](https://github.com/OpenBMB/BMTools)支持。首先在当前目录下克隆BMTools并进行配置：
```bash
git clone git@github.com:OpenBMB/BMTools.git
cd BMTools
pip install --upgrade pip
pip install -r requirements.txt
python setup.py develop
cd ..
```
接下来，在 secret_keys.sh 文件中添加您的API密钥，并启动本地工具：
```bash
source BMTools/secret_keys.sh
python BMTools/host_local_tools.py
```

### 使用命令行界面进行推理
准备API密钥和Python路径：
```bash
source BMTools/secret_keys.sh
export PYTHONPATH=BMTools
```
下面的命令需要大约14GB的GPU内存用于ToolLLaMA-7B。请将 /path/to/ToolLLaMA/weights替换为您转换后的ToolLLaMA的weights的路径：
- 单工具推理:
```bash
python toolbench/inference/inference_single_tool.py \
    --tool_name weather \
    --model_path /path/to/ToolLLaMA/weights
```
lora:
```bash
python toolbench/inference/inference_single_tool.py \
    --tool_name weather \
    --model_path /path/to/llama/weights \
    --lora_path /path/to/lora/weights
```
- 多工具推理:
```bash
python toolbench/inference/inference_multi_tools.py \
    --model_path /path/to/ToolLLaMA/weights
```


## 评测

ToolBench的总体思想是用我们的监督数据训练一个语言模型（LLM），然后能在[BMTools](https://github.com/OpenBMB/BMTools)中支持。
ToolBench的每个领域都有其自身的挑战，并需要特定的策略设计。

### 模型实验
- 机器评测

为构建我们的机器评估测试平台，我们从每个工具中随机抽样100个链路步骤。平均而言，其中有27个最终步骤和73个中间工具调用步骤。我们使用Rouge-L评估最终步骤，使用ExactMatch评估中间步骤。

| model_name                   | Downsampling | Beam size | Overall - Final Answer | Overall - Action | Overall - Input |
|------------------------------|--------------|-----------|------------------------|------------------|-----------------|
| cpmbee-finetuned             | 0.05         | 1         | **0.55**               | 0.64             | 0.40            |
| llama7b-finetuned            | 0.05         | 1         | 0.27                   | **0.77**         | 0.53            |
| vicuna7b-finetuned           | 0.05         | 1         | 0.42                   | 0.53             | 0.40            |
| llama7b-finetuned            | 0.5          | 1         | 0.35                   | 0.67             | 0.50            |
| llama7b-finetuned            | 0.7          | 1         | 0.29                   | 0.74             | **0.56**        |

- 人工评测

我们在以下工具中随机抽样了每个工具中的10个查询：天气（Weather）、地图（Map）、股票（Stock）、翻译（Translation）、化学（Chemical）和WolframAlpha。我们评估工具调用过程的通过率、最终答案以及最终答案与ChatGPT的比较。

| model_name                   | Downsampling | Beam size |  Tool Calling Process  |   Final Answer   |   Comparison   |
|------------------------------|--------------|-----------|------------------------|------------------|----------------|
| llama7b-finetuned            | 0.05         | 1         | **90%**                | **76.7%**        | 11.7%/60%/28.3%|


- ChatGPT评测

为了对LLaMA和ChatGPT的答案和工具链进行自动评估，我们使用ChatGPT进行评分。

要运行ChatGPT评估代码，请执行以下步骤：
```bash
python toolbench/evaluation/evaluate_by_chatgpt.py
```

ChatGPT的评测提示模版设计如下：
```
You are a fair AI assistant for checking the quality of the answers of other two AI assistants. 

    [Question] 

    {data['query']}

    [The Start of Assistant 1's Answer]

    llama chains: {data['llama_chains']}
    llama answer: {data['llama_answer']}

    [The End of Assistant 1's Answer]

    [The Start of Assistant 2's Answer]

    chatgpt chains: {data['chatgpt_chains']}
    chatgpt answer: {data['chatgpt_answer']}

    [The End of Assistant 2's Answer] 

    We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above. 
    Please first judge if the answer is correct based on the question, if an assistant gives a wrong answer, the score should be low.
    Please rate the quality, correctness, helpfulness of their responses based on the question.
    Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance, your scores should be supported by reasonable reasons. 
    Please first output a single line containing only two values indicating the scores for Assistant 1 and 2, respectively. 
    The two scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias, and the order in which the responses were presented does not affect your judgement.
    If the two assistants perform equally well, please output the same score for both of them.
```


以下是6个工具的15个案例的评估结果（较高的分数表示更好）。我们的ToolLLaMA在不同场景下与ChatGPT表现相当或更好。

| Tool                            | ToolLLaMA Score         | ChatGPT Score         |
| ------------------------------- | ------------------- | --------------------- |
| baidu-translation               | 8.0                 | 8.0                   |
| chemical-prop                   | 7.93                | 7.53                  |
| bing-map                        | 7.93                | 7.64                  |
| stock                           | 4.87                | 4.4                   |
| weather                         | 7.20                | 7.47                  |
| wolframalpha                    | 7.67                | 7.80                  |

## 待办事项
- [ ] 发布BMTools中其他工具的剩余部分数据。
- [ ] 使ToolLLaMA达到GPT-4的工具使用能力。
- [ ] ToolBench的中文版本。
- [ ] 支持中文LLM，例如CPM-bee。

## 待办事项
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
