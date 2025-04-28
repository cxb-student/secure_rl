#将两个json文件直接拼接起来

import json

with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\part_0.json', 'r',encoding='utf-8')as f:
    data1 = json.load(f)
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\part_1.json', 'r',encoding='utf-8')as f:
    data2 = json.load(f)


data1.extend(data2)
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\output.json', 'w',encoding='utf-8')as f:
    json.dump(data1, f, ensure_ascii=False, indent=4)
