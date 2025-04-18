source ~/anaconda3/etc/profile.d/conda.sh
conda activate torch_forself
python syn_infer.py \
--condition_path "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\A_safe_condition\omni_cells_filtered.json" \
--prompts_path "./prompts.json" \
--model_path "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" \
--db_dataset "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\omni_2000.json" \
--ex_path "./ex.json" \
--batch_size 16 \
--prompts_per_type 1 \
--output_path "./output_whole_column.json"\



read -p "Press enter to exit"
