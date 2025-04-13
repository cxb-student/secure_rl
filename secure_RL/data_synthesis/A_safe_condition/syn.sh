source ~/anaconda3/etc/profile.d/conda.sh
conda activate torch_forself

#这个是整列的
#prompts_path 是存贮的位置
python syn.py \
--prompts_path "./prompts.json" \
--model_path "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" \
--db_dataset "../original_data/all_with_column.json" \
--ex_path "./ex.json" \
--range_type "whole_column" \
--batch_size 16 \
--output_path "./output_whole_column.json"


#这个是cells的
python syn.py \
  --model_path "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" \
  --db_dataset "../original_data/all_with_column.json" \
  --ex_path "./ex.json" \
  --prompts_path"./prompts.json" \
  --range_type "cells" \
  --batch_size 16 \
  --output_path "./output_cells.json"