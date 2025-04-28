import json
import random
from collections import Counter, defaultdict


def process_data(input_json_path, db_desc_path, output_path):
    # 读取输入数据
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取数据库描述
    with open(db_desc_path, 'r', encoding='utf-8') as f:
        db_descriptions = json.load(f)

    processed_data = []
    total_length = 0
    skipped_count = 0

    # 用于统计历史条数分布
    history_count_distribution = Counter()

    # 按历史条数分组数据
    history_grouped_data = defaultdict(list)

    for item in data:
        try:
            # 获取数据库描述
            db_id = item['id']
            if db_id >= len(db_descriptions):
                skipped_count += 1
                continue

            db_desc = db_descriptions[db_id]

            # 获取问题列表和SQL列表
            questions = item['questions']
            sql_list = item['sql_list']

            # 检查SQL_COT是否存在且非空
            if 'SQL_COT' not in item or not item['SQL_COT']:
                skipped_count += 1
                continue

            # 检查SQL_COT[-1]是否为None
            if item['SQL_COT'][-1] is None:
                skipped_count += 1
                continue

            # 构建历史对话记录
            history = []
            for q, s in zip(questions[:-1], sql_list[:-1]):
                history.append({
                    "Q": q,
                    "A": s
                })

            # 统计历史条数
            history_count = len(history)
            history_count_distribution[history_count] += 1

            # 构建历史对话字符串
            chat_history = ""
            if history:
                history_items = []
                for idx, h in enumerate(history):
                    history_items.append(f"\nTurn-{idx + 1} :[ 'Question': {h['Q']}, 'SQL': {h['A']}]")
                chat_history = "".join(history_items)
                task_template = f"""**Task Overview**
You are a senior data analyst with expertise in Structured Query Language (SQL). Given a question raised by a front-end team member and a corresponding database schema, your task is to translate the question into an accurate SQLite query, accompanied by a detailed explanation of your reasoning process. 
In addition to the question and schema, you will also receive a streamlined chat history from colleagues. This chat history may contain helpful context or prior attempts—correct or not—and is intended to assist you in formulating a precise and well-informed response. 
To support automated SQL extraction using regular expressions, please follow the output format below. 
**Database Schema** 
{db_desc}
**Chat history**
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

                # 构建输入和输出
                input_text = task_template.replace("{chat history}", chat_history)
                input_text = input_text.replace("<question>", f"{questions[-1]}")
                if "Turn-2"in input_text:
                    print(input_text)
                #
            else:
                input_text = f"""**Task Overview** 
You are a senior data analyst with expertise in Structured Query Language (SQL). Given a question raised by a front-end team member and a corresponding database schema, your task is to translate the question into an accurate SQLite query, accompanied by a detailed explanation of your reasoning process. 
To support automated SQL extraction using regular expressions, please follow the output format below.  
**Database Schema** 
{db_desc} 
**Output Format Requirements** 
The SQL query must be enclosed in a Markdown code block with SQL syntax highlighting. 
Your reasoning process should be enclosed within <COT>...</COT> tags. 
For example: 
<COT>I need to select all in the database</COT> 
```sql 
SELECT * FROM database; 
``` 
**Question**
{question}
**Answer** 
Let's proceed step by step."""
                input_text = input_text.replace("<question>", f"{questions[-1]}")
            
            # 构建任务模板

            output_text = f"<COT>{item['SQL_COT'][-1]}</COT>\n```sql\n{sql_list[-1]}\n```"

            # 计算总长度
            total_length += len(input_text) + len(output_text)

            # 按历史条数分组
            processed_item = { # 保持与Omni.py格式一致
                "input": input_text,
                "output": output_text,
            }
            history_grouped_data[history_count].append(processed_item)

        except (KeyError, IndexError, TypeError) as e:
            skipped_count += 1
            continue

    print(f"跳过的数据条数: {skipped_count}")

    # 打印历史条数分布
    print("历史条数分布:")
    for count, frequency in sorted(history_count_distribution.items()):
        print(f"  历史条数 {count}: {frequency} 条数据")

    # 如果没有有效数据，则返回
    if not history_grouped_data:
        print("没有有效数据可以处理")
        return 0, 0

    # 从每种历史条数中随机采样3000条数据
    sampled_data = []
    for history_count, items in history_grouped_data.items():
        # 确定采样数量，最多3000条，如果不足则全部采用
        sample_size = min(3000, len(items))
        sampled = random.sample(items, sample_size)
        sampled_data.extend(sampled)
        print(f"  历史条数 {history_count}: 采样 {sample_size} 条数据")

    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sampled_data, f, ensure_ascii=False, indent=2)

    return total_length, len(sampled_data)


if __name__ == "__main__":
    input_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\our\U_put_balance.json"  # 输入JSON文件路径
    db_desc_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\omni_2000.json"  # 数据库描述文件路径
    output_path = "our_v1.json"  # 输出文件路径

    total_len, sample_count = process_data(input_path, db_desc_path, output_path)
    print(f"总长度: {total_len}")
    print(f"采样数据总条数: {sample_count}")