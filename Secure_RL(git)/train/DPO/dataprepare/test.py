import json

input_path  = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\DPO\dataprepare\generated_predictions_wo_cv.json'
output_path = 'Generated_wo_cv.json'

data = []
with open(input_path, 'r', encoding='utf-8') as fin:
    for line in fin:
        # 跳过空行
        line = line.strip()
        if not line:
            continue
        # 逐行解析 JSON 并追加到列表
        obj = json.loads(line)
        data.append(obj)

# 把列表写成标准 JSON 数组
with open(output_path, 'w', encoding='utf-8') as fout:
    json.dump(data, fout, ensure_ascii=False, indent=2)

print(f"已将 {input_path} 转换为列表并保存到 {output_path}")
