import json
import re

count = 0
wrong_count =0
with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\output_with_secure_cot.json", "r", encoding="utf-8") as f:
    data = json.load(f)
print(len(data))
for item in data:
    syn_output = item["secure_cot" ]
    #提取<secure_output></secure_output>中的内容
    syn_output1 = syn_output.split("<secure_output>")[1].split("</secure_output>")[0]
    safe_label = item["safe_label"]
    if safe_label != syn_output1:
        #删除这项
        wrong_count+=1
        data.remove(item)

    #保证syn——output完全按照这个格式来的<secureCOT>...</secureCOT><secure_result>...</secure_result>
    cot_match = re.search(r"<secureCOT>(.*?)</secureCOT>", syn_output, re.DOTALL)
    cot = cot_match.group(1).strip() if cot_match else print("No match found")

    # Extract content inside <secure_result> tags
    result_match = re.search(r"<secure_output>(.*?)</secure_output>", syn_output, re.DOTALL)
    result = result_match.group(1).strip() if result_match else print("No match found")
    new_one = f"<secureCOT>{cot}</secureCOT>\n<secure_output>{result}</secure_output>"
    if new_one != item["secure_cot"]:
       count += 1
       print(new_one)
       item["secure_cot"]= new_one

print(len(data))
with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\output——filtered.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print("ss",count)
print("move",wrong_count)