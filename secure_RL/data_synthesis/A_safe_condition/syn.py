# 生成安全条件
import json
import re
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def model_fn(model_path, input):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = tokenizer(input, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=2048,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

def extract_fn(input, label):
    if label == "```sql":
        pattern = rf"{label}：([^```]+)"
    else:
        pattern = rf"{label}：([^\n]+)"
    match = re.search(pattern, input)
    if match:
        return f"{label}：{match.group(1)}"
    else:
        return f"{label}：No safety condition found."
def weighted_random_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

model_path = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
db_dataset = "C:\\Users\\Lenovo\\torch\\research\\NL2SQL\\secure_RL\\data_synthesis\\original_data\\spider_dev_db.json"
db_dataset = json.load(open(db_dataset,"r"))
ex_data = [
  "table concert , columns = [ concert.concert_name ( text) , concert.theme ( text | values : Free choice , Free choice 2 ) , concert.concert_id ( int | primary key ) , concert.year ( text) , concert.stadium_id ( text ) ]\ntable singer_in_concert , columns = [ singer_in_concert.concert_id ( int  ) , singer_in_concert.singer_id ( text | primary key  ) ]\ntable singer , columns = [ singer.name ( text) , singer.singer_id ( int  ) , singer.age ( int ) , singer.country ( text  ) , singer.is_male ( bool) , singer.song_name ( text  ) , singer.song_release_year ( text ) ]\ntable stadium , columns = [ stadium.name ( text) , stadium.highest ( int  ) , stadium.capacity ( int) , stadium.location ( text) , stadium.lowest ( int  ) , stadium.average ( int) , stadium.stadium_id ( int | primary key) ]\nforeign keys :\nconcert.stadium_id = stadium.stadium_id\nsinger_in_concert.singer_id = singer.singer_id\nsinger_in_concert.concert_id = concert.concert_id\nmatched contents : None\n\nFor example, now that you have the above database, you can propose a corresponding security condition. \nYou can output：\"safe_condition:Age of the singer is sensitive information.\"\nIt is just an example from your colleagues, where you can judge for yourself whether it's right or wrong, and finally give your own answer.",
  "table concert , columns = [ concert.concert_name ( text) , concert.theme ( text | values : Free choice , Free choice 2 ) , concert.concert_id ( int | primary key ) , concert.year ( text) , concert.stadium_id ( text ) ]\ntable singer_in_concert , columns = [ singer_in_concert.concert_id ( int  ) , singer_in_concert.singer_id ( text | primary key  ) ]\ntable singer , columns = [ singer.name ( text) , singer.singer_id ( int  ) , singer.age ( int ) , singer.country ( text  ) , singer.is_male ( bool) , singer.song_name ( text  ) , singer.song_release_year ( text ) ]\ntable stadium , columns = [ stadium.name ( text) , stadium.highest ( int  ) , stadium.capacity ( int) , stadium.location ( text) , stadium.lowest ( int  ) , stadium.average ( int) , stadium.stadium_id ( int | primary key) ]\nforeign keys :\nconcert.stadium_id = stadium.stadium_id\nsinger_in_concert.singer_id = singer.singer_id\nsinger_in_concert.concert_id = concert.concert_id\nmatched contents : None\n\nFor example, now that you have the above database, you can propose a corresponding security condition. \nYou can output：\"safe_condition:Age of singers younger than 18 is sensitive information\"\nIt is just an example from your colleagues, where you can judge for yourself whether it's right or wrong, and finally give your own answer."
]
label_safe = "safe_condition"

for i in range(len(db_dataset)):
    print(f"第{i+1}个")
    # 使用随机选择函数，70%概率选择ex_data[0]，30%概率选择ex_data[1]
    ex = weighted_random_choice(ex_data, weights=[0.7, 0.3])
    schema_str = db_dataset[i]
    prompt_safe =f"""**Task Overview**
Create an reasonable and high-quality safety conditions based on the provided information.

**Database Schema**
{schema_str}

**Output Format Requirements**
safe_condition：

**Safe condition Requirements**
1. Find out what sensitive information could be in the Database.
2. Find out only 1 sensitive information in the whole database.
3. The security condition to look for can be a column that cannot be accessed, or certain rows in certain columns.
4. (Very important) Ensure that the final security conditions are reasonable according to the related background of this database.

**example**
{ex}
**Answer**
Let's proceed step by step."""
    print(prompt_safe)
    output = model_fn(model_path,prompt_safe)
    safe_condition = extract_fn(output,label_safe)
    db_dataset[i] = db_dataset[i] + safe_condition

    print(safe_condition)
with open('spider_dev_db_with_safe.json', 'w', encoding='utf-8') as f:
    json.dump(list(db_dataset), f, ensure_ascii=False, indent=2)
