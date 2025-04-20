import os
import json

# 设置你的文件夹路径
folder_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Ultimate_outcome'  # ← 替换为你的目录路径

all_data = []

# 遍历文件夹中的所有 .json 文件
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        if filename == 'U_cells_direct.json':
            continue
        if filename == 'U_column_direct.json':
            continue
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        item.pop('output', None)  # 删除 'output' 键（如果存在）
                    all_data.extend(data)
                else:
                    print(f"⚠️ 文件 {filename} 的格式不是列表，已跳过。")
            except json.JSONDecodeError:
                print(f"❌ 文件 {filename} 不是合法的 JSON，已跳过。")

# 按 id 排序（如果没有 id 则使用 0）
sorted_data = sorted(all_data, key=lambda x: x.get('id', 0))

# 保存到一个新文件
output_path = os.path.join('merged_sorted.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"✅ 合并并删除 output 字段完成，结果已保存到：{output_path}")
