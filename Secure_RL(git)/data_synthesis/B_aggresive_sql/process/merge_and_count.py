import json
import sys
from collections import defaultdict

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_and_sort(json1_path, json2_path, output_path):
    # 加载两个JSON文件
    json1_data = load_json(json1_path)
    json2_data = load_json(json2_path)
    
    # 合并数据
    merged_data = json1_data + json2_data
    
    # 按id排序
    try:
        merged_data.sort(key=lambda x: x.get('id'))
    except TypeError:
        print("警告：某些对象的 'id' 无法排序（非数字或缺失）")
    
    # 统计label数量
    label_counts = defaultdict(int)
    for item in merged_data:
        label = item.get('safe_label', 'unknown')
        label_counts[label] += 1
    
    # 保存合并后的结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # 输出统计结果
    print(f"✅ 合并完成，共 {len(merged_data)} 条数据")
    print(f"safe标签数量: {label_counts.get('safe', 0)}")
    print(f"unsafe标签数量: {label_counts.get('unsafe', 0)}")

if __name__ == "__main__":
    # 硬编码文件路径
    json1_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Final\U_whole_output.json"  # 替换为第一个JSON文件路径
    json2_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\process\p111.json"  # 替换为第二个JSON文件路径
    output_path = r"/research/NL2SQL/secure_RL/data_synthesis/B_aggresive_sql/EX_output/Final/U_whole.json"  # 替换为输出文件路径
    
    merge_and_sort(json1_path, json2_path, output_path)