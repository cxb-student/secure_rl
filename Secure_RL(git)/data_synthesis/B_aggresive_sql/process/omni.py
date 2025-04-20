import json
import re

# 定义一个函数来清理字符串中的多余空格和换行符，并过滤掉包含WITH的SQL语句
def clean_text(text):
    if isinstance(text, str):
        # 检查是否包含WITH关键字（不区分大小写）
        if re.search(r'\bWITH\b', text, re.IGNORECASE):
            return ""
        # 替换多个空格为单个空格，替换换行符为空格
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空格
        text = text.strip()
    return text

with open(
        "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\output\\selected_data.json",
        'r', encoding="utf-8") as f:
    output = json.load(f)
with (open(
        "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\db_ids.json",
        'r', encoding="utf-8") as f):
    db_id = json.load(f)

added_result = []
for i in range(len(output)):
    output_id = output[i]
    middle_one = {}
    
    # 确保id字段存在
    if "id" not in output_id and i < len(db_id):
        for j in range(len(db_id)):
            if db_id[j] == output_id.get("db_id"):
                middle_one["id"] = j
                break
    else:
        middle_one["id"] = output_id.get("id")
    
    # 添加db_id字段
    middle_one["db_id"] = output_id.get("db_id")
    
    # 处理extracted_sql字段，清理多余空格和换行符，并过滤掉包含WITH的SQL语句
    if "extracted_sql" in output_id:
        output_text = output_id["extracted_sql"]
        # 清理SQL文本并过滤WITH语句
        cleaned_sql = clean_text(output_text)
        # 如果过滤后为空字符串，则跳过该条记录
        if cleaned_sql == "":
            continue
        middle_one["extracted_sql"] = cleaned_sql
    
    # 添加其他字段
    for key, value in output_id.items():
        if key not in ["id", "db_id", "extracted_sql"]:
            middle_one[key] = value
    
    added_result.append(middle_one)

# 按id排序
added_result = sorted(added_result, key=lambda x: x.get("id", float('inf')))
# 输出结果
with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\output\\selected_data.json",
          'w', encoding="utf-8") as f:
    f.write(json.dumps(added_result, indent=2, ensure_ascii=False))