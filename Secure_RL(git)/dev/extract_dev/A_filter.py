import json
a = input("label:")
# 定义输入和输出文件路径
input_file = "../dev.json"
output_file = f"{a}_Dev.json"

# 读取 JSON 数据集
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 筛选出 label 为 "RE" 的项
filtered_data = [item for item in data if item.get("label") == a]

# 将筛选后的数据写入新的 JSON 文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)

print(f"已筛选出 {len(filtered_data)} 条 label 为 'RE' 的记录，结果保存在 {output_file}")
