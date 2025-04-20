# 过滤不包含specific_column的SQL语句

import json
import re
import os


def extract_column_names(specific_column):
    """从specific_column中提取列名，不包括表名和括号里的内容"""
    # 使用正则表达式匹配表名.列名(类型)的模式
    matches = re.findall(r'\b\w+\.(?P<column>\w+)\s*\([^)]*\)', specific_column)
    return matches


def check_sql_contains_any_column(extracted_sql, column_names):
    """检查所有SQL语句作为一个整体是否包含任何指定的列名"""
    # 将所有SQL语句合并为一个字符串
    all_sql_text = ""
    for i in range(len(extracted_sql)):
        all_sql_text += extracted_sql[i]
    # 检查合并后的文本是否包含任何指定的列名
    correct = 0
    for column_name in column_names:
        if column_name in all_sql_text:
            correct+=1
        else:
            continue
    if correct == len(column_names):
        return True
    return False


def main():
    # 设置输入和输出文件路径
    input_path = r"/research/NL2SQL/secure_RL/data_synthesis/B_aggresive_sql/EX_output/column_infer.json"
    output_path = r"/research/NL2SQL/secure_RL/data_synthesis/B_aggresive_sql/U_cells_infer.json"
    error_path = r"c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\output_errors2.json"

    # 读取输入文件
    with open(input_path, 'r', encoding="utf-8") as f:
        data = json.load(f)

    # 过滤SQL语句
    total_items_count = len(data)
    removed_items_count = 0
    filtered_data = []
    error_data = []

    for item in data:
        if "extracted_sql" in item and "specific_column" in item:
            column_names = extract_column_names(item["specific_column"])
            print(column_names)

            # 检查所有SQL语句作为一个整体是否包含任何指定的列名
            if check_sql_contains_any_column(item["extracted_sql"], column_names):
                # 如果包含，则保留整个数据项
                filtered_data.append(item)
            else:
                # 如果不包含，则将其添加到错误数据列表中
                error_data.append(item)
                removed_items_count += 1
        else:
            # 如果项目中没有extracted_sql或specific_column字段，添加到错误数据
            error_data.append(item)
            removed_items_count += 1

    # 保存过滤后的结果
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)

    # 保存错误数据
    with open(error_path, 'w', encoding="utf-8") as f:
        json.dump(error_data, f, indent=2, ensure_ascii=False)

    print(f"处理完成！共处理 {total_items_count} 个数据项")
    print(f"共移除 {removed_items_count} 个项目（所有SQL都不包含指定列名）")
    print(f"保留 {len(filtered_data)} 个项目")
    print(f"结果已保存至: {output_path}")
    print(f"错误数据已保存至: {error_path}")


if __name__ == "__main__":
    main()