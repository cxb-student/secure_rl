import json
from collections import defaultdict

# 读取三个 JSON 文件
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\map1.json', 'r', encoding='utf-8') as f:
    map_data = json.load(f)

with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\total_nl2sql_part_1.json', 'r', encoding='utf-8') as f:
    output_data = json.load(f)


# 分组结果字典：item_idx -> list of outputs（按顺序）
# 临时结构：item_idx -> list of (output, db_id, item_id, sql_list)
temp_grouped = defaultdict(list)

# 按item_idx分组SQL数据
sql_grouped = defaultdict(list)
for sql_item in map_data:
    item_idx = sql_item['item_idx']
    sql_grouped[item_idx].append(sql_item['sql'])

# 遍历 map_data，根据索引从 output_data 获取对应项
for i, map_item in enumerate(map_data):
    item_idx = map_item['item_idx']
    db_id = map_item['db_id']
    item_id = map_item['item_id']
    output_text = output_data[i].get('output', None)
    if output_text is not None:
        temp_grouped[item_idx].append({
            "output": output_text,
            "db_id": db_id,
            "item_id": item_id,
            "sql_list": sql_grouped.get(item_idx, [])
        })

# 整理输出结构
final_output = []
for item_idx, items in sorted(temp_grouped.items()):
    outputs = [x['output'] for x in items]
    sql_lists = [x['sql_list'] for x in items]
    db_id = items[0]['db_id']  # 同一组的 db_id 应该相同
    item_id = items[0]['item_id']
    final_output.append({
        "item_idx": item_idx,
        "item_id": item_id,
        "db_id": db_id,
        "outputs": outputs,
        "sql_list": sql_lists[0] if sql_lists else []
    })

# 保存到 JSON 文件
with open('grou_output.json', 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print("包含 db_id 和 item_id 的分组输出已保存到 grouped_output.json")