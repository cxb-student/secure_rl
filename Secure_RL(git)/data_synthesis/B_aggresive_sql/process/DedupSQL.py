# 移除同一个id下相同的SQL语句

import json
import os


def remove_duplicate_sql(data):
    """移除同一个id下相同的SQL语句"""
    # 创建一个字典来存储每个id对应的唯一SQL
    id_sql_map = {}

    for item in data:
        item_id = item.get("id")
        if not item_id or "extracted_sql" not in item:
            continue

        # 将SQL列表转换为元组以便用作字典键
        sql_tuple = tuple(item["extracted_sql"])

        if item_id not in id_sql_map:
            id_sql_map[item_id] = {sql_tuple: item}
        else:
            # 如果这个SQL组合已经存在，跳过
            if sql_tuple in id_sql_map[item_id]:
                continue
            # 否则添加这个新的SQL组合
            id_sql_map[item_id][sql_tuple] = item

    # 将去重后的数据重新组合成列表
    deduplicated_data = []
    for id_dict in id_sql_map.values():
        deduplicated_data.extend(id_dict.values())

    return deduplicated_data


def main():
    # 设置输入和输出文件路径
    input_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\U_column_direct.json"
    output_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\U_column_direct.json"

    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：输入文件 {input_path} 不存在")
        return

    # 读取输入文件
    try:
        with open(input_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取输入文件时出错: {e}")
        return

    # 记录原始数据项数量
    original_count = len(data)
    print(f"原始数据项数量: {original_count}")

    # 去除重复的SQL
    deduplicated_data = remove_duplicate_sql(data)
    deduped_count = len(deduplicated_data)
    print(f"去重后数据项数量: {deduped_count}")
    print(f"共移除 {original_count - deduped_count} 个重复项")

    # 保存去重后的结果
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(deduplicated_data, f, indent=2, ensure_ascii=False)
        print(f"去重后的数据已保存至: {output_path}")
    except Exception as e:
        print(f"保存输出文件时出错: {e}")


if __name__ == "__main__":
    main()