import json
import os
import random
from tqdm import tqdm

# 输入与输出路径
input_path = r'../../data_synthesis/merged_schema_qa.json'
output_path = r'../../data_synthesis/final_prompts.json'

# 加载已合并的 schema QA 数据
with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 按 schema_sequence 分组
groups = {}
for idx, item in enumerate(data):
    key = item['schema_sequence']
    groups.setdefault(key, []).append(idx)

# 确定每条记录的历史长度 (0,1,2) 均匀分布
n = len(data)
base = n // 3
counts = [base, base, base]
for i in range(n - base * 3):
    counts[i] += 1
lengths = [0] * counts[0] + [1] * counts[1] + [2] * counts[2]
random.shuffle(lengths)

prompts = []
# 构建 Prompt
for idx, hist_len in tqdm(enumerate(lengths), total=n, desc='Building prompts'):
    item = data[idx]
    schema = item['schema_sequence']
    question = item['question']
    sql = item['sql']
    # 采样历史记录
    chat_history = ''
    if hist_len > 0:
        other_idxs = [i for i in groups[schema] if i != idx]
        sampled = random.sample(other_idxs, min(hist_len, len(other_idxs)))
        lines = ['**Chat history**']
        for turn, j in enumerate(sampled, start=1):
            prev = data[j]
            lines.append(f"Turn-{turn} :[ 'Question': {repr(prev['question'])}, 'SQL': {repr(prev['sql'])} ]")
        chat_history = '\n'.join(lines)

    if hist_len > 0:
        prompt = f"""**Task Overview**
You are a senior data analyst with expertise in Structured Query Language (SQL). Given a question raised by a front-end team member and a corresponding database schema, your task is to translate the question into an accurate SQLite query, accompanied by a detailed explanation of your reasoning process. 
In addition to the question and schema, you will also receive a streamlined chat history from colleagues. This chat history may contain helpful context or prior attempts—correct or not—and is intended to assist you in formulating a precise and well-informed response. 
To support automated SQL extraction using regular expressions, please follow the output format below. 
**Database Schema** 
{schema}

{chat_history}

**Output Format Requirements** 
The SQL query must be enclosed in a Markdown code block with SQL syntax highlighting. 
Your reasoning process should be enclosed within <COT>...</COT> tags. 、
For example: 
<COT>I need to select all in the database</COT> 
```sql 
SELECT * FROM database; 
``` 
**Question**
{question}
**Answer** 
Let's proceed step by step."""
    else:
        prompt = f"""**Task Overview**
You are a senior data analyst with expertise in Structured Query Language (SQL). Given a question raised by a front-end team member and a corresponding database schema, your task is to translate the question into an accurate SQLite query, accompanied by a detailed explanation of your reasoning process. 
To support automated SQL extraction using regular expressions, please follow the output format below.  
**Database Schema** 
{schema} 

**Output Format Requirements** 
The SQL query must be enclosed in a Markdown code block with SQL syntax highlighting. 
Your reasoning process should be enclosed within <COT>...</COT> tags. For example: 
<COT>I need to select all in the database</COT> 
```sql 
SELECT * FROM database; 
``` 
**Question**
{question}
**Answer** 
Let's proceed step by step."""
    prompts.append({
        'prompt': prompt,
        'question': question,
        'sql': sql
    })

# 保存最终 prompts
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(prompts, f, ensure_ascii=False, indent=2)

print(f"Generated {len(prompts)} prompts, saved to {output_path}")