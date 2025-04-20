import json
import re


# ... 现有代码保持不变 ...

def extract_sql_queries(text):
    pattern = r"SELECT.*?(?:;|\n{2,}|\Z)"

    return re.findall(pattern, text)
# ... 其余代码保持不变 ...


def modify_json(input_path,output_path, delect = 0):
    # 读取输入的 JSON 文件
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        if "extracted_sql" in item:
            content = item["extracted_sql"]

            matches = extract_sql_queries(content)
            item["extracted_sql"] = matches
        else:
            #删除该项
            data.remove(item)
            delect +=1
    # 将修改后的数据保存到输出文件
    print(f"{delect} items deleted")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 示例调用
input_json_path = 'c:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\Infer_column.json'
output_json_path = 'c:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\Infer_column.json'
modify_json(input_json_path, output_json_path)