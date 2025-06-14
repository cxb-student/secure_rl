source ~/anaconda3/etc/profile.d/conda.sh
conda activate torch_forself
python syn.py \
--Input_sql "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\B_aggresive_sql\EX_output\Final\U_whole.json" \
--schema_dir "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\original_data\omni_2000.json" \
--output_prompt "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\prompts.json" \
--output_mapping "C:\Users\Lenovo\torch\research\NL2SQL\secure_RL\data_synthesis\C_NL_question_syn\map.json" \
--model_path   "" \
--batch_size 16 \
--output_path "" \
--part 0 \

read -p "Press enter to exit"