<div align= "center">
    <h1> 🛠️Tool Eval🤖</h1>
</div>

By fine-tuning LLaMA on ToolBench, we obtain **ToolLLaMA**. Considering that human evaluation can be time-consuming, we follow [AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/) to develop an efficient machine evaluator **ToolEval**, which incorporates two evaluation metrics:
 - **Pass Rate**: Calculates the proportion of successfully completing an instruction within limited OpenAI API calls. 
 - **Preference**: Measured by comparing two answers (action sequences) for a given instruction. We pre-define a set of criteria for a better answer, which are organized as prompts for ChatGPT. We provide the test instruction and two candidate answers to the evaluator and obtain its preference. We evaluate each answer pair multiple times to improve the reliability of our system. Then we calculate the **Win Rate** (percentage of being preferred by the evaluator) and **Standard Error** (the standard error of the Win Rate). More details can be found in our paper.

To validate the effectiveness of the metric **Preference**, we sample among three different methods (ChatGPT+ReACT, GPT4+ReACT, and ChatGPT+DFSDT) to obtain answer pairs for *600* test instructions. Then we engage humans to annotate human preference for them (*4* annotations for each answer pair, *2400* annotations in total).
Our automatic evaluator, developed using ChatGPT, demonstrates a significant correlation of **75.8%** with human annotators.
We also obtain the agreement among different human annotators **83.54%**, and the agreement between humans and our evaluator **80.21%**.

## 🚀Usage

### Reproduce our Results

To evaluate a model on G1-Inst. test set, for example, run the following commands.
- Pass rate:
```bash
python pass_rate.py --answer_dir data/answer/toolllama_dfs/G1_instruction
```
- Win rate (Reference model: ChatGPT-ReACT):
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

### Evaluate New Method

The calculation of pass rate is depended on specific method, so we skip the pass rate calculation here.
To calculate the win rate, you should:

1. Prepare the reference model's answer. You can find the reference answer of `ChatGPT-ReACT` for our default test set in here [Data](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J).
Note that the downloaded data should be converted with the script `convert_to_answer_format.py` before using it as reference model's answer.

2. Prepare your generated answer for evaluation, the result should be a json file in following format:

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

3. Run the evaluation script to get result:

```bash
python automatic_eval_sample.py \
    --output ${REF_MODEL_DATA} \
    --ref_output ${TEST_MODEL_DATA} \
    --method ${TEST_MODEL_METHOD} \
    --ref_method ${REF_MODEL_METHOD} \
    --use_existed_output
```


### Update the Leaderboard

To update the [ToolEval Leaderboard](https://openbmb.github.io/ToolBench/), you should submit your answer file to us (urtoolbench@gmail.com) in above format.
We will run the evaluation script to get the result and update the leaderboard.

Sepcifically, you should provide the following information in your submission email:
```
Method Name:
Method Link : (Optional)
Test Set : (default to data/test_query_ids)
Comparison Method Name : (default: ChatGPT-ReACT) 
Answer Files Link : (shuold contain 6 json files for each subset in Test Set)
```

We will run the script `eval_and_update_leaderboard.py` to valid your submission and update the leaderboard.
```bash
python eval_and_update_leaderboard.py \
    --evalset default_evalset \
    --method your_method_name \
    --ref_method ref_method_name \
    --result_folder your_answer_files \
    --ref_result_folder ref_results_files  \
```


## 🔨Evaluate Automatic Evaluators

To validate the effectiveness of the automatic evaluator, we collect a human cross-annotations dataset and compare the performance of automatic annotator with human annotator.

### Human Cross-Annotations Dataset
The dataset contains 600 comparison pairs, each pair is annotated by 4 human annotators.
We randomly sample 600 instructions from the ToolBench dataset and randomly select 2 answers for each instruction from answers generated by 3 different methods (ChatGPT+ReACT, GPT4+ReACT, and ChatGPT+DFSDT).
Then we engage 4 human annotators to annotate the preference between the two answers for each instruction.
The dataset can be found in [Data](https://drive.google.com/drive/folders/1yBUQ732mPu-KclJnuQELEhtKakdXFc3J).

### Performance of Automatic Evaluators
We evaluate the performance of automatic evaluator on the human cross-annotations dataset with the script `evaluators_comparison.py`.
The script calculate four metrics for the evaluators, we adopt metrics **Human Agreement**, **Bias** and **Variance** from [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval/tree/main)
:
- **Human Agreement** measures the agreement between the current annotator and the majority preferences of humans on our cross-annotations dataset.
- **Bias** measures the agreement between the most likely human label and the most likely automatic one.
- **Variance** measures the unstablility of the automatic evaluator.
- **Correlation** measures the pearson correlation between the automatic evaluator and human annotators.


The result is shown below:
| Evaluator                   | Human Agreement(%) | Bias | Variance | Correlation |
|-------------------------|----------|----------|---------|----------
| Human          | **83.54**   | 0.0  | 3.97  | N/A   
| tooleval gpt-3.5-turbo normalized           | 80.21       | 19.3       | 3.47      | 0.7580       
| tooleval gpt-3.5-turbo fn  | 63.75       | 36.5       | 9.52      | 0.5308       


### Create new Automatic Evaluators
To create new automatic evaluators, you should create a config folder under `toolbench/tooleval/evaluators` and adding your `completions_fn` to the class `AutomaticEvaluator` in `toolbench/tooleval/evaluators/evaluator.py`.

To test your evaluator, you can run the script `evaluators_comparison.py` for your evaluator.
