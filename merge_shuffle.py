import pandas as pd

def merge_and_shuffle(csv_file1, csv_file2, output_file, shuffle=False):
    # 读取两个CSV文件
    data1 = pd.read_csv(csv_file1)
    data2 = pd.read_csv(csv_file2)

    # 合并两个数据集
    merged_data = pd.concat([data1, data2], ignore_index=True)

    # 如果需要打乱顺序，则进行随机排列
    if shuffle:
        merged_data = merged_data.sample(frac=1).reset_index(drop=True)
        print("数据已打乱顺序。")

    # 输出合并后的CSV文件
    merged_data.to_csv(output_file, index=False)
    print(f"合并完成，结果已保存至 {output_file}")

# 预设输入、输出文件路径及是否打乱顺序
csv_file1 = "BENIGN_test_output_1_10.csv"        # 第一个CSV文件路径
csv_file2 = "hulk_test_output_1_10.csv"        # 第二个CSV文件路径
output_file = "hulk_test_merge_1_20.csv"  # 输出文件路径
shuffle = True  # 设置为True表示打乱顺序，False则保持原顺序

# 调用函数
merge_and_shuffle(csv_file1, csv_file2, output_file, shuffle)
