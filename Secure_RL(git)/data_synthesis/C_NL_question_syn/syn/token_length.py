import json
import os
import argparse
from tqdm import tqdm
from transformers import AutoTokenizer
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--Input_sql",  help="总文件的路径（全部的）")
    parser.add_argument( "--schema_dir",  help="omni2000的那个文件")
    parser.add_argument( "--output_mapping",  help="匹配的存储的地方，为了后期的数据处理")
    parser.add_argument('--model_path', type=str,help='模型路径')
    parser.add_argument('--output_path', type=str,help='输出文件路径')
    parser.add_argument('--batch_size', type=int,help='批处理大小')
    parser.add_argument('--part', type=int,help='分成一半一半来，上一半是0，下一半是1',choices=[0,1])
    return parser.parse_args()
PROMPT_TEMPLATE = """**Task Overview**
Your task is to create a high-quality natural language question based on a given SQL query and other information.

**Database**
{database_str}

**SQL Query**
Given SQL query:
'''sql
{sql}
'''

**Output Format**
Please structure your response as follows:
Q：['question'].

**Insturction**
1.Uses standard grammar and vocabulary.
- Example: ['Find all students older than 18 years and return their home addresses.']
2.Clearly describe the columns being selected by the SQL query.
3. Ensure the natural language question accurately captures the semantics of the SQL query, including conditions such as predicates, ORDER BY, and LIMIT clauses.

**Answer**
Let's proceed step by step"""

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_schema(db_id, schema_dir):
    with open(schema_dir, "r", encoding="utf-8") as f:
        schema_str = json.load(f)
        return schema_str[db_id]

def main(args):
    lun = 0
    data = load_json(args.Input_sql)
    data_length = len(data)
    if args.part == 0:
        data = data[:data_length // 2]
    else:
        data = data[data_length // 2:]
    all_prompts = []
    mapping_info = []
    skipped_count = 0

    for idx, item in tqdm(enumerate(data), total=len(data), desc="Processing"):
        db_id = item["db_id"]
        id = item["id"]
        sql_list = item["extracted_sql"]
        schema_str = load_schema(id, args.schema_dir)

        if not schema_str:
            print(f"[Skip] Missing schema for {db_id}")
            continue

        for sql_idx, sql in enumerate(sql_list):
            prompt = PROMPT_TEMPLATE.format(
                database_str=schema_str.strip(),
                sql=sql.strip()
            )
            all_prompts.append(prompt)
            mapping_info.append({
                "item_idx": idx,
                "sql_idx": sql_idx,
                "item_id": id,
                "db_id": db_id,
                "sql": sql
            })


    with open(args.output_mapping, "w", encoding="utf-8") as f:
        json.dump(mapping_info, f, indent=2, ensure_ascii=False)


    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    total_tokens = 0
    for prompt in all_prompts:
        inputs = tokenizer(prompt, return_tensors="pt")
        total_tokens += inputs["input_ids"].shape[1]
    print(total_tokens / len(all_prompts))