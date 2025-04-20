import json

# 读取output_errors.json文件
try:
    with open('output_errors2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 创建一个字典来存储每个label的计数
    label_counts = {}

    # 遍历数据并统计每个label的数量
    for item in data:
        label = item.get('label')
        if label:
            label_counts[label] = label_counts.get(label, 0) + 1

    # 打印统计结果
    print('每个label的数量统计结果：')
    for label, count in label_counts.items():
        print(f'Label "{label}": {count} 条记录')

except FileNotFoundError:
    print('错误：找不到output_errors.json文件')
except json.JSONDecodeError:
    print('错误：文件不是有效的JSON格式')
except Exception as e:
    print(f'发生错误：{str(e)}')