import json
import random

def process_json_v3(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_data = []
    safe_candidates = []

    # 第一次遍历，找出可处理的safe项
    for item in data:
        if item.get('safe_label') == 'safe' and len(item.get('sql_list', [])) == 3:
            safe_candidates.append(item)
        else:
            # unsafe 和其余 safe 项先放进结果集（unsafe 会再处理）
            processed_data.append(item)

    # 随机选取3000个需要处理的safe项
    selected_safe = safe_candidates[:2400]

    for item in safe_candidates:
        if item in selected_safe:
            # 修改sql、question、cot（保留前2个）
            item['sql_list'] = item.get('sql_list', [])[:2]
            if isinstance(item.get('questions'), list):
                item['questions'] = item['questions'][:2]
            if isinstance(item.get('SQL_COT'), list):
                item['SQL_COT'] = item['SQL_COT'][:2]
        # 放入最终结果集
        processed_data.append(item)

    # 再次处理 unsafe 的截断（sql > 3）
    for item in processed_data:
        if item.get('safe_label') == 'unsafe':
            if len(item.get('sql_list', [])) > 3:
                item['sql_list'] = item['sql_list'][:3]
                if isinstance(item.get('question'), list):
                    item['questions'] = item['questions'][:3]
                if isinstance(item.get('cot'), list):
                    item['SQL_COT'] = item['SQL_COT'][:3]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 完成：总数据 {len(processed_data)} 条，处理了 {len(selected_safe)} 条 safe，处理 unsafe 若干。")

# 调用示例
process_json_v3(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\process\json1_with_labels.json', r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\U_put11.json')
