import json

with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\evaluate\secure-sql\dev.json",  "r", encoding="utf-8")as f:
    data = json.load(f)
with  open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\all_with_db_id111.json",  "r", encoding="utf-8")as f:
    db_data = json.load(f)
db_list = []
Ulti = []
for item in data:
    db  = item["db_id"]
    db_list.append(db)
#去重
db_list = list(set(db_list))
for id in db_list:
    if_have = False
    for item in db_data:
        if item["db_id"] == id:
            if_have = True
            Ulti.append(item)
        else:
            continue
    if if_have:
        continue
    else:
        print(f"{id}")
with open(r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\evaluate\secure-sql\db_filtered.json",  "w", encoding="utf-8")as f:
    json.dump(Ulti,f,ensure_ascii=False,indent=4)