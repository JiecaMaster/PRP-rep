import pandas as pd


def remove_columns(input_file, output_file, columns_to_remove):
    # 读取CSV文件
    data = pd.read_csv(input_file)

    # 检查并删除指定字段
    existing_columns = [col for col in columns_to_remove if col in data.columns]
    if existing_columns:
        data = data.drop(columns=existing_columns)
        print(f"以下字段已删除：{', '.join(existing_columns)}")
    else:
        print("未找到指定的字段。")

    # 输出新的CSV文件
    data.to_csv(output_file, index=False)
    print(f"处理完成，新文件已保存至 {output_file}")


# 预设输入、输出文件路径和要删除的字段
input_file = "BENIGN_sampled_output_1_10.csv"  # 输入文件路径
output_file = "BENIGN_pure_sample_1_10.csv"  # 输出文件路径
columns_to_remove = [#" Label",
    "Flow ID"," Source IP"," Source Port"," Destination IP"," Destination Port"," Timestamp"]  # 要删除的字段列表

remove_columns(input_file, output_file, columns_to_remove)
