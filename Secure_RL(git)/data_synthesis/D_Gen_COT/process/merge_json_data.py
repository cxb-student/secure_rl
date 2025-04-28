import json
import os


def main():
    # 定义文件路径
    main_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\process\01.json'
    uwhole_path = r'C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\syn\U_1.json'
    count = 0

    # 加载主文件数据
    with open(main_path, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    print(len(main_data))

    # 加载U_WHOLE数据并建立映射
    with open(uwhole_path, 'r', encoding='utf-8') as f:
        uwhole_data = json.load(f)
    uput = []

    # 处理每个主文件条目
    for item in main_data:
        id = item['item_id']
        match_items = []
        for item1 in uwhole_data:
            if item1['id'] == id:
                match_items.append(item1)
            else:
                continue
        for match_item in match_items:
            if item['sql_list'] == match_item['sql_list']:
                # 修正字段命名并添加异常处理
                try:
                    item.update({
                        'id': match_item['id'],
                        'db_id': match_item['db_id'],  # 修正字段名
                        'safe_condition': match_item['safe_condition'],
                        'specific_column': match_item['specific_column'],
                        'specific_value': match_item['specific_value'],
                        'cot_content': match_item['cot_content'],
                        'safe_label': match_item['safe_label'],
                        'questions': match_item['questions'],
                    })
                    uput.append(item)
                    count += 1
                    break

                except KeyError as e:
                    print(f"字段处理错误: {e}")
            else:
                continue

    # 添加文件存在性检查
    if not os.path.exists(main_path) or not os.path.exists(uwhole_path):
        print("错误：输入文件路径不存在")
        return
    print(f"共修正了{count}条数据")

    # 使用安全写入模式
    output_path = r'c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\process\merged_final.json'
    with open(
            r'c:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\D_Gen_COT\process\11.json',
            'w', encoding='utf-8') as f:
        json.dump(uput, f, indent=2, ensure_ascii=False)
    print(len(uput))


if __name__ == '__main__':
    main()
    # 添加最终结果验证
