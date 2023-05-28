import json
import openai
import logging
import os
import numpy as np
import requests
from multiprocessing import Pool, cpu_count

openai.api_key = 'YOUR_OPENAI_KET'
directory = r'./chatgpt_evaluation_6tools_15'
out_directory = r'./evaluate_logs'

def get_prompt(data):
    return f"""
    You are a fair AI assistant for checking the quality of the answers and quality of its use of tools of other two AI assistants. 

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
    """

def call_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a fair AI assistant for checking the quality of the answers of other two AI assistants."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message['content']

def process_file(filename):
    
    logging.basicConfig(filename=os.path.join(out_directory, f'{os.path.splitext(filename)[0]}.log'), level=logging.INFO)

    with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
        data = json.load(file)

    scores1 = []
    scores2 = []

    for i, item in enumerate(data):
        prompt = get_prompt(item)
        try:
            response = call_chatgpt(prompt)
            scores, reasoning = response.split('\n', 1)
            score1, score2 = map(float, scores.split())
            scores1.append(score1)
            scores2.append(score2)

            logging.info(f"Question {i + 1}")
            logging.info(f"Scores: Assistant 1: {score1}, Assistant 2: {score2}")
            logging.info(f"Reasoning: {reasoning}\n")
        except:
            continue

    logging.info(f"Average score for Assistant 1 (Llama): {np.mean(scores1)}")
    logging.info(f"Average score for Assistant 2 (ChatGPT): {np.mean(scores2)}")

def main():
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    with Pool(cpu_count()) as p:
        p.map(process_file, files)

if __name__ == "__main__":
    main()