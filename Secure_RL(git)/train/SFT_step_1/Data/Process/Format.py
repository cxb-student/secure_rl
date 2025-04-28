import json
import re
from collections import defaultdict

def clean_input(content: str) -> str:
    # 删除从 "math-content" 到 第一个分号 "；" 的内容（包括这部分）
    return re.sub(r'matched contents[^；]*；', '', content)

def process_data(data):
    grouped = defaultdict(list)
    for item in data:
        qid = item.get("question_id")
        grouped[qid].append(item)

    result = []
    for qid, items in grouped.items():
        first = items[0]
        messages = first.get("messages", [])
        input_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        output_msg = next((m["content"] for m in messages if m["role"] == "assistant"), "")
        cleaned_input = clean_input(input_msg)
        result.append({
            "input": cleaned_input.strip(),
            "output": output_msg.strip()
        })

    return result

# 假设你的 JSON 数据存储在一个文件中，比如 data.json
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\DPO-sql\syn_cot_data.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

processed = process_data(raw_data)
print(len(processed))
# 保存为简化后的 json 文件
with open('processed_data.json', 'w', encoding='utf-8') as f:
    json.dump(processed, f, indent=2, ensure_ascii=False)
