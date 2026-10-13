import requests
import json

def ask_model(model, prompt,timeout=120):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
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

if __name__ == "__main__":
    qs =load_gsm8k("data/gsm8k_test.jsonl",5)
    text, token_per_s, eval_count, eval_duration = ask_model("llama3.2:1b-instruct-q4_K_M", "What is 17 * 23? Answer with only the number.")
    print(text)
    print(gold_answer(qs[0]["answer"]))
    print(len(qs))
    print(token_per_s)
    print(eval_count)
    print(eval_duration)