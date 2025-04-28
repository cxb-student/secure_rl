import json
import random


def process_data(input_json_path, db_desc_path, output_path):
    # 读取输入数据
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取数据库描述
    with open(db_desc_path, 'r', encoding='utf-8') as f:
        db_descriptions = json.load(f)
    output_list = []
    for item in data:
            # 获取数据库描述
            db_id = item['id']
            db_desc = db_descriptions[db_id]
            # 获取问题列表和SQL列表
            questions = item['questions']
            sql_list = item['sql_list']
            history = []
            for q, s in zip(questions[:-1], sql_list[:-1]):
                history.append({
                    "Q": q,
                    "A": s
                })
            safe_condition = item["safe_condition"]
            specific_column = item["specific_column"]
            specific_value = item["specific_value"]
            if len(history) == 0:
                chat_history = "The current question is the first question."
            else:
                history_items = []
                for idx, h in enumerate(history):
                    history_items.append(f"\nTurn-{idx + 1} :[ 'Question': {h['Q']}, 'SQL': {h['A']}]")
                chat_history = "".join(history_items)
            input_secure = f"""**Task Overview**
You are a Senior Data Analyst with deep expertise in SQL. When given:
1.A question from a front-end teammate
2.The corresponding database schema with safe condition
3.A concise chat history of prior discussion
your goal is to:
1.First, perform a security review against the schema and chat history.
If the question risks exposing restricted or sensitive fields or conditions, you must label the response as unsafe and stop—do not generate any SQL.
2.Then, if it’s safe, translate the question into a precise SQLite query, and provide a step-by-step explanation of your reasoning.
**Database Schema** 
{db_desc}
safe_condition:{safe_condition}
**Chat history**
{chat_history}
**Output Format Requirements** 
To enable automated SQL extraction via regex, your reply must follow this exact format:
<secureCOT>
(Provide detailed reasoning here about whether it is safe to answer. Include any conditions checked, sensitive fields identified, etc.You can analysis in this way["first,I need to check and understand the safe_condition."...."Then,I need to figure out what can be infered or get from these queries."],which may help you.
</secureCOT>
<secure_output>(safe or unsafe)</secure_output>
<sql_COT>
(If safe: Explain your SQL reasoning step by step.And put your answer in a code box like
'''sql
select * from table
'''
If unsafe: Say clearly that you cannot answer due to security concerns.)
</sql_COT>
**Question**
{questions[-1]}
**Answer** 
Let's proceed step by step."""
            unsafe_response = [
                    "I’m unable to provide a SQL query, as it would potentially reveal restricted or sensitive data based on the current context.",
"Due to security constraints, I must refrain from answering—this query risks exposing protected fields.",
"Answering this question would involve referencing sensitive information, which is not allowed under the current data access policy.",
"Generating SQL for this request would breach the defined safety conditions. I cannot proceed.",
"Unfortunately, this question touches on restricted fields, so I won’t be able to provide an SQL statement.",
"The information required to answer this safely includes sensitive columns. I have to mark this as unsafe.",
"This request falls outside of safe operational boundaries—certain field(s) involved are classified as restricted.",
"I reviewed the schema and context, and generating a query would lead to exposure of confidential data, so I must decline.",
"Providing an answer here would violate security rules due to inclusion of protected attributes.",
"For data privacy reasons, I can't fulfill this request—doing so would compromise field-level security."
                ]
            if item["safe_label"] == "unsafe":
                    output = item["secure_cot"]+"<sql_COT>"+random.choice(unsafe_response)+"</sql_COT>"
                    #随机选择一个拒绝回复
            elif item["safe_label"] == "safe":
                    output = item["secure_cot"]+"<sql_COT>"+item["SQL_COT"][-1]+"</sql_COT>"
            else:
                    print("error")
                    continue
            output_list.append({
                        "id": item["id"],
                        "input": input_secure,
                        "output": output
                    })
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, ensure_ascii=False, indent=4)
    return output_list

output_list = process_data(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\Syn_Ultimate_clean_with_injection.json"
             ,r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\omni_2000.json",
             r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT_step_2\data_prepare\SFT_stage_2_V2.json")
print(len(output_list))