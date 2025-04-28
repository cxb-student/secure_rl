import json
import re

# 读取 grouped_output.json
with open(r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\222.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


def extract_last_question(text):
    # 标准化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    prefix_pattern = r'(?:\*\*Q[:：]\*\*|Q[:：]|\*\*Q:\*\*|\*\*Q：\*\*|\*\*Q\*\*[:：]|\*\*Q\*\*:)'

    # 匹配格式为：
    # Q前缀 后跟 [xxx]，或任意问句（以 ? 或 . 结尾），可跨行
    full_pattern = re.compile(
        rf'{prefix_pattern}\s*\n?\s*(\[[^\[\]]+?\]|.+?[?.])',
        re.IGNORECASE
    )

    matches = full_pattern.findall(text)

    if not matches:
        return None

    last = matches[-1].strip()

    # 如果是 [xxx] 格式，去除括号
    if last.startswith('[') and last.endswith(']'):
        last = last[1:-1].strip()
    
    # 去除两端的单引号
    last = last.strip("'")
    return last

count = 0
# 对每组数据提取 output 中的问题
for item in data:
    item['questions'] = []
    for output in item['outputs']:
        question = extract_last_question(output)
        if question:
            item['questions'].append(question)
        else:
            print(f"No question found in output: {output}")
            count += 1
            item['questions'].append("What are the names and email addresses of principals in schools with a student-teacher ratio greater than 15？")

# 保存结果（包含提取的问题）
print(f"没有问题的数量: {count}")
# 删除output键
for item in data:
    del item['outputs']

with open('extracted_questions111.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("问题已提取并保存在 extracted_questions.json")
