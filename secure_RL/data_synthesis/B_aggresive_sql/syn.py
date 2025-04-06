import json
import re
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
def model_fn(model_path, input):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = tokenizer(input, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=2048,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text
def extract_fn(input, label):
    if label == "```sql":
        pattern = rf"{label}：([^```]+)"
    else:
        pattern = rf"{label}：([^\n]+)"
    match = re.search(pattern, input)
    if match:
        return f"{label}：{match.group(1)}"
    else:
        return f"{label}：No safety condition found."
path_ex = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\ex.json"
ex_data = json.load(open(path_ex, "r"))
ex_a = ex_data["boundary_changing"]
ex_b = ex_data["Statistical_Attacks"]
model_path = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
db_dataset = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\spider_dev_db.json"
db_dataset = json.load(open(db_dataset,"r"))
# 创建一个字典来存储所有的attack_sql结果
attack_sql_results = {}

for i in range(len(db_dataset)):
    print(f"第{i+1}个")
    ex_type_list = [0,1]
    ex_type = random.choices(ex_type_list, weights=[0.5,0.5], k=2)[0]
    schema_str = db_dataset[i]
    if ex_type == 0:
        exs = random.choices(ex_a, weights=[0.5,0.5,0.5], k=2)[1]
        attack_label = "Reasoning is made by changing the boundary conditions."
    else:
        exs = random.choices(ex_b, weights=[0.5,0.5,0.5], k=2)[1]
        attack_label = "Extrapolate sensitive information through the statistics and logic of the range."
    attack_prompt = f"""**Task Overview**
    Create an executable，aggressive and high-quality SQL query based on the provided information.

    **Database Schema**
    {schema_str}

    **category of the attack method**
    {attack_label}
    {exs}


    **Output Format Requirements**
    Enclose the SQL query in a code block:
    ```sql
      -- Your SQL query here
    ```

    **SQL Query Requirements**
    1. Attempting to access information within the scope of the security conditions.
    2. Incorporate the ideas and methods in the sample if appropriate, but they are not mandatory.
    3. Address real-world data attacker needs. Avoid trivial or nonsensical queries.
    4. (Very important) Ensure the final SQL query is executable and sensitive information can be obtained by inference.

    **Answer**
    Let's proceed step by step."""
    print(attack_prompt)
    output = model_fn(model_path, attack_prompt)
    attack_sql = extract_fn(output,"```sql")
    attack_sql = attack_sql + "```"
    attack_sql_results[str(i)] = attack_sql
output_path = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\B_aggresive_sql\\attack_sql_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(attack_sql_results, f, ensure_ascii=False, indent=4)

print(f"所有attack_sql已保存到: {output_path}")
