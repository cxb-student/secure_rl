import json
import os

# 定义需要检查的关键字段
required_keys = [
    "id",
    "db_id",
    "safe_condition",
    "specific_column",
    "safe_label",
    "sql_list",
    "questions",
    "SQL_COT",
    "label",
    "secure_cot",
]

# 判断值是否为空
def is_empty(value):
    if value is None:
        return True
    if isinstance(value, (list, dict, str)) and len(value) == 0:
        return True
    return False


def filter_json(input_path: str, output_path: str) -> None:
    """
    读取 input_path 中的 JSON 数据（列表），
    过滤掉缺少 required_keys 或 对应值为空的项，
    并将结果写入 output_path。
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("输入文件的顶层结构应为 JSON 列表")

    filtered = []
    removed_count = 0

    for idx, item in enumerate(data):
        # 检查所有必需字段
        if not isinstance(item, dict):
            removed_count += 1
            continue

        valid = True
        for key in required_keys:
            if key not in item or is_empty(item.get(key)):
                valid = False
                break


        if len(item["SQL_COT"]) == 0:
            print(1)
            removed_count += 1
            continue
        elif item["SQL_COT"][-1] is None:
            print(2)
            removed_count += 1
            continue
        if valid:
            filtered.append(item)
        else:
            removed_count += 1

    # 将过滤后的列表写回文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"原数据总项数: {len(data)}, 保留项数: {len(filtered)}, 删除项数: {removed_count}")


if __name__ == '__main__':

    in_path, out_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\Syn_Ultimate.json", r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\Syn_Ultimate_clean.json"
    filter_json(in_path, out_path)