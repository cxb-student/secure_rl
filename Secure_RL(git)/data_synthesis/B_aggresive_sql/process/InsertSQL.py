import json
import re


def extract_column_names(specific_column):
    """从specific_column中提取列名，不包括表名和括号里的内容"""
    matches = re.findall(r'\b\w+\.(?P<column>\w+)\s*\([^)]*\)', specific_column)
    return matches


def main():
    # 设置输入和输出文件路径
    json1_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\U_column_infer.json'
    json2_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\output\selected_data.json'
    output_path = 'path_to_output.json'

    # 读取json1文件
    with open(json1_path, 'r', encoding='utf-8') as f:
        json1_data = json.load(f)

    # 读取json2文件
    with open(json2_path, 'r', encoding='utf-8') as f:
        json2_data = json.load(f)

    # 初始化结果列表
    result = []

    # 遍历json1中的每个项
    for item1 in json1_data:
        item_id = item1.get('id')
        specific_column = item1.get('specific_column', '')
        extracted_sql = item1.get('extracted_sql', [])

        # 提取列名
        column_names = extract_column_names(specific_column)

        # 在json2中查找具有相同id的项
        for item2 in json2_data:
            if item2.get('id') == item_id:
                exout_sql = item2.get('extracted_sql', '')

                # 检查exout_sql是否不包含specific_column中的任何列
                if not any(column in exout_sql for column in column_names):
                    # 在extracted_sql中选择长度大于等于2的项
                    valid_sqls = [sql for sql in extracted_sql if len(sql) >= 2]
                    for i in range(len(valid_sqls)):
                        if i ==0:
                            vaa = [valid_sqls[0]]
                            vaa.append(exout_sql)
                        else:
                            vaa.append(valid_sqls[i])



                    # 构造新的项
                    new_item = {
                        "id": item_id,
                        "db_id": item1.get('db_id'),
                        "safe_condition": item1.get('safe_condition'),
                        "specific_column": specific_column,
                        "specific_value": item1.get('specific_value'),
                        "extracted_sql": vaa
                    }

                    # 添加到结果列表
                    result.append(new_item)
                    break
                break
        continue

    # 保存结果到输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"处理完成，结果已保存到{output_path}")


if __name__ == "__main__":
    main()