import json
import re


def parse_db_schema_with_types(schema_text):
    """
    从 schema 中提取每个表的主键列（包含类型信息），格式：
    {
       "department": ["department.department_id (int)"],
       ...
    }
    """
    pk_dict = {}
    table_pattern = re.compile(r"table\s+(\w+)\s*,\s*columns\s*=\s*\[(.*?)\]", re.S)
    column_pattern = re.compile(r"(\w+\.\w+)\s*\(([^)]*primary key[^)]*)\)", re.I)  # 只抓 primary key 的列，保留类型信息

    for table_match in table_pattern.finditer(schema_text):
        table_name = table_match.group(1)
        columns_block = table_match.group(2)
        pk_columns = []
        for col_match in column_pattern.finditer(columns_block):
            full_col = f"{col_match.group(1)} ({col_match.group(2).split('|')[0].strip()})"
            pk_columns.append(full_col)
        pk_dict[table_name] = pk_columns
    return pk_dict


def update_input_with_pk(db_list, input_list):
    updated_input = []
    insert_count = 0

    for record in input_list:
        db_index = record.get("id")
        if db_index is None or db_index >= len(db_list):
            updated_input.append(record)
            continue

        schema_text = db_list[db_index]
        pk_info = parse_db_schema_with_types(schema_text)
        spec_col_str = record.get("specific_column", "")

        # 提取所有的 表.列
        column_matches = re.findall(r"(\w+\.\w+)\s*\([^)]*\)", spec_col_str)

        if len(column_matches) == 1:
            print(db_index)
            table_name = column_matches[0].split('.')[0]
            if table_name in pk_info and pk_info[table_name]:
                pk_strs = pk_info[table_name]
                # 把这些加进去，用 , 连接，保持 [] 格式
                # 去掉原始字符串的方括号和空格
                original_content = spec_col_str.strip()[1:-1].strip()
                pk_combined = ', ' + ', '.join(pk_strs)
                record["specific_column"] = f"[{original_content}{pk_combined}]"
                insert_count += 1
        # 不符合条件，原样保留
        updated_input.append(record)

    return updated_input, insert_count


# 示例使用
if __name__ == "__main__":
    with open("C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omni_2000.json", "r", encoding="utf-8") as f:
        db_list = json.load(f)
    with open("omni_whole_column.json", "r", encoding="utf-8") as f:
        input_list = json.load(f)

    updated_data, total_inserted = update_input_with_pk(db_list, input_list)

    with open("omni_whole_column_added.json", "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

    print(f"总共插入了 {total_inserted} 条主键信息。结果已保存至 new_input.json。")
