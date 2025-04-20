import json
import os


def extract_db_ids_json(tables_json_path, output_path, limit=2000):
    """从tables.json文件中提取数据库ID并以JSON列表格式保存到文件中，限制提取数量"""
    # 读取tables.json文件
    try:
        with open(tables_json_path, 'r', encoding='utf-8') as f:
            tables_data = json.load(f)
    except Exception as e:
        print(f"读取输入文件时出错: {e}")
        return False

    # 如果设置了限制，则只处理指定数量的数据库
    if limit and limit > 0:
        tables_data = tables_data[:limit]
        print(f"注意：只处理前 {limit} 个数据库")

    db_ids = []

    # 遍历每个数据库，提取db_id
    for db_info in tables_data:
        # 获取数据库名称
        db_id = db_info.get('db_id', '')
        if db_id:
            db_ids.append(db_id)
            print(f"提取数据库ID: {db_id}")
        else:
            print(f"警告：发现没有db_id的数据库条目")

    # 写入输出文件（JSON格式）
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # 将整个列表以JSON格式写入文件
            json.dump(db_ids, f, ensure_ascii=False, indent=2)
        print(f"共提取 {len(db_ids)} 个数据库ID")
        print(f"转换完成，输出文件：{output_path}")
        return True
    except Exception as e:
        print(f"写入输出文件时出错: {e}")
        return False


if __name__ == "__main__":
    # 设置输入和输出文件路径
    tables_json_path = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omnisql\\tables.json"
    output_path = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\db_ids.json"

    # 检查输入文件是否存在
    if not os.path.exists(tables_json_path):
        print(f"错误：输入文件 {tables_json_path} 不存在")
    else:
        # 执行提取，默认限制为2000条
        extract_db_ids_json(tables_json_path, output_path)