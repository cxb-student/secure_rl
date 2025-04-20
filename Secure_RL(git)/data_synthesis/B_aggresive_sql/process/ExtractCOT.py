# 提取<COT>...</COT>中的内容，并添加到新的键值对中

import json
import re
import os


def extract_cot_content(data):
    """提取数据中<COT>...</COT>标签之间的内容，并添加到新的键值对中"""
    # 正则表达式模式，用于匹配<COT>...</COT>之间的内容
    cot_pattern = re.compile(r'<COT>(.*?)</COT>', re.DOTALL)
    
    # 遍历数据中的每个项目
    for item in data:
        # 检查是否存在'output'键
        if 'output' in item:
            # 在output中查找<COT>...</COT>标签
            match = cot_pattern.search(item['output'])
            if match:
                # 提取匹配的内容并添加到新的键'cot_content'中
                item['cot_content'] = match.group(1).strip()
            else:
                # 如果没有找到匹配项，设置为空字符串
                item['cot_content'] = ""
    
    return data


def main():
    # 设置输入和输出文件路径
    input_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\Infer_column.json"
    output_path = r"C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\Infer_column.json"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：输入文件 {input_path} 不存在")
        return
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取输入文件
    try:
        with open(input_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取输入文件时出错: {e}")
        return
    
    # 记录原始数据项数量
    original_count = len(data)
    print(f"原始数据项数量: {original_count}")
    
    # 提取COT内容
    processed_data = extract_cot_content(data)
    
    # 统计有COT内容的项目数量
    cot_count = sum(1 for item in processed_data if 'cot_content' in item and item['cot_content'])
    print(f"包含COT内容的数据项数量: {cot_count}")
    
    # 保存处理后的结果
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        print(f"处理后的数据已保存至: {output_path}")
    except Exception as e:
        print(f"保存输出文件时出错: {e}")


if __name__ == "__main__":
    main()