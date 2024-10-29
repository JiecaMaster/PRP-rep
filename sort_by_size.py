import pandas as pd

# 读取CSV文件
input_file = "Dos_hulk_all.csv"  # 请将此路径替换为你的csv文件路径
data = pd.read_csv(input_file)

# 按照Average Packet Size字段进行降序排序
sorted_data = data.sort_values(by=" Average Packet Size", ascending=False)

# 输出排序后的CSV文件
output_file = "hulk_sorted_output.csv"  # 输出文件的路径
sorted_data.to_csv(output_file, index=False)

print(f"排序完成，结果已保存到 {output_file}")
