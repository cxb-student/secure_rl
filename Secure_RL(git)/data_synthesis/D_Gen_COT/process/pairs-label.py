import json


def merge_labels(json1_path, json2_path, output_path):
    # Load the two JSON files
    with open(json1_path, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)
    with open(json2_path, 'r', encoding='utf-8') as f2:
        data2 = json.load(f2)

    # Group json2 entries by their 'id'
    json2_by_id = {}
    for entry in data2:
        entry_id = entry.get('id')
        if entry_id is None:
            continue
        json2_by_id.setdefault(entry_id, []).append(entry)

    # Iterate over json1 entries and assign labels
    for item in data1:
        item_id = item.get('id')
        if item_id is None:
            print("id不匹配")
            continue

        # Retrieve the list of SQLs from json1 (ensure a list)
        sql_list = item.get('sql_list')
        sqls = sql_list if isinstance(sql_list, list) else [sql_list]

        assigned_label = None
        candidates = json2_by_id.get(item_id, [])

        # For each SQL in json1, find matching entry in json2
        match = next((e for e in candidates if e.get('extracted_sql') == sqls), None)
        if match:
                print("匹配成功")
                raw_label = match.get('label')
                # If json1 marked this item as safe, override to 'safe'
                if item.get('safe_label') == 'safe':
                    print()
                    assigned_label = 'safe'
                else:
                    # If json2's label is null/None, mark as 'vil'
                    assigned_label = 'Confused' if raw_label is None else raw_label
        else:
                print(e for e in candidates if e.get('extracted_sql'))
                print(sqls)
                print("匹配失败")

        # Attach the computed label back to the json1 item
        item['label'] = assigned_label
        if assigned_label == "safe":
            print(item)

    # Write the updated data back to a new JSON file
    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(data1, fout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # Example usage:
    merge_labels(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\U_put.json',
                 r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Final\U_WHOLE.json',
                 'json1_with_labels.json')