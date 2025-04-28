
import json
from collections import defaultdict

def classify_and_summarize(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 分类结构：{label: {sql_len: [idx1, idx2, ...]}}
    stats = defaultdict(lambda: defaultdict(list))

    for idx, item in enumerate(data):
        label = item.get('safe_label', 'unknown')
        sql_list = item.get('sql_list', [])
        sql_len = len(sql_list)

        stats[label][sql_len].append(idx)

    # 输出结果
    for label, length_dict in stats.items():
        print(f"\n=== Label: {label} ===")
        for sql_len, indices in sorted(length_dict.items()):
            print(f"  SQL length {sql_len}: {len(indices)} items")

    return stats

# 使用示例
json_file = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\syn\U_1.json"  # 替换为你的 JSON 路径
stats = classify_and_summarize(json_file)
