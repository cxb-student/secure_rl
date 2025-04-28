import json
from collections import defaultdict

# 设置输入输出文件路径
main_json_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\process\grou_output.json'  # 主数据文件路径
ref_json_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\db_ids.json'  # 正确db_id参考文件路径
output_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\222.json' # 输出文件路径

# 读取主数据
with open(main_json_path, 'r', encoding='utf-8') as f:
    main_data = json.load(f)

# 读取参考数据（假设为id->db_id的映射字典或列表）
with open(ref_json_path, 'r', encoding='utf-8') as f:
    ref_data = json.load(f)

print(f'原始数据长度：{len(main_data)}')
count = 0
result = []
for item in main_data:
    item_id = item.get('item_id')
    db_id = item.get('db_id')
    correct_dbid = ref_data[item_id]
    if correct_dbid is not None and db_id == correct_dbid:
        result.append(item)
    else:
        count += 1
print(f'去除db_id不正确的项数量：{count}')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'处理完成，已按item_id分类并去除db_id不正确的项，结果保存在{output_path}')