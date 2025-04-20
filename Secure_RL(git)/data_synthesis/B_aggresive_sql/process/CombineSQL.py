import os
import json

# 指定需要保留和补全的键
TARGET_KEYS = [
    "id",
    "db_id",
    "label",
    "safe_condition",

    "specific_column",
    "specific_value",
    "extracted_sql",
    "cot_content"

]

def load_json_files(directory):
    json_list = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            path = os.path.join(directory, filename)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        json_list.extend(data)
                    elif isinstance(data, dict):
                        json_list.append(data)
                except json.JSONDecodeError:
                    print(f"跳过无效的 JSON 文件: {filename}")
    return json_list

def filter_and_complete_keys(data_list):
    completed_data = []
    for item in data_list:
        new_item = {key: item.get(key, None) for key in TARGET_KEYS}
        completed_data.append(new_item)
    return completed_data

def merge_and_sort_json(directory, output_file):
    data = load_json_files(directory)
    data = filter_and_complete_keys(data)
    try:
        data.sort(key=lambda x: x.get('id'))
    except TypeError:
        print("警告：某些对象的 'id' 无法排序（非数字或缺失）")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存合并后的 JSON 文件: {output_file}")

# 示例用法
merge_and_sort_json(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Ultimate_outcome',
                    '../EX_output/Final/U_Attack_SQL.json')
