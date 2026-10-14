import requests
import json
import re

def ask_model(model, prompt,timeout=120):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options":{"temperature":0, "seed":42}
    }
    
    response=requests.post(url, json=payload,timeout=timeout)
    if response.status_code != 200:
        raise Exception(f"Failed to ask model: {response.status_code} {response.text}")
    data = response.json()
    text = data["response"]
    eval_count = data["eval_count"]
    eval_duration = data["eval_duration"]
    token_per_s = eval_count / eval_duration *1e9
    return text, token_per_s, eval_count, eval_duration

def load_gsm8k(path, n):
    with open(path) as f:
        problems = []
        for line in f:
            if len(problems) == n:
                return problems
            json_line = json.loads(line)
            problems.append(json_line)
            
        return problems

def gold_answer(answer_text):
    parts=answer_text.split("####")
    final=parts[1].strip().replace(",", "")

    return float(final)

NUM = r'-?[\d,]*\.?\d+'
PROMPT_TEMPLATE = """
Answer the below Question step by step and include answer in the last line 
with the format "Answer:<number>"
Question: {question}
"""
def build_prompt(question):
    return PROMPT_TEMPLATE.format(question=question)

def parse_answer(text):
    m = re.search(r"Answer:\s*\$?(" + NUM + ")", text)
    if m:
        return float(m.group(1).replace(",","")), True
    nums = re.findall(NUM, text)
    if nums:
        return float(nums[-1].replace(",","")), False
    return None, False

if __name__ == "__main__":
    qs =load_gsm8k("data/gsm8k_test.jsonl",10)
    correct =0
    formatted = 0
    for i in range(len(qs)):
        p = build_prompt(qs[i]["question"])
        text, token_per_s, eval_count, eval_duration = ask_model("llama3.2:1b-instruct-q4_K_M", p)
        pred, ok = parse_answer(text)
        gold = gold_answer(qs[i]["answer"])
        if ok==True:
            formatted +=1
        if pred is not None and abs(pred - gold) < 1e-6:
            correct+=1
    print(f"format: {formatted/len(qs):.0%}  accuracy: {correct/len(qs):.0%}")
