import json
import os


def process_data_files(source_json_path, id_mapping_path, data_path, output_path):
    """
    处理多个数据文件，生成符合NL2SQL任务格式的问答对数据集

    参数:
    source_json_path: 包含原始数据和ID的JSON文件路径
    id_mapping_path: 包含ID对应位置的文件路径
    data_path: 包含实际数据的文件路径
    output_path: 输出结果的文件路径
    """
    # 加载源JSON文件
    with open(source_json_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # 加载ID映射文件
    with open(id_mapping_path, 'r', encoding='utf-8') as f:
        id_mapping = json.load(f)

    # 加载数据文件
    with open(data_path, 'r', encoding='utf-8') as f:
        actual_data = json.load(f)

    # 创建结果列表
    result = []

    # 遍历源数据中的每一项
    for index, item in enumerate(source_data):
        # 获取ID
        item_id = item.get('db_id')
        if item_id is None:
            print(f"警告: 第{index}项没有ID，已跳过")
            continue
        position = -1

        for i in range(len(id_mapping)):
            if id_mapping[i] == item_id:
                position = i
                break

        # 使用位置在数据文件中查找对应数
        if actual_data[position]:
           data_item = actual_data[position]
        else:
            print(f"警告: 第{index}项没有对应的数据，已跳过")
            continue

        # 获取问题数据
        question = item.get('question', '')
        sql = item.get('sql', '')
        #删除sql中多余的空格和换行
        sql = sql.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')
        possible_chat = [{"Q": question, "A": sql}]


        # 获取COT内容
        cot = item.get('cot', '')
        chat_history = "{chat history}"
        # 构建任务模板
        task_template = f"""**Task Overview**
You are a senior data analyst with expertise in Structured Query Language (SQL). Given a question raised by a front-end team member and a corresponding database schema, your task is to translate the question into an accurate SQLite query, accompanied by a detailed explanation of your reasoning process. 
In addition to the question and schema, you will also receive a streamlined chat history from colleagues. This chat history may contain helpful context or prior attempts—correct or not—and is intended to assist you in formulating a precise and well-informed response. 
To support automated SQL extraction using regular expressions, please follow the output format below. 
**Database Schema** 
{data_item}
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
<question>
**Answer** 
Let's proceed step by step."""
        task_template = task_template.replace("<question>", question)
        print("task_template",task_template)
        # 创建问答对
        qa_pair = {
            "id": position,
            "db_id": item_id,
            "input": task_template,
            "output": f"<COT>{cot}</COT>\n```sql\n{sql}\n```",
            "history": possible_chat,
        }

        result.append(qa_pair)

    # 保存结果
    result.sort(key=lambda x: x.get('id'))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"处理完成，共生成 {len(result)} 条问答对，已保存至 {output_path}")


if __name__ == "__main__":
    # 示例用法，请根据实际文件路径修改
    source_json = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Omni-sql\selected_data.json"
    id_mapping = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\db_ids.json"
    data_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\omni_2000.json"
    output_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\Omni_v1.json"

    process_data_files(source_json, id_mapping, data_path, output_path)