import requests
import json
import re
import pandas as pd

MODELS = [
    # 问题 1:每少一位精度,准确率掉多少(llama3.2 1B,5 个精度)
    "llama3.2:1b-instruct-q3_K_M",
    "llama3.2:1b-instruct-q4_K_M",
    "llama3.2:1b-instruct-q6_K",
    "llama3.2:1b-instruct-q8_0",
    "llama3.2:1b-instruct-fp16",
    # 问题 2:QAT 和普通 Q4 比(gemma3 1B)
    "gemma3:1b-it-qat",
    "gemma3:1b-it-q4_K_M",
    "gemma3:1b-it-fp16",
    # 问题 3:同样约 2 GB,选大模型压缩还是小模型不压缩(qwen3.5 2B)
    "qwen3.5:2b-q4_K_M",
    "qwen3.5:2b-q8_0",
]

def ask_model(model, prompt,timeout=120):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options":{"temperature":0, "seed":42},
        "think": False
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
    rows =[]
    qs =load_gsm8k("data/gsm8k_test.jsonl",2)
    for model in MODELS:
        for i in range(len(qs)):
            row ={}
            row["model"]=model
            p = build_prompt(qs[i]["question"])
            text, token_per_s,eval_count,eval_duration  = ask_model(model, p)
            pred, ok = parse_answer(text)
            gold = gold_answer(qs[i]["answer"])
            row["correct"] = pred is not None and abs(pred - gold) < 1e-6
            row["gold"]=gold
            row["pred"]=pred
            row["formatted"]= ok
            row["item_id"] = i
            row["token_per_s"] = token_per_s
            row["eval_count"] = eval_count
            row["eval_duration"] = eval_duration
            row["response"]=text
            rows.append(row)
    pd.DataFrame(rows).to_csv("results/gsm8k_raw.csv", index=False)
