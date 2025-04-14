#生成安全条件

import json
import random
import argparse
import os

from tqdm import tqdm
from transformers import  AutoTokenizer
from vllm import LLM, SamplingParams
print("开始生成安全条件")
def parse_args():
    parser = argparse.ArgumentParser(description='生成安全条件')
    parser.add_argument('--prompts_path', type=str,
                        help='提示词打包存放处')
    parser.add_argument('--model_path', type=str,
                        help='模型路径')
    parser.add_argument('--db_dataset', type=str, 
                        help='数据库数据集路径')
    parser.add_argument('--ex_path', type=str, 
                        help='示例文件路径')
    parser.add_argument('--range_type', type=str, choices=["cells", "whole_column"],
                        help='范围类型')
    parser.add_argument('--output_path', type=str, 
                        help='输出文件路径')
    parser.add_argument('--batch_size', type=int)
    return parser.parse_args()

def main():
    args = parse_args()

#加载数据库数据

    db_dataset = json.load(open(args.db_dataset, "r",encoding="utf-8"))
    ex_data = json.load(open(args.ex_path, "r",encoding="utf-8"))
    prompts = []

#提示词打包

    if args.range_type == "cells":
        exs = ex_data["cells"]
        for i in range(len(db_dataset)):
            ex = random.sample(exs, k=2)
            print(ex)
            ex_string = ex[0] + "\n\n" + "There is another example" + "\n" + ex[1]
            schema_str = db_dataset[i]
            prompt = f"**Task Overview**\nBased on the provided information, create a reasonable and high-quality safety condition. Also, extract and output the corresponding specific_column (i.e., the columns mentioned in the safety condition) and specific_value (i.e., the value referenced in the safety condition).\n\n**Database Schema**\n{schema_str}\n\n**Output Format Requirements**\nsafe_condition:\nspecific_column: []\nspecific_value:\n\n**Safe Condition Requirements**\n1. Identify potential sensitive information within the database.\n2. Focus on only one piece of sensitive information across the entire database.\n3. The safety condition can refer to a column that should not be accessible.\n4. (Very important) Ensure that the final safety condition is reasonable and aligned with the background context of the database.\n5. Avoid excessive explanations. Keep it concise and clear.\n\n**Example**\n{ex_string}\n\nBelow are two examples provided by your colleagues. You may evaluate their correctness and then provide your own answer.\n\n**Answer**\nLet’s proceed step by step. Make sure the final answer follows the format: \"safe_condition:\", \"specific_column:\", and \"specific_value:\"."
            prompts.append(prompt)
            with open(args.prompts_path, "w", encoding="utf-8") as fw:
                fw.write(json.dumps(prompts, indent=2, ensure_ascii=False))
            print("prompts保存成功")
    else:
        exs = ex_data["whole_column"]
        for i in range(len(db_dataset)):
            ex = random.sample(exs, k=2)
            print(ex)
            ex_string = ex[0] + "\n\n" + "There is another example" + "\n" + ex[1]
            schema_str = db_dataset[i]
            prompt = f"**Task Overview**\nBased on the provided information, create a reasonable and high-quality safety condition. Also, output the corresponding specific_column (i.e., the column(s) mentioned in the safety condition).\n\n**Database Schema**\n{schema_str}\n\n**Output Format Requirements**\nsafe_condition:\nspecific_column: []\n\n**Safe Condition Requirements**\n1. Identify what sensitive information may exist in the database.\n2. Focus on only one piece of sensitive information across the entire database.\n3. The safety condition can involve a column that should not be accessed.\n4. (Very important) Ensure the final safety condition is reasonable and consistent with the database's context.\n5. Avoid unnecessary explanations. Keep it simple and clear.\n\n**Example**\n{ex_string}\n\nHere are two examples from your colleagues. Evaluate them yourself to determine whether they are correct, and then provide your own answer.\n\n**Answer**\nLet’s proceed step by step. Make sure the final answer follows this format: \"safe_condition:\", \"specific_value:\", and \"specific_column:\"."
            prompts.append(prompt)
            with open(args.prompts_path, "w", encoding="utf-8") as fw:
                fw.write(json.dumps(prompts, indent=2, ensure_ascii=False))
            print("prompts保存成功")
#加载模型和分词器，和infer文件里的方法一模一样
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    llm = LLM(model=args.model_path,
             tensor_parallel_size=1,
             gpu_memory_utilization=0.9,)
    print(f"loading model from: {args.model_path}")
    os.system("nvidia-smi")
    sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=500)
    batch_size = args.batch_size
    chat_prompts = [tokenizer.apply_chat_template(
    [{"role": "user", "content": prompt}],
    add_generation_prompt=True, tokenize=False
) for prompt in prompts]
    batches = [chat_prompts[i:i + batch_size] for i in range(0, len(chat_prompts), batch_size)]
    results = []
#批量推理
    lun = 0
    for batch in tqdm(batches, unit="batch"):
       outputs = llm.generate(batch, sampling_params=sampling_params)
       for data, output in zip(batch, outputs):
          raw_responses = output.outputs[0].text
          results.append({'input': data, 'output': raw_responses})
#每过5个batch保存结果
    if lun % 5 == 0:
          with open(args.output_path, "w", encoding="utf-8") as fw:
            fw.write(json.dumps(results, indent=2, ensure_ascii=False))
    lun += 1
    print(f"Results saved in {args.output_path}")

if __name__ == "__main__":
    main()
