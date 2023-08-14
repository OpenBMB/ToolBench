<div align= "center">
    <h1> 🛠️Tool Eval🤖</h1>
</div>

通过在ToolBench上对LLaMA进行微调，我们得到了**ToolLLaMA**。考虑到人工评估非常耗时，我们借鉴[AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/)开发了一个高效的机器自动评估**ToolEval**，其中包含两个评估指标：

- **通过率**：计算在有限的OpenAI API调用次数内成功完成指令的比例。

- **偏好**：通过比较给定指令的两个答案（动作序列）来衡量。我们预先定义了一组更好答案的标准，这些标准被组织成ChatGPT的提示。我们向评估器提供测试指令和两个候选答案，并获得其偏好。我们对每个答案对进行多次评估以提高系统的可靠性。然后，我们计算**优胜率**（被评估器选择为更优的百分比）和**标准差**（优胜率的标准误差）。有关详细信息，请参阅我们的论文。

为了验证偏好指标的有效性，我们从三种不同方法（ChatGPT+ReACT、GPT4+ReACT和ChatGPT+DFSDT）中随机抽样获得600个测试指令的答案对。然后，我们邀请人工标注人员对它们进行人工偏好注释（每个答案对4个注释，总共2400个注释）。我们使用ChatGPT开发的自动评估器与人工标注者呈现出显著的**75.8%**相关性。我们还获得了不同人工标注者之间的一致性为**83.54%**，与我们的评估器和人类标注者之间的一致性为**80.21%**。

有关ToolEval的更多细节，请参阅我们的论文。

## 🚀用法

### 安装
安装包，要求(python>=3.9)
```bash
pip install -r requirements.txt
```

### 复现结果

要在测试集（如G1-Inst.）上评估模型，可以执行以下命令：
- 通过率:
```bash
python pass_rate.py --answer_dir data/answer/toolllama_dfs/G1_instruction
```
- 优胜率 (参考模型: ChatGPT-ReACT):
```bash
export OPENAI_KEY=""
export REF_MODEL_DATA="data/answer/chatgpt_cot/G1_instruction"
export REF_MODEL_METHOD="CoT"
export TEST_MODEL_DATA="data/answer/toolllama_dfs/G1_instruction"
export TEST_MODEL_METHOD="DFS"
python convert_to_answer_format.py \
    --method CoT \
    --answer_dir ${REF_MODEL_DATA} \
    --output ${REF_MODEL_DATA}_converted

python convert_to_answer_format.py \
    --method DFS \
    --answer_dir ${TEST_MODEL_DATA} \
    --output ${TEST_MODEL_DATA}_converted

python automatic_eval_sample.py \
    --output ${REF_MODEL_DATA}_converted \
    --ref_output ${TEST_MODEL_DATA}_converted \
    --method ${TEST_MODEL_METHOD} \
    --ref_method ${REF_MODEL_METHOD} \
    --use_existed_output
```

### 评估新方法

通过率的计算方式取决于特定的方法或模型，请参考有关通过率的说明与代码计算通过率。
这里我们介绍优胜率的计算方式：

1. 准备参考模型的答案，我们将`ChatGPT-ReACT`模型在我们的默认测试集上的结果上传到了[Data](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J)。
请注意，下载的答案首先需要通过脚本`convert_to_answer_format.py`转换为评测结构的格式，再用于评测。
2. 按下面的格式准备待评测的答案：
```json
[
    {
        "method":"method name",
        "total_steps": int, // 一个整数，记录answer_details的总步数
        "final_answer": "final answer from the method",
        "answer_details":[{
            "role":"node role, can be system, user, assistant and tool",
            "message":"message for the node",
            "next":[// 下一步，如果有多个候选步，可以有多个元素
                {
                    "role":"",
                    "message":"",
                    "next":[...]
                },
                ...//更多候选步
            ]
        }]
    }
    ... // 其他答案
]
```
请注意，答案的顺序需要保持和参考模型的答案顺序一致。
3. 执行评测脚本：
```bash
python automatic_eval_sample.py \
    --output ${REF_MODEL_DATA} \
    --ref_output ${TEST_MODEL_DATA} \
    --method ${TEST_MODEL_METHOD} \
    --ref_method ${REF_MODEL_METHOD} \
    --use_existed_output
```

### 更新排行榜

如果您想将您的模型的结果上传到[ToolEval Leaderboard](https://openbmb.github.io/ToolBench/)，请您将您的结果文件整理成上述格式发送给我们（urtoolbench@gmail.com）。
我们将运行评测脚本更新结果并将您的模型添加到排行榜中。

具体来说，您需要提供下列信息：
```
Method Name : 方法名称
Method Link : 方法链接，可选
Test Set : (测试集，默认为data/test_query_ids中的6个集合)
Comparison Method Name : (参考模型，默认为ChatGPT-ReACT) 
Answer Files Link : (结果文件下载链接，应该包含6个json文件，对应测试集中的6个子集合)
```

我们将运行脚本`eval_and_update_leaderboard.py`验证结果并更新排行榜，您也可以在本地运行该脚本查看结果。
```bash
python eval_and_update_leaderboard.py \
    --evalset default_evalset \
    --method your_method_name \
    --ref_method ref_method_name \
    --result_folder your_answer_files \
    --ref_result_folder ref_results_files  \
```

## 🔨评估自动评估器
为了验证自动评估器的有效性，我们收集了600个测试指令的答案对，然后邀请人工标注人员对它们进行人工偏好注释（每个答案对4个注释，总共2400个注释）。

### 人类交叉标注数据集
该数据集包含600个答案对，每个答案对由4个人类标注者标注。
我们随机从ToolBench数据中选择了600个测试指令，并随机从3个不同方法（ChatGPT+ReACT，GPT4+ReACT 和 ChatGPT+DFSDT）的结果中挑选2个答案组成答案对。
然后我们对每个答案邀请4个人类标注者进行偏好选择，每个标注者都会看到一个答案对，然后选择他们认为更好的答案。
原始数据集可从[这里](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J)下载。

### 自动评估器性能
我们使用人类交叉标注数据集评估了自动评估器的性能。
评测脚本`evaluators_comparison.py`为自动评估器计算了4个指标，其中 **人类赞同率**，**偏差**和**方差**是从[AlpacaEval](https://github.com/tatsu-lab/alpaca_eval/tree/main)中借鉴的。
- **人类赞同率** 代表了当前评估者和主要人类偏好的一致性，越高越一致。
- **偏差** 计算了主要人类偏好和主要评估器偏好的一致性，越低一致性越高。
- **方差** 计算了评估器的不稳定性，越低越稳定。
- **相关系数** 是自动评估器和人类评估者之间的皮尔逊相关系数，越高越相关。

评测结果如下：
The result is shown below:
| 评估器                   | 人类赞同率(%) | 偏差 | 方差 | 相关系数 |
|-------------------------|----------|----------|---------|----------
| Human          | **83.54**   | **0.0**  | 3.97  | N/A   
| tooleval gpt-3.5-turbo normalized           | 80.21       | 19.3       | **3.47**      | **0.7580**       
| tooleval gpt-3.5-turbo fn  | 63.75       | 36.5       | 9.52      | 0.5308       

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
