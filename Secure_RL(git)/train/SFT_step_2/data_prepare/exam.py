import json

with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\E_secure_COT\safe_cot\Syn_Ultimate_clean_with_injection.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for item in data:
    if item["label"]=="injection":
        print(item["questions"][-1])
        print(item["secure_cot"])