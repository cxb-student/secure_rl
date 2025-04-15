import json
import re

# 读取原始JSON文件
with open(
        'C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\A_safe_condition\\omni\\output_whole_column.json',
        'r', encoding='utf-8') as f:
    data = json.load(f)
with open(
        'C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\db_ids.json',
        'r', encoding='utf-8') as f:
    db_list = json.load(f)
# 创建新的数据结构
result = []

# 计数器，用于统计跳过的条目数量
skipped_count = 0

for idx, item in enumerate(data):
    output_text = item['output']

    # 尝试多种格式匹配
    # 处理带有星号或其他格式的情况
    safe_condition_patterns = [
        r'(?:safe_condition:|Safe condition:)\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*Safe condition:\*\*\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*Safety condition:\*\*\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*Safety Condition:\*\*\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*Safe Condition:\*\*\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*safe_condition:\*\*\s*(.*?\.)(?=\s|\n|$)',
        r'\*\*Safety Condition\*\*\s*(.*?\.)(?=\s|\n|$)',
    ]

    safe_condition_match = None
    for pattern in safe_condition_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            safe_condition_match = match
            break

    specific_column_patterns = [
        r'(?:specific_column:|specific_column:\s*)\s*(\[.*?\])(?:\n|$)',
        r'\*\*specific_column:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific column:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific Column:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific Column\*\*\s*(\[.*?\])(?:\n|$)'


    ]

    specific_column_match = None
    for pattern in specific_column_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            specific_column_match = match
            break

    specific_value_patterns = [
        r'(?:specific_value:|specific_values?:)\s*(\[.*?\])(?:\n|$)',
        r'\*\*specific_value:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific value:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*specific_values:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific Value:\*\*\s*(\[.*?\])(?:\n|$)',
        r'\*\*Specific Value\*\*\s*(\[.*?\])(?:\n|$)'
    ]

    specific_value_match = None
    for pattern in specific_value_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            specific_value_match = match
            break

    # 提取匹配的内容或设为None
    safe_condition = None
    if safe_condition_match:
        safe_condition = safe_condition_match.group(1).strip()
        # 移除可能的星号
        safe_condition = safe_condition.replace('*', '').strip()

    specific_column = None
    if specific_column_match:
        specific_column = specific_column_match.group(1).strip()
        # 移除可能的星号
        specific_column = specific_column.replace('*', '').strip()

    specific_value = None
    if specific_value_match:
        specific_value = specific_value_match.group(1).strip()
        # 移除可能的星号
        specific_value = specific_value.replace('*', '').strip()

    # 如果没有找到，设为"None"
    safe_condition = safe_condition if safe_condition else "None"
    specific_column = specific_column if specific_column else "None"
    specific_value = specific_value if specific_value else "None"

    # 如果safe_condition和specific_column都没有找到值，则跳过这一条目
    if safe_condition == "None":
        skipped_count += 1
        continue
    if specific_column == "None":
        skipped_count += 1
        continue
    # 处理specific_column中的每一项
    should_skip = False
    if specific_column != "None" and specific_column.startswith("[") and specific_column.endswith("]"): 
        # 去掉首尾的方括号，然后按逗号分割
        columns_str = specific_column[1:-1].strip()
        if columns_str:  # 确保不是空列表
            columns = [col.strip() for col in columns_str.split(',')]
            
            # 处理每一列，去掉括号及括号内的内容
            processed_columns = []
            for col in columns:
                # 使用正则表达式去掉括号及括号内的内容
                col_name = re.sub(r'\([^)]*\)', '', col).strip()
                processed_columns.append(col_name)
            
            # 检查每一列是否在输入中存在
            input_text = item.get('input', '')
            for col_name in processed_columns:
                if col_name and col_name not in input_text:
                    should_skip = True
                    skipped_count += 1
                    break
    
    if should_skip:
        continue

    # 创建新的条目
    new_item = {
        "id":idx,
        "db_id": db_list[idx],
        "safe_condition": safe_condition,
        "specific_column": specific_column,
        "specific_value": specific_value
    }

    result.append(new_item)

# 保存为新的JSON文件
with open(
        'C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\A_safe_condition\\omni_whole_column.json',
        'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"提取完成，已保存到omni_cells.json文件，共跳过 {skipped_count} 条数据")