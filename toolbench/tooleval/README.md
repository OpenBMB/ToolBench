<div align= "center">
    <h1> 🛠️Tool Eval🤖</h1>
</div>

By fine-tuning LLaMA on ToolBench, we obtain **ToolLLaMA**. Considering that human evaluation can be time-consuming, we follow [AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/) to develop an efficient machine evaluator **ToolEval**, which incorporates two evaluation metrics:
 - **Pass Rate**: Calculates the proportion of successfully completing an instruction within limited OpenAI API calls. 
 - **Preference**: Measured by comparing two answers (action sequences) for a given instruction. We pre-define a set of criteria for a better answer, which are organized as prompts for ChatGPT. We provide the test instruction and two candidate answers to the evaluator and obtain its preference. We evaluate each answer pair multiple times to improve the reliability of our system. Then we calculate the **Win Rate** (percentage of being preferred by the evaluator). More details can be found in our paper.

To validate the reliability of ChatGPT evaluator in both pass rate and win rate, we sample among four different methods (ChatGPT+ReACT, ChatGPT+DFSDT, ToolLLaMA+DFSDT and GPT4+DFSDT) to obtain solution pairs for 300 test instructions for each method. Then we engage humans to annotate the pass rate for ChatGPT+DFSDT, ToolLLaMA+DFSDT and GPT4+DFSDT, and the win rate among ChatGPT+ReACT and ChatGPT+DFSDT.
Our ChatGPT evaluator demonstrates a high agreement of **87.1%** in pass rate and **80.3%** in win rate with human annotators. This result shows that our evaluator generates highly similar evaluation results to humans and can be viewed as a credible evaluator who simulates human evaluation on pass rate and win rate.

## 🚀Usage
### Install
Install Package (python>=3.9)
```bash
pip install -r requirements.txt
```

### Evaluation
*If you want to reproduce the official results, download the reproduction data `reproduction_data.zip` through [Google Drive](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J), unzip it and put the `reproduction_data` under `ToolBench/data/`, and skip the data preparation process.*
- Data preparation. To evaluate your own model and method using ToolEval, first you need to prepare all the model predictions for the six test subsets. Create a directory naming with your model and method, e.g. `chatgpt_cot` then put each test set's predictions under the directory. The file sturcture of the directory should be:
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

Then preprocess the predictions by running the following commands:
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
After that, check if there are preprocessed json files for the test sets under `${CONVERTED_ANSWER_PATH}/${MODEL_NAME}`. If so, you're ready to run the following evaluate process. If not, check if there is anything wrong with the model's predictions.

- OpenAI Key. Prepare your openai key to use our evaluator. The key(s) should be stored in a json file, e.g. `path/to/your/openai_key_json_file.json`:
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

- Pass rate:
```bash
export CONVERTED_ANSWER_PATH=../../data/reproduction_data/model_predictions_converted/
export SAVE_PATH=pass_rate_results
export CANDIDATE_MODEL=chatgpt_cot
export API_POOL_FILE=path/to/your/openai_key_json_file.json

python eval_pass_rate.py \
    --converted_answer_path ${CONVERTED_ANSWER_PATH} \
    --save_path ${SAVE_PATH} \
    --reference_model ${CANDIDATE_MODEL} \
    --test_ids ../../data/test_ids/ \
    --max_eval_threads 20 \
    --evaluate_times 4

```
The result files will be stored under the ${SAVE_PATH}.

- Win rate. The below example take ChatGPT-ReACT as reference model and GPT4-ReACT as candidate model. Notice that you need to get both model's pass rate results first, then run the following commands to evaluate the preference result of GPT4-ReACT:
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
    --test_ids ../../data/test_ids/ \
    --save_path ${SAVE_PATH} \
    --pass_rate_result_path ${PASS_TARE_PATH} \
    --max_eval_threads 20 \
    --use_pass_rate true \
    --evaluate_times 4
```
The result files will be stored under the ${SAVE_PATH}.

### Evaluate New Method
To evaluate with a new method besides ReACT and DFSDT, you should prepare your converted answer for evaluation following the above Data preparation step. The converted answers should be a json file in following format:

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

### Update the Leaderboard

To update the [ToolEval Leaderboard](https://openbmb.github.io/ToolBench/), you should submit your converted answer file (`${CONVERTED_ANSWER_PATH}/${MODEL_NAME}`) to us (urtoolbench@gmail.com) in above format or open a pull request.
We will run the evaluation script to get the result and update the leaderboard.     


### Create new Automatic Evaluators
To create new automatic evaluators, you can following the steps below:
1. Create a config folder under `toolbench/tooleval/evaluators`, name it with the name of your evaluators.
Adding a `config.yaml` file (must have) and a `template.txt` file (optional) in the folder.
You can refer to the `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized` folder for example. 
2. Create your own evaluator class and implement the `fn_completions` function in folder `toolbench/tooleval/evaluators/registered_cls` if needed.
Or you can use the precreated class like `OpenAINormalizedEvaluator`.
Fill the `registered_cls_name` with class name of the evaluator in your `config.yaml`.
Here is a example of the evaluator class: 
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
The wrapper `register_evaluator` will register your evaluator to the available evaluators.

3. Run the script `evaluators_comparison.py` to test the performance of your evaluators.
