# Automatic Evaluator
We build automatic annotator based on GPT-4 API to compare the results with Base Model.

## Human Cross-Annotations Dataset
We collect 600 entries, each with 4 human annotation, to compare the performance of automatic annotator with human annotator.

## Reference Model for Comparison
We select _gpt-3.5-turbo with CoT_ as reference model for comparison.

To compare performance of a method against reference model. You should:
1. prepare the generated answer for evaluation, the model_ouput should be a json file in following format:
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
2. change `CONFIG` in the python script `evaluate_model_outputs.py`, set the `model_output` to the file path of your model outputs, set `method` to your method name.
3. run the script `evaluate_model_outputs.py` to get final answers.

**Win Rate**: the win rate measures the fraction of time the model's output is preferred over reference outputs.
More specifically, to compute the win rate we collect pairs of outputs of the desired model on every query from the ToolLearning dataset.
We then pair each output with the output of our reference model on the same query.
We then ask our automatic evaluator which output they prefer.
We then average the preferences over all instructions in the dataset to get the win rate of the model over the reference model.

**Standard error**: this is the standard error (normalized by N-1) of the win rate, i.e., the preferences averaged over
the different instructions.


## Evaluators Comparison
