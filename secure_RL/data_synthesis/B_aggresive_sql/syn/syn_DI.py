#生成攻击性sql

import json
import random
import argparse
import os
import re

from tqdm import tqdm
from transformers import AutoTokenizer
# from vllm import LLM, SamplingParams

def parse_args():
    parser = argparse.ArgumentParser(description='生成攻击性sql')
    parser.add_argument('--condition_path', type=str,
                        help='安全条件路径')
    parser.add_argument('--prompts_path', type=str,
                        help='提示词打包存放处')
    parser.add_argument('--model_path', type=str,
                        help='模型路径')
    parser.add_argument('--db_dataset', type=str,
                        help='数据库数据集路径')
    parser.add_argument('--ex_path', type=str,
                        help='示例文件路径')
    parser.add_argument('--output_path', type=str,
                        help='输出文件路径')
    parser.add_argument('--batch_size', type=int,
                        help='批处理大小')
    parser.add_argument('--prompts_per_type', type=int, default=3,
                        help='每种攻击类型生成的prompt数量')
    return parser.parse_args()

# 攻击类型说明
# 1是边界试探
# 2是聚合推断
# 3是极值排序
# 4是递进定位
# 5是补集攻击
# 6是直接攻击

def if_number(specific_column):
    # 定义数值类型的关键词
    numeric_types = {'int', 'integer', 'real', 'float', 'double', 'decimal', 'numeric'}

    # 用正则提取出所有列的 (name, type)
    matches = re.findall(r'\b\w+\.(\w+)\s*\((\w+)\)', specific_column)

    # 遍历检查类型是否是数值型
    for _, col_type in matches:
        if col_type.lower() in numeric_types:
            return True
    return False

def if_cells(specific_value):
    if specific_value == "None":
        return False
    return True

def get_prompt_template(attack_type, is_number, is_cells):
    # 根据攻击类型和条件选择对应的prompt模板
    # 从prompt.json加载提示词模板
    with open(os.path.join(os.path.dirname(__file__), "prompt.json"), 'r', encoding="utf-8") as f:
        prompt_templates = json.load(f)
    template_key = ""
    # 根据攻击类型设置模板键名
    if attack_type == "1":  # 边界试探
        template_key = "Boundary"
    elif attack_type == "2":  # 聚合推断
        template_key = "Aggregation"
    elif attack_type == "3":  # 极值排序
        template_key = "Equivalence"
    elif attack_type == "4":  # 递进定位
        template_key = "Incremental"
    elif attack_type == "5":  # 补集攻击
        template_key = "Complement"
    elif attack_type == "6":  # 直接攻击
        template_key = "Directly"
    
    # 根据条件选择具体的模板
    if template_key in prompt_templates:
        if is_cells and is_number:
            return prompt_templates.get(template_key, {}).get("is_cells_and_number", "默认模板")
        elif is_cells and not is_number:
            return prompt_templates.get(template_key, {}).get("is_cells_and_not_number", "默认模板")
        elif not is_cells and is_number:
            return prompt_templates.get(template_key, {}).get("is_column_and_number", "默认模板")
        else:
            return prompt_templates.get(template_key, {}).get("is_column_and_not_number", "默认模板")
    else:
        # 如果找不到对应的模板键名，返回默认模板
        return "默认模板"

def get_example_key(secure_type):
    # 根据安全类型返回对应的示例键名
    example_keys = {
        "1": "Boundary",
        "2": "Aggregation",
        "3": "Equivalence_max_not_in_column",  # 极值排序
        "4": "Incremental",  # 递进定位
        "5": "Complement",  # 补集攻击
        "6": "Direct"  # 直接攻击
    }
    return example_keys.get(secure_type, "")

def generate_prompt(attack_type, safe_condition, schema_str, exs):
    safe_con = safe_condition["safe_condition"]
    specific_column = safe_condition["specific_column"]
    specific_value = safe_condition["specific_value"]
    is_number = if_number(specific_column)
    is_cells = if_cells(specific_value)
    prompt_template = get_prompt_template(attack_type, is_number, is_cells)
    example_key = get_example_key(attack_type)
    
    # 随机选择两个示例
    ex_samples = random.sample(exs.get(example_key, []), k=min(2, len(exs.get(example_key, []))))
    if len(ex_samples) == 0:
        prompt_template = prompt_template.replace("{exs}", "\n")
    else:

        ex_string = ex_samples[0]
        if len(ex_samples) > 1:
            ex_string += "\n\n" + "There is another example" + "\n" + ex_samples[1]
        prompt_template = prompt_template.replace("{exs}", ex_string)
    schema_str = schema_str+"\n" +f"safe_condition: {safe_con}" + "\n" + f"specific_column: {specific_column}" + "\n" + f"specific_value: {specific_value}"
    # 替换模板中的占位符
    prompt = prompt_template.replace("{schema_str}", schema_str).replace("{specific_column}", specific_column).replace("{specific_value}", specific_value)
    print(prompt)
    return prompt

def main():
    args = parse_args()
    lun = 0
    # 从安全条件结果中抽取数据
    with open(args.condition_path, 'r', encoding="utf-8") as f:
        safe_conditions = json.load(f)
    
    # 加载示例数据
    with open(args.ex_path, 'r', encoding="utf-8") as f:
        exs = json.load(f)
    
    # 加载数据库数据集
    with open(args.db_dataset, 'r', encoding="utf-8") as f:
        db_dataset = json.load(f)

    
    all_prompts = []  
    all_labels = []
    all_ids = []
    
    # 对应每个安全条件模式生成prompts
    for i in range(len(safe_conditions)):
        if safe_conditions[i]:
            safe_condition = safe_conditions[i]
        else:
            continue
        schema_str = db_dataset[int(safe_condition["id"])]
        
        # 对每种攻击类型生成prompts
        for attack_type in ["6"]:
            # 设置标签
            label_map = {
                "1": "Boundary",
                "2": "Aggregation",
                "3": "Equivalence_max_not_in_column",
                "4": "Incremental",
                "5": "Complement",
                "6": "Direct"
            }
            label = label_map.get(attack_type, "")
            
            # 为每种攻击类型生成多个prompts
            for _ in range(args.prompts_per_type):
                prompt = generate_prompt(attack_type, safe_condition, schema_str, exs)
                if prompt:
                    all_prompts.append(prompt)
                    all_labels.append(label)
                    all_ids.append(safe_condition["id"])
    
    # 保存prompts到文件
    with open(args.prompts_path, "w", encoding="utf-8") as fw:
        fw.write(json.dumps(all_prompts, indent=2, ensure_ascii=False))
    
    # 保存ids到单独文件
    ids_path = os.path.join(os.path.dirname(args.prompts_path), "prompt_ids.json")
    with open(ids_path, "w", encoding="utf-8") as fw:
        fw.write(json.dumps(all_ids, indent=2, ensure_ascii=False))
    
    print(f"共生成 {len(all_prompts)} 个prompts，保存成功")
    print(f"共保存 {len(all_ids)} 个prompt对应的id，保存成功")

    # # 加载模型和分词器
    # tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    # llm = LLM(model=args.model_path,
    #           tensor_parallel_size=1,
    #           gpu_memory_utilization=0.9)
    # print(f"loading model from: {args.model_path}")
    # os.system("nvidia-smi")
    #
    # # 设置采样参数
    # sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=500)
    # batch_size = args.batch_size
    #
    # # 应用聊天模板
    # chat_prompts = [tokenizer.apply_chat_template(
    #     [{"role": "user", "content": prompt}],
    #     add_generation_prompt=True, tokenize=False
    # ) for prompt in all_prompts]
    #
    # # 分批处理
    # batches = [chat_prompts[i:i + batch_size] for i in range(0, len(chat_prompts), batch_size)]
    # results = []
    #
    # # 批量推理
    # for batch in tqdm(batches, unit="batch"):
    #     outputs = llm.generate(batch, sampling_params=sampling_params)
    #     for data, output, label in zip(batch, outputs, all_labels[len(results):len(results)+len(batch)]):
    #         raw_responses = output.outputs[0].text
    #         results.append({'label': label, 'input': data, 'output': raw_responses})
    #
    # # 保存结果
    # if lun % 5 == 0:
    #     with open(args.output_path, "w", encoding="utf-8") as fw:
    #         fw.write(json.dumps(results, indent=2, ensure_ascii=False))
    # lun += 1
    # print(f"Results saved in {args.output_path}")

if __name__ == "__main__":
    main()