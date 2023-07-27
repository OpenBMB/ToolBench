TEST_PROMPT = '''
1.You are value-GPT. Please tell the following math numbers, which is higher.
2.First you may analyze the two candiates. 
3.Finally, You must exactly say which is higher in ONE word! Exactly say the word "candidate_1" or "candidate_2".
Use the format:
Analyze: xxx
Final Answer: "candidate_1" or "candidate_2"
now, here are the inputs:
candidate_1: {candidate_1}
candidate_2: {candidate_2}
'''


LLM_PAIRWISE_RANK_ALLCHAIN_SYSTEM_PROMPT = '''
You are value-GPT, which is an expert of defining which trail is better, which trail is more close to solving the task. Here is the task description:
*******************************
{{TASK_DESCRIPTION}}
{task_description}
{{END_TASK_DESCRIPTION}}
*******************************
Here are two candidates A and B, they both try to handle the task with some function calls, Their trails are as follows.
*******************************
{{CANDIDATE_A_START}}
{candidate_A}
{{CANDIDATE_A_END}}
*******************************
{{CANDIDATE_B_START}}
{candidate_B}
{{CANDIDATE_B_END}}
'''

LLM_PAIRWISE_RANK_SUBFIX_SYSTEM_PROMPT = '''
You are value-GPT, which is an expert of defining which trail is better, which trail is more close to solving the task. 
All candidate tries to solve this task with some funciton calls:
*******************************
{{TASK_DESCRIPTION}}
{task_description}
{{END_TASK_DESCRIPTION}}
*******************************
First, all candidate do the following things:
{intersect_trice}
After that, there are two candidates A and B, they do different things:
*******************************
{{CANDIDATE_A_START}}
{candidate_A}
{{CANDIDATE_A_END}}
*******************************
{{CANDIDATE_B_START}}
{candidate_B}
{{CANDIDATE_B_END}}
Which try do you think is more helpful to solving the task?
'''




LLM_PAIRWISE_RANK_USER_PROMPT = '''
Tell me which candidate is better in ONE Word: "A" or "B":'''