import json

from transformers import AutoTokenizer
model_path = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\U_V2.json", "r",encoding="utf-8") as f:
    data = json.load(f)
all_prompts = []
for i in range(len(data)):
    input_string  = data[i]["input"]
    all_prompts.append(input_string)



tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
total_tokens = 0
for prompt in all_prompts:
    inputs = tokenizer(prompt, return_tensors="pt")
    total_tokens += inputs["input_ids"].shape[1]
print("平均token")
print(total_tokens / len(all_prompts))
print("最大token")
print(max(len(tokenizer.encode(prompt)) for prompt in all_prompts))