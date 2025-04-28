import json
from collections import OrderedDict

KEY_ORDER = [
    'id',
    'db_id',
    'safe_condition',
    'specific_value',
    'specific_column',
    'safe_label',
    'sql_list',
    'questions',
    'cot_content'
]

def process_json(input_path, output_path):
    """处理JSON文件键序并验证数据结构"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 验证必需字段
    required_fields = set(KEY_ORDER)
    for idx, item in enumerate(data):
        missing = required_fields - set(item.keys())
        if missing:
            print(f'错误：第{idx}条数据缺失字段 {missing}')
            return False

    # 重构数据格式
    processed_data = []
    for item in data:
        ordered_item = OrderedDict()
        for key in KEY_ORDER:
            ordered_item[key] = item[key]
        processed_data.append(ordered_item)

    # 安全写入
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    print(f'成功处理{len(processed_data)}条数据')
    return True

if __name__ == '__main__':
    input_file = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\process\extracted_questions222.json'
    output_file = r'c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\formatted_output.json'
    process_json(input_file, output_file)