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
            prompt = f"**Task Overview**\nCreate a reasonable and high-quality safety condition based on the provided information. Also, output the corresponding specific_column—the columns mentioned in safe_condition and specific_value-the value mentioned in the safe_condition\n\n**Database Schema**\n{schema_str}\n\n**Output Format Requirements**\nsafe_condition:\nspecific_column:[]\nspecific_value:\n\n**Safe condition Requirements**\n1. Find out what sensitive information could be in the Database.\n2. Find out only 1 sensitive information in the whole database.\n3. The security condition to look for can be a column that cannot be accessed\n4. (Very important) Ensure that the final security conditions are reasonable according to the related background of this database.\n5.There is no need for excessive explanations, just keep it simple.\n\n**example**\n{ex_string}\n\nThere are just 2 examples from your colleagues, where you can judge for yourself whether it's right or wrong, and finally give your own answer.\n\n**Answer**\nLet's proceed step by step,and sure the final answer have the format of \"safe_condition:\",\"specific_value:\",and\"specific_column:\"."
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
            prompt = f"**Task Overview**\nCreate a reasonable and high-quality safety condition based on the provided information. Also, output the corresponding specific_column(the columns mentioned in safe_condition).\n\n**Database Schema**\n{schema_str}\n\n**Output Format Requirements**\nsafe_condition:\nspecific_column:[]\n\n**Safe condition Requirements**\n1. Find out what sensitive information could be in the Database.\n2. Find out only 1 sensitive information in the whole database.\n3. The security condition to look for can be a column that cannot be accessed\n4. (Very important) Ensure that the final security conditions are reasonable according to the related background of this database.\n5.There is no need for excessive explanations, just keep it simple.\n\n**example**\n{ex_string}\n\nThere are just 2 examples from your colleagues, where you can judge for yourself whether it's right or wrong, and finally give your own answer.\n\n**Answer**\nLet's proceed step by step,and sure the final answer have the format of \"safe_condition:\",\"specific_value:\",and\"specific_column:\"."
            prompts.append(prompt)
            with open(args.prompts_path, "w", encoding="utf-8") as fw:
                fw.write(json.dumps(prompts, indent=2, ensure_ascii=False))
            print("prompts保存成功")
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
    for batch in tqdm(batches, unit="batch"):
       outputs = llm.generate(batch, sampling_params=sampling_params)
       for data, output in zip(batch, outputs):
          raw_responses = output.outputs[0].text
          results.append({'input': data, 'output': raw_responses})

    with open(args.output_path, "w", encoding="utf-8") as fw:
        fw.write(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Results saved in {args.output_path}")

if __name__ == "__main__":
    main()
