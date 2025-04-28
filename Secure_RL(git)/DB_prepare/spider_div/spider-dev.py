import json
from tqdm import tqdm
import os
import sqlite3

# 输入路径
text2sql_data_dir = r'C:\Users\Lenovo\torch\research\NL2SQL\Code-S\data\sft_spider_dev_text2sql.json'
# 输出路径
output_path = r'../../data_synthesis/merged_schema_qa.json'

# -------- 工具函数 --------
def detect_special_char(name):
    return any(ch in name for ch in ['(', '-', ')', ' ', '/'])

def add_quotation_mark(s):
    return f'`{s}`'

def get_cursor_from_path(sqlite_path):
    if not os.path.exists(sqlite_path):
        print(f"Opening new connection: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path, check_same_thread=False)
    conn.text_factory = lambda b: b.decode(errors='ignore')
    return conn.cursor()

def execute_sql(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()

def filter_schema(dataset):
    for data in tqdm(dataset, desc="Filtering schema..."):
        filtered = {'schema_items': [], 'foreign_keys': []}
        for tbl in data['schema']['schema_items']:
            filtered['schema_items'].append({
                'table_name': tbl['table_name'],
                'column_names': tbl['column_names'],
                'column_types': tbl['column_types'],
                'column_comments': tbl['column_comments'],
                'column_contents': tbl['column_contents'],
                'pk_indicators': tbl['pk_indicators']
            })
        valid_tables = {tbl['table_name'] for tbl in filtered['schema_items']}
        for fk in data['schema'].get('foreign_keys', []):
            if fk[0] in valid_tables and fk[2] in valid_tables:
                filtered['foreign_keys'].append(fk)
        data['schema'] = filtered
    return dataset

def get_db_schema_sequence(schema):
    lines = ["database schema :"]
    for tbl in schema['schema_items']:
        tname = tbl['table_name']
        if detect_special_char(tname):
            tname = add_quotation_mark(tname)
        cols = []
        for name, typ, cmt, _, pk in zip(
            tbl['column_names'], tbl['column_types'], tbl['column_comments'],
            tbl['column_contents'], tbl['pk_indicators']
        ):
            nm = add_quotation_mark(name) if detect_special_char(name) else name
            parts = [typ]
            if pk:
                parts.append('primary key')
            if cmt:
                parts.append(f'comment : {cmt}')
            cols.append(f"{tname}.{nm} ( {' | '.join(parts)} )")
        lines.append(f"table {tname} , columns = [ {', '.join(cols)} ]")
    fks = schema.get('foreign_keys', [])
    if fks:
        lines.append("foreign keys :")
        for s_tbl, s_col, t_tbl, t_col in fks:
            s = add_quotation_mark(s_tbl) if detect_special_char(s_tbl) else s_tbl
            sc = add_quotation_mark(s_col) if detect_special_char(s_col) else s_col
            t = add_quotation_mark(t_tbl) if detect_special_char(t_tbl) else t_tbl
            tc = add_quotation_mark(t_col) if detect_special_char(t_col) else t_col
            lines.append(f"{s}.{sc} = {t}.{tc}")
    else:
        lines.append("foreign keys : None")
    return "\n".join(lines)

# -------- 主流程 --------
# 加载原始数据
with open(text2sql_data_dir, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# 过滤 schema
dataset = filter_schema(dataset)

# 构建合并记录
merged_items = []
for data in tqdm(dataset, desc='Building merged QA items'):
    seq = get_db_schema_sequence(data['schema'])
    merged_items.append({
        'schema_sequence': seq,
        'question': data.get('question', ''),
        'sql': data.get('sql', '')
    })

# 保存输出
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(merged_items, f, ensure_ascii=False, indent=2)

print(f"完成：共 {len(merged_items)} 条，保存在 {output_path}")
