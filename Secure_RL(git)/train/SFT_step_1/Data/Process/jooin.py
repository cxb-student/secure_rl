import json
import random
from collections import defaultdict



def extract_qa_pairs(file_path):
    """
    从文件中提取问答对，并按ID分类
    """
    ou_count = 0
    omni_count = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    qa_pairs_by_id = defaultdict(list)


    for item in data:
        # 获取ID

        item_id = item.get('id')
        if item_id is None:
            continue

        # 提取问题和回答
        if 'questions' in item and 'sql_list' in item:
            # 处理原始格式
            for q, a in zip(item['questions'], item['sql_list']):
                qa_pairs_by_id[item_id].append({
                    "Q": q,
                    "A": a
                })
                ou_count +=1

        # 检查是否有历史记录
        elif 'history' in item and isinstance(item['history'], list):

            qa_pairs_by_id[item_id].append(item['history'][0])
            omni_count+=1
    print(ou_count,omni_count)

    return qa_pairs_by_id


def extract_history_from_file(file_path):
    """
    从另一个文件中提取历史记录并按ID分类
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    history_by_id = defaultdict(list)

    for item in data:
        # 获取ID
        item_id = item.get('id')
        if item_id is None:
            continue

        # 提取历史记录
        if 'history' in item and isinstance(item['history'], list):
            history_by_id[item_id].append(item['history'][0])

    return history_by_id


def process_data_with_history(input_file, history_file,output_file):
    """
    在history_file基础上，通过随机取样添加历史记录来改变input
    只处理约13%的数据，并且只保存这13%的数据
    """
    # 读取输入数据（历史文件，已包含input和output）
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取问答对和历史记录
    qa_pairs_by_id = extract_qa_pairs(input_file)
    count = 0
    # 处理数据
    processed_data = []
    history_count_distribution = {0: 0, 1: 0, 2: 0}
    # 记录处理的数据比例
    processed_ratio = 0.13  # 只处理13%的数据

    for item in data:
        try:
            # 获取ID和当前问题
            db_id = item.get('id')
            if db_id is None:
                continue

            # 获取当前的input和output
            if 'input' not in item or 'output' not in item:
                continue

            input_text = item['input']
            output_text = item['output']


            # 初始化变量
            sampled_history = []
            is_processed = False  # 标记是否处理了这条数据
            
            # 随机决定是否处理这条数据（只处理13%的数据）
            if random.random() < processed_ratio:
                # 随机决定添加几条历史记录
                num_history = random.choice([0, 1, 2])
                history_count_distribution[num_history] += 1
                is_processed = True  # 标记为已处理

                # 从当前ID的历史记录中随机采样
                if num_history > 0 and db_id in qa_pairs_by_id and len(qa_pairs_by_id[db_id]) > 0:
                    # 排除当前问题
                    available_history = [h for h in qa_pairs_by_id[db_id]]
                    if available_history:
                        # 随机采样指定数量的历史记录
                        sampled_history = random.sample(available_history, min(num_history, len(available_history)))

            if sampled_history:
                his_list = []
                for idx, h in enumerate(sampled_history):
                    his_list.append(f"Turn-{idx + 1} :[ 'Question': {h['Q']}, 'SQL': {h['A']}]\n")
                history_str = "".join(his_list)
                if "**Assistant**" in input_text:
                    count+=1
                    continue


                input_text=input_text.replace("{chat history}",f"{history_str}\n")
                if "Turn-2" in input_text:
                    print(input_text)
            else:
                if "**Assistant**" in input_text:
                    count+=1
                    continue
                input_text = input_text.replace("\n**Chat history**", "")
                input_text = input_text.replace("\n{chat history}", "")
                input_text = input_text.replace("\nIn addition to the question and schema, you will also receive a streamlined chat history from colleagues. This chat history may contain helpful context or prior attempts—correct or not—and is intended to assist you in formulating a precise and well-informed response. ", "")



            # 只添加被处理过的数据到结果列表
            if is_processed:
                processed_data.append({
                    "id": db_id,
                    "input": input_text,
                    "output": output_text
                })


        except Exception as e:
            continue
    print(count)
    # 打印历史记录分布
    print("历史记录分布:")
    total = sum(history_count_distribution.values())
    if total > 0:
        for count, frequency in sorted(history_count_distribution.items()):
            print(f"  历史记录数量 {count}: {frequency} 条数据 ({frequency / total * 100:.2f}%)")
    
    # 打印处理数据比例
    print(f"总数据量: {len(data)}, 处理数据量: {len(processed_data)}, 处理比例: {len(processed_data)/len(data)*100:.2f}%")

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"已处理 {len(processed_data)} 条数据并保存到 {output_file}")


if __name__ == "__main__":
    input_file = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\our\U_put_balance.json"
    history_file = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\train\SFT\Data\Process\Omni_v1.json"
    output_file = "Omni_v12.json"

    process_data_with_history(input_file, history_file, output_file)