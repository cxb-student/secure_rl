#将两个json文件直接拼接起来

import json

with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\Omni_v12.json', 'r',encoding='utf-8')as f:
    data1 = json.load(f)
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\our_v1.json', 'r',encoding='utf-8')as f:
    data2 = json.load(f)
print(len(data1))
print(len(data2))
for i in range(len(data1)):
    del data1[i]["id"]
data1.extend(data2)
print(len(data1))
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\U_V2.json', 'w',encoding='utf-8')as f:
    json.dump(data1, f, ensure_ascii=False, indent=4)
