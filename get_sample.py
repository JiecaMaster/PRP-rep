import pandas as pd
import numpy as np

# 读取排序后的CSV文件
sorted_file = "BENIGN_sorted_output.csv"  # 请将此路径替换为已排序的csv文件路径
data = pd.read_csv(sorted_file)

def stratified_sampling(data, n):
    m = len(data)  # 总行数
    indices = np.linspace(0, m - 1, n + 1, dtype=int)  # 将数据均匀切分为n块的索引范围
    sample_indices = [np.random.randint(indices[i], indices[i+1]) for i in range(n)]  # 每块中随机抽取一行索引
    sampled_data = data.iloc[sample_indices]  # 获取抽样结果
    return sampled_data

# 设置样本数量n
n = 10  # 可根据需要设置样本数量

# 进行分层抽样
sampled_data = stratified_sampling(data, n)

# 输出抽样后的CSV文件
sample_output_file = "BENIGN_sampled_output_1_10.csv"  # 输出文件路径
sampled_data.to_csv(sample_output_file, index=False)

print(f"抽样完成，结果已保存到 {sample_output_file}")
