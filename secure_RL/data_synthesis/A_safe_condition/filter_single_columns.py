import json
import re

# 读取原始JSON文件
input_file = 'omni_whole_column_added.json'
output_file = 'omni_whole_column_filtered.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

filtered_data = []
removed_count = 0

for item in data:
    specific_column = item.get('specific_column', '')
    
    # 使用正则表达式匹配列名
    columns = re.findall(r'\w+\.\w+\s*\([^)]*\)', specific_column)
    
    # 如果只有一个列，则跳过
    if len(columns) <= 1:
        removed_count += 1
        continue
    
    filtered_data.append(item)

# 保存过滤后的数据
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)

print(f"处理完成，共移除了 {removed_count} 条记录。结果已保存到 {output_file}")