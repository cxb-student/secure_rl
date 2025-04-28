import json

with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Final\U_WHOLE1.json", "r", encoding="utf-8") as f:
          data = json.load(f)

data.sort(key=lambda x: x.get('id'))
with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Final\U_WHOLE1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)