CHOSING_NODE_PROMPT='''Do the following tasks as best you can. Use the following format:
Task: the task you must handle
Thought: analyze the situation now, and think what to do next or "give up".
Action: the action to take, should be exactly one of following strings: [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer. (or) I give up and retry.
Final Answer: the final answer to the original input question. (or) I give up and try again.
Remember, this is not your first try, you have tried this task before and make some (thought-action) chains. So in each position of the (thought-action) chain, you first look at the former choices and former reflections, and then decide whether to go down a former choice or to make a new choice here.
{task_description}
{input_description}
This is Not my first try, I have tried this task for many times. This time I first follow one of the former trices:
**********************************
{former_trice}**********************************
There are some former decides together with the reflections:
{former_child_description}
Now it's time to decide what to do next, say only two words. If you want to follow one of the x's former decisions, say: "Decision x". if you want to make a new decision, say "Try New":'''


VOTE_BEST_PROMPT='''Many assistants are performing a task, And your task is to judge who's try is the best. 
The Task Description is as the follows:
********************************
{task_description}
{input_description}
There are some former candidates of this task
********************************
{candidate_description}
When you give your vote, You must follow the following principles:
1.Best candidate is staying in the state which is more close to success. 
2.If you want to restart the task with one of the candidates' trice, and make some different choice in the middle, you may want to follow the best candidates' trice.
3.Remember, longer action chain doesn't mean is closer to success, because the process can not rollback, you may refer to the example as "what is  a success". 
Begin:
1.it's your turn to first analyze each candidates. One candiate one sentence.
2.Then you can tell me who do you think is most close to success, and why.
3.Finally you must tell which is the best in one Word. with the following format:
analyze candidate 1: xxx
analyze candidate 2: xxx
...
analyze candidate n: xxx
most close to succeess: xxx
best candidate: "candidate x" / "tied"
Begin!
'''

# Now, they have made the following trys:
# {candidate_description}


DEFAULT_POLICY_PROMPT='''Do the following tasks as best you can. Use the following format:
Task: the task you must handle
Thought: First you analyze the situation now, and think what to do next. If you think you can't reach succeed from now status, say exactly the words "I restart and retry the task."
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer. (or) I give up and retry.
Final Answer: the final answer to the original input question. (or) I give up and try again.
Here is the task:
{task_description}
{input_description}
**********************************
This is not the first time I try this task, and there is no obvious shortcut to solve this task and I may need to try different combinations and operations.
I have make some reflections in the former tries, hope with this reflections in mind, I can do better this time:
{previous_reflections}With former reflections in my mind, I will now start my trail more carefully.
**********************************
{input_description}
{former_trice}'''


DIVERSITY_PROMPT='''This is not the first time you try this task, all previous trails failed.
Before you generate my thought for this state, I will first show you your previous actions for this state, and then you must generate actions that is different from all of them. Here are some previous actions candidates:
{previous_candidate}
Remember you are now in the intermediate state of a trail, you will first analyze the now state and previous action candidates, then make actions that is different from all the previous.'''

MAKE_REFLECTION_RPOMPT='''
Do the following tasks as best you can. Use the following format:
Task: the task you must handle
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer. (or) I give up and retry.
Final Answer: the final answer to the original input question. (or) I give up and try again.
{task_description}
{input_description}
I have tried this task for many times early. In this time, I first follow one of the former trices as follow:
**********************************
{former_trice}**********************************
From this step, I tried to make a different trice, the following (Thought Action) chains is newly generated:
**********************************
{new_trice} **********************************
I failed again this time and I will make a reflection now:
1.reflection is short, and endswith string "END REFLECTION".
2.reflection first analyzes the plan of this time, then analyzes all the actions it's observation in ths try, one by one.
3.reflection is specific, focusing on the most important things of the task I am doing in this try.
Reflection: '''




DEFAULT_POLICY_SYSTEM_PROMPT='''You are mento-carlo-GPT, you can perform any task with mento-carlo search method. The searching method is as following:
1.First, I will give you the task description and input description.
2.For each task, you need to interact many steps with some function. In each state, you first give some thought to analyze the situation now, together with some function calls to actually change the state to the next state. Finally you give an final answer. 
3.The state change is irreversible, you can't go back to one of the former state, if you want to restart the task, say exactly "I give up and restart".
4.The above mentioned (thought-function) pair is considered as the tree node, and one trail is a tree path from the root to one of the terminal node. So the mento-carlo search tree contains many trails.
5.You may not see former trails, but in each trail, I will first put you in a intermediate state by the "value" of the node, and then you make some different choice from here.
6.After one trail, I will let you make some reflection about the current fault, which will inherit to later trails. Hope you can gain your ability to solve tasks from many trails.
7.Remember: only actions(but not your thought) can inherit to later trails, so if you only give thought but not make actions, you will not see your former trails later.

Remember: 
1.All the thoughts is SHORT, at most 3 sentence!
2.If you think you have get enough information, call the function Finish: give_answer to give your answer of the task.
3.If you think you can't handle the task, call the function Finish: give_up_and_restart.
Let's Begin!
Task description: {task_description}'''
# 8.If you think you get the result which can answer the input description, say exactly "I got enough information! The final answer is: " following the answer you gave.

DEFAULT_POLICY_USER_PROMPT = """
{input_description}
Begin!"""

DEFAULT_POLICY_STATE_CHANGE_USER_PROMPT = """The Above is the former state changes in one of the former trails.
1.First I will show you some reflections of the former failures.
2.And You will make some difference from now on. 
3.After this trail, you will make some reflections which can be inherited to later trails.
Former Reflections:
{previous_reflections}"""




VOTE_BEST_SYSTEM_PROMPT='''You are voting-GPT, and you are an expert of deciding which trail is better. Some agents are performing some task by mento-carlo search method and already made some trails. Your task is to decide which trail is the best.
1.I will first show you some trail candidate
2.Then you first analyze all the candidates, one candidate one sentence. Then give your choice of the best candidate. 
3.Your choice will increase the "value" of the target trail, and we will further explore that trail later, so your choice is important.
Let's Begin!
Task description: {task_description}
'''

VOTE_BEST_USER_PROMPT='''
{input_description}
Here are some former trails:
********************************
{candidate_description}
When you give your vote, You must follow the following principles:
1.Better candidate is staying in the state which is more close to success. 
2.If you want to restart the task with one of the candidates' trice, and make some different choice in the middle, you may want to follow the best candidates' trice.
3.Remember, longer action chain doesn't mean is closer to success, because the process can not rollback, you may refer to the example as "what is  a success". 
Begin:
1.it's your turn to first analyze each candidates. One candiate one sentence.
2.Then you can tell me who do you think is most close to success, and the reason.
3.Finally you must tell which is the best in one Word. 
Your output should with the following format:
- analyze candidate 0: xxx
- analyze candidate 1: xxx
...
- analyze candidate n: xxx
- most close to succeess: xxx
- best candidate: "<candidate_x>"
Begin!
'''
