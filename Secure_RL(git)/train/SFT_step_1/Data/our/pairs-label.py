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
            continue

        # Retrieve the list of SQLs from json1 (ensure a list)
        sql_list = item.get('sqlist')
        sqls = sql_list if isinstance(sql_list, list) else [sql_list]

        assigned_label = None
        # For each SQL in json1, find matching entry in json2
        for sql in sqls:
            # Look up json2 entries for this id
            candidates = json2_by_id.get(item_id, [])
            # Find the first entry whose exact SQL matches
            match = next((e for e in candidates if e.get('exacct-sql') == sql), None)
            if match:
                raw_label = match.get('label')
                # If json1 marked this item as safe, override to 'safe'
                if item.get('safe-label') == 'safe':
                    assigned_label = 'safe'
                else:
                    # If json2's label is null/None, mark as 'vil'
                    assigned_label = 'vil' if raw_label is None else raw_label
                break

        # Attach the computed label back to the json1 item
        item['label'] = assigned_label

    # Write the updated data back to a new JSON file
    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(data1, fout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # Example usage:
    merge_labels('json1.json', 'json2.json', 'json1_with_labels.json')