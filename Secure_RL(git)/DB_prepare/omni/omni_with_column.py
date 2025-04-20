import json
import os
import sqlite3

def get_db_path(db_id):
    """根据数据库ID获取数据库文件路径"""
    # 尝试几个可能的路径
    possible_paths = [
        f"C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omnisql\\databases\\databases\\{db_id}\\{db_id}.sqlite"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def query_example_values(db_path, table_name, column_name, limit=4):
    """查询指定表和列的示例值"""
    if not db_path or not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 尝试查询该列的不同值，限制为limit个
        try:
            cursor.execute(f"SELECT DISTINCT \"{column_name}\" FROM \"{table_name}\" WHERE \"{column_name}\" IS NOT NULL LIMIT 10")
            values = list({str(row[0]) for row in cursor.fetchall()})
            
            if len(values) >= 3:
                return values[:3]
            elif len(values) == 2:
                return values[:2]
            elif len(values) == 1:
                return values[:1]
            return []
        except sqlite3.OperationalError:
            # 如果查询失败，返回默认值
            return []
    except Exception as e:
        print(f"查询数据库时出错: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def convert_tables_to_all_with_column(tables_json_path, output_path, limit=None):
    # 读取tables.json文件
    with open(tables_json_path, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)
    
    # 如果设置了限制，则只处理指定数量的数据库
    if limit and limit > 0:
        tables_data = tables_data[:limit]
        print(f"注意：只处理前 {limit} 个数据库")
    
    all_with_column_data = []
    
    # 遍历每个数据库
    for db_info in tables_data:
        # 获取数据库名称
        db_id = db_info.get('db_id', '')
        
        # 获取数据库文件路径
        db_path = get_db_path(db_id)
        if db_path:
            print(f"找到数据库: {db_id} 路径: {db_path}")
        else:
            print(f"未找到数据库: {db_id}，将使用默认示例值")
        
        # 获取表信息
        table_names = db_info.get('table_names_original', [])
        column_names= db_info.get('column_names_original', [])
        column_types = db_info.get('column_types', [])
        
        # 获取主键信息
        primary_keys = db_info.get('primary_keys', [])
        
        # 获取外键信息
        foreign_keys = db_info.get('foreign_keys', [])
        
        # 构建数据库模式描述
        schema_desc = ""
        
        # 处理每个表
        for table_idx, table_name in enumerate(table_names):
            schema_desc += f"table {table_name} , columns = [ "
            
            # 查找属于该表的所有列
            table_columns = []
            column_counter = 0  # 新增列计数器
            for col_idx, (tab_idx, col_name) in enumerate(column_names):
                if tab_idx == table_idx:
                    # 获取列的原始名称和类型
                    col_type = column_types[col_idx].lower() if col_idx < len(column_types) else "text"
                    col_type = col_type.replace('integer', 'int')
                    # 检查是否是主键
                    is_primary = col_idx in primary_keys
                    primary_key_str = " | primary key" if is_primary else ""
                    
                    # 查询示例值
                    example_values = query_example_values(db_path, table_name, col_name)
                    if len(example_values) == 2:
                        example_str = f" | example values : {example_values[0]}, {example_values[1]}"
                        col_desc = f"{table_name}.{col_name} ( {col_type}{primary_key_str}{example_str} )"
                        table_columns.append(col_desc)
                        # 当有效列达到6个时停止处理
                        if column_counter >= 6:
                            break
                        column_counter += 1  # 计数器递增
                    elif len(example_values) < 2:
                        col_desc = f"{table_name}.{col_name} ( {col_type}{primary_key_str}  )"
                        table_columns.append(col_desc)
                        # 当有效列达到6个时停止处理
                        if column_counter >= 6:
                            break
                        column_counter += 1  # 计数器递增
                    elif len(example_values) == 3:
                        example_str = f" | example values : {example_values[0]}, {example_values[1]}, {example_values[2]}"
                        col_desc = f"{table_name}.{col_name} ( {col_type}{primary_key_str}{example_str} )"
                        table_columns.append(col_desc)
                        # 当有效列达到6个时停止处理
                        if column_counter >= 6:
                            break
                        column_counter += 1  # 计数器递增

                    # 构建列描述


            # 将列添加到表描述中
            schema_desc += ", ".join(table_columns) + " ]\n"

        # 添加外键信息
        if foreign_keys:
            schema_desc += "foreign keys :\n"
            for fk in foreign_keys:
                # 获取外键列和引用列的信息
                fk_col_idx = fk[0]
                ref_col_idx = fk[1]
                
                if fk_col_idx < len(column_names) and ref_col_idx < len(column_names):
                    fk_tab_idx, fk_col_name = column_names[fk_col_idx]
                    ref_tab_idx, ref_col_name = column_names[ref_col_idx]
                    
                    if fk_tab_idx < len(table_names) and ref_tab_idx < len(table_names):
                        fk_tab_name = table_names[fk_tab_idx]
                        ref_tab_name = table_names[ref_tab_idx]
                        
                        schema_desc += f"{fk_tab_name}.{fk_col_name} = {ref_tab_name}.{ref_col_name}\n"
        else:
            schema_desc += "foreign keys : None\n"
        
        # 将数据库模式添加到结果中
        all_with_column_data.append(schema_desc)
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_with_column_data, f, ensure_ascii=False, indent=2)
    
    print(f"转换完成，输出文件：{output_path}")


if __name__ == "__main__":
    # 设置输入和输出文件路径
    tables_json_path = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omnisql\\tables.json"
    output_path = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\omni_2000_with_column.json"

    # 检查输入文件是否存在
    if not os.path.exists(tables_json_path):
        print(f"错误：输入文件 {tables_json_path} 不存在")
    else:
        # 执行转换，只处理前10个数据库
        convert_tables_to_all_with_column(tables_json_path, output_path, limit=2000)