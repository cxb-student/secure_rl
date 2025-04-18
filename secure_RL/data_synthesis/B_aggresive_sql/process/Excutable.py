# 过滤不包含specific_column的SQL语句

import json
import re
import os
import sqlite3


def extract_column_names(specific_column):
    """从specific_column中提取列名，不包括表名和括号里的内容"""
    # 使用正则表达式匹配表名.列名(类型)的模式
    matches = re.findall(r'\b\w+\.(?P<column>\w+)\s*\([^)]*\)', specific_column)
    return matches


def get_db_path(db_id):
    """根据数据库ID获取数据库文件路径"""
    possible_paths = [
        f"C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omnisql\\databases\\databases\\{db_id}\\{db_id}.sqlite"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def check_sql_executable(db_id, sql_text):
    """检查SQL语句是否能在数据库中执行"""
    db_path = get_db_path(db_id)
    if not db_path:
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute(sql_text)
        cursor.execute("ROLLBACK")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"SQL执行错误: {error_msg}")
        # 动态识别错误类型
        if "no such table" in error_msg.lower():
            error_type = "TABLE_NOT_EXIST"
        elif "no such column" in error_msg.lower():
            error_type = "COLUMN_NOT_EXIST"
        elif "syntax error" in error_msg.lower():
            error_type = "SYNTAX_ERROR"
        elif "incomplete input" in error_msg.lower():
            error_type = "INCOMPLETE_INPUT"
        else:
            # 提取错误消息的第一部分作为错误类型
            error_parts = error_msg.split(":", 1)
            if len(error_parts) > 1 and error_parts[0].strip():
                error_type = error_parts[0].strip().upper().replace(" ", "_")
            else:
                error_type = "OTHER_ERROR"
        return {"error": error_msg, "type": error_type}
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def check_sql_contains_any_column(extracted_sql, column_names, db_id=None):
    """检查所有SQL语句作为一个整体是否包含任何指定的列名"""
    # 将所有SQL语句合并为一个字符串
    all_sql_text = ""
    for i in range(len(extracted_sql)):
        all_sql_text += extracted_sql[i]
    # 检查合并后的文本是否包含任何指定的列名
    correct = 0
    for column_name in column_names:
        if column_name in all_sql_text:
            correct += 1
        else:
            continue
    if correct == len(column_names):
        # 如果提供了db_id，则进一步检查SQL是否可执行
        for i in range(len(extracted_sql)):
            sql_result = check_sql_executable(db_id, extracted_sql[i])
            if sql_result is not True:
                for i in range(len(extracted_sql)):
                    print(extracted_sql[i])
                return False
        return True


def main():
    # 设置输入和输出文件路径
    input_path = r"c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\output1.json"
    output_path = r"/research/NL2SQL/secure_RL/data_synthesis/B_aggresive_sql/EX_output/U_column_infer.json"
    error_path = r"c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\output_errors2.json"
    
    # 初始化错误统计 - 使用字典默认值处理动态错误类型
    error_stats = {}

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

            # 检查所有SQL语句作为一个整体是否包含任何指定的列名，并验证是否可执行
            db_id = item.get("db_id")
            result = check_sql_contains_any_column(item["extracted_sql"], column_names, db_id)
            if result is True:
                # 如果包含，则保留整个数据项
                filtered_data.append(item)
            else:
                # 如果不包含，则将其添加到错误数据列表中
                if isinstance(result, dict) and "type" in result:
                    error_type = result["type"]
                    # 动态更新错误统计
                    if error_type not in error_stats:
                        error_stats[error_type] = 0
                    error_stats[error_type] += 1
                    item["error_info"] = result
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
    print(f"共移除 {removed_items_count} 个项目（至少有一个SQL语句不能执行）")
    print(f"保留 {len(filtered_data)} 个项目")
    print(f"结果已保存至: {output_path}")
    print(f"错误数据已保存至: {error_path}")
    print("\n错误类型统计:")
    for error_type, count in error_stats.items():
        print(f"{error_type}: {count}")


if __name__ == "__main__":
    main()