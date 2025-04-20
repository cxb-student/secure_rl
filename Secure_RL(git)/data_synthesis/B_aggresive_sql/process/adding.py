import json

with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\A_safe_condition\\omni_cells.json", 'r', encoding="utf-8") as f:
    safe_conditions = json.load(f)
with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\output\\output\\output_whole_cell.json", 'r', encoding="utf-8") as f:
    output = json.load(f)
with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\syn\\prompt_ids.json", 'r', encoding="utf-8") as f:
    prompt_ids = json.load(f)
added_result = []
print(len(prompt_ids))
print(len(output))
for i in range(len(prompt_ids)):
    safe_id = prompt_ids[i]
    print(safe_id)
    safe_condition = next((item for item in safe_conditions if item.get("id") == safe_id), None)
    output_id = output[i]
    middle_one = {**safe_condition, **output_id}
    del middle_one["input"]
    
    # 提取output字段中最后一个```sql ```标记之间的SQL语句
    if "output" in middle_one:
        output_text = middle_one["output"]
        sql_blocks = output_text.split("```sql")
        if len(sql_blocks) >= 1:
            last_sql_block = sql_blocks[-1]
            # 提取SQL语句（去除结尾的```和额外空白）
            sql_content = last_sql_block.split("```")[0].strip()
            # 去除多余换行符
            sql_content = ' '.join(sql_content.split())
            middle_one["extracted_sql"] = sql_content
    
    added_result.append(middle_one)
with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\Infer_column.json", 'w', encoding="utf-8") as f:
    f.write(json.dumps(added_result, indent=2, ensure_ascii=False))