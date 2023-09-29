<div align= "center">
    <h1> 🛠️Tool Eval🤖</h1>
</div>

通过在ToolBench上对LLaMA进行微调，我们得到了**ToolLLaMA**。考虑到人工评估非常耗时，我们借鉴[AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/)开发了一个高效的机器自动评估**ToolEval**，其中包含两个评估指标：

- **通过率**：计算在有限的OpenAI API调用次数内成功完成指令的比例。

- **偏好**：通过比较给定指令的两个答案（动作序列）来衡量。我们预先定义了一组更好答案的标准，这些标准被组织成ChatGPT的提示。我们向评估器提供测试指令和两个候选答案，并获得其偏好。我们对每个答案对进行多次评估以提高系统的可靠性。然后，我们计算**优胜率**（被评估器选择为更优的百分比。有关详细信息，请参阅我们的论文。

为了验证ChatGPT评估器在通过率和胜率方面的可靠性，我们从四种不同的方法（ChatGPT+ReACT，ChatGPT+DFSDT，ToolLLaMA+DFSDT和GPT4+DFSDT）中进行采样，为每种方法的300个测试指令获取解决方案对。然后，我们请人类标注ChatGPT+DFSDT，ToolLLaMA+DFSDT和GPT4+DFSDT的通过率，以及ChatGPT+ReACT和ChatGPT+DFSDT之间的胜率。

我们的ChatGPT评估器在通过率方面与人类标注者具有高达**87.1%**的一致性，在胜率方面具有**80.3%**的一致性。这个结果表明，我们的评估器生成的评估结果与人类非常相似，并且可以视为在通过率和胜率上模拟人类评估的可靠评估器。
有关ToolEval的更多细节，请参阅我们的论文。

## 🚀用法

### Install
Install Package (python>=3.9)
```bash
pip install -r requirements.txt
```

### Evaluation
*若要复现结果，直接通过[Google Drive](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J)下载我们的`reproduction_data.zip`，解压后置`reproduction_data`于`ToolBench/data/`下即可，可以跳过数据准备流程。*
- 数据准备。若要使用 ToolEval 评估您自己的模型和方法，首先需要为六个测试子集准备所有的模型预测。创建一个以您的模型和方法命名的目录，例如 `chatgpt_cot`，然后将每个测试集的预测放在该目录下。目录的文件结构应如下：
```
├── /chatgpt_cot/
│  ├── /G1_instruction/
│  │  ├── /10160_CoT@1.json
│  │  └── ...
│  ├── /G1_tool/
│  │  ├── /10221_CoT@1.json
│  │  └── ...
│  ├── ...
│  ├── /G3_instruction/
│  │  ├── /10221_CoT@1.json
│  │  └── ...
```

然后对模型预测进行预处理:

```bash
export RAW_ANSWER_PATH=../../data/reproduction_data/model_predictions/
export CONVERTED_ANSWER_PATH=../../data/reproduction_data/model_predictions_converted/
export MODEL_NAME=chatgpt_cot
export METHOD=CoT
mkdir ${CONVERTED_ANSWER_PATH}/${MODEL_NAME}
for test_set in G1_instruction G1_category G1_tool G2_category G2_instruction G3_instruction
do
    answer_dir=${RAW_ANSWER_PATH}/${MODEL_NAME}/${test_set}
    output_file=${CONVERTED_ANSWER_PATH}/${MODEL_NAME}/${test_set}.json
    python convert_to_answer_format.py\
        --answer_dir ${answer_dir} \
        --method ${METHOD} \
        --output ${output_file}
done
```
之后，检查`${CONVERTED_ANSWER_PATH}/${MODEL_NAME}`下是否有测试集的预处理JSON文件。如果有，你就可以准备运行以下评估过程了。如果没有，请检查模型的预测是否有问题。

- OpenAI Key
准备您的OpenAI Key来搭建我们的evaluator。Key需要被存储到一个json file中，如`path/to/your/openai_key_json_file.json`：
```bash
[
    {
        "username": "your_user_name",
        "passwd": "your_password",
        "api_key": "your_openai_key",
        "organization": "your_organization"
    },
    ...
]
```
- Pass rate.
```bash
export CONVERTED_ANSWER_PATH=../../data/reproduction_data/model_predictions_converted/
export SAVE_PATH=pass_rate_results
export CANDIDATE_MODEL=chatgpt_cot
export API_POOL_FILE=path/to/your/openai_key_json_file.json

python eval_pass_rate.py \
    --converted_answer_path ${CONVERTED_ANSWER_PATH} \
    --save_path ${SAVE_PATH} \
    --reference_model ${CANDIDATE_MODEL} \
    --test_ids ../../data/test_query_ids/ \
    --max_eval_threads 20 \
    --evaluate_times 4

```

结果文件会被存储至${SAVE_PATH}中。

- Win rate. 以下示例以ChatGPT-ReACT作为参考模型，GPT4-ReACT作为候选模型。请注意，您首先需要获取两个模型的pass rate结果，然后运行以下命令来评估GPT4-ReACT的win rate结果:
```bash
export CONVERTED_ANSWER_PATH=../../data/reproduction_data/model_predictions_converted/
export SAVE_PATH=preference_results
export PASS_TARE_PATH=pass_rate_results
export REFERENCE_MODEL=chatgpt_cot
export CANDIDATE_MODEL=gpt-4-0613_cot
export API_POOL_FILE=path/to/your/openai_key_json_file.json

python eval_preference.py \
    --converted_answer_path ${CONVERTED_ANSWER_PATH} \
    --reference_model ${REFERENCE_MODEL} \
    --output_model ${CANDIDATE_MODEL} \
    --test_ids ../../data/test_query_ids/ \
    --save_path ${SAVE_PATH} \
    --pass_rate_result_path ${PASS_TARE_PATH} \
    --max_eval_threads 20 \
    --use_pass_rate true \
    --evaluate_times 4
```

结果文件会被存储至${SAVE_PATH}中。

### 评估新方法
要评估除了ReACT和DFSDT之外的方法，您需要遵循以上Data preparation的步骤准备您的预处理好的answer数据。预处理好的answer数据需遵循以下json格式:

```json
[
    {
        "method":"method name",
        "total_steps": int, // a integer count total steps in answer details
        "final_answer": "final answer from the method",
        "answer_details":[{
            "role":"node role, can be system, user, assistant and tool",
            "message":"message for the node",
            "next":[//next steps, can have multiple elements if the node have multiple candidates.
                {
                    "role":"",
                    "message":"",
                    "next":[...]
                },
                ...//more candidates
            ]
        }]
    }
    ... // more answers for the give query in the testdata
]
```


### 更新排行榜

如果您想将您的模型的结果上传到[ToolEval Leaderboard](https://openbmb.github.io/ToolBench/)，请您将您的结果文件整理成上述格式发送给我们（urtoolbench@gmail.com）或者开一个pull request。
我们将运行评测脚本更新结果并将您的模型添加到排行榜中。


### 创建新的自动评估器
如果您想创建新的自动评估器，您需要按下列步骤进行：
1. 在路径`toolbench/tooleval/evaluators`下创建一个评测器配置文件目录，命名与你的评测器名一致。在其中添加`config.yaml`文件与`template.txt`文件。具体配置方式可参考`toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized`中的实现。
2. 创建你的evaluator类并实现`fn_completions`函数在文件夹`toolbench/tooleval/evaluators/registered_cls`中，或者你可以使用我们预先定义好的类例如`OpenAINormalizedEvaluator`。
完成后将配置文件中`registered_cls_name`字段填写为该类的名称。
这里给出一个例子：
```Python
from evaluators import register_evaluator,BaseEvaluator
from typing import Dict,List

@register_evaluator
class MyEvaluator(BaseEvaluator):
    def __init__(self,config):
        super().__init__(
            fn_completions=self.fn_completions,
        )
        # set your configures here
    
    def fn_completions(self,query:Dict,answers:List[Dict])->int:
        # implement your evaluator here
        # return the index of the preferred answer
        return 0
```
其中register_evaluator是一个装饰器，用于注册评估器，BaseEvaluator是一个基类，用于实现评估器的基本功能。
3. 测试评估器的性能，运行脚本`evaluators_comparison.py`。
