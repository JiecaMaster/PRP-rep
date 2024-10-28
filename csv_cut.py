import pandas as pd

def filter_csv(input_file, output_file):
    # 加载CSV文件
    data = pd.read_csv(input_file)

    # 筛选出Label列值为'Dos Slowloris'的行
    filtered_data = data[data[' Label'] == 'BENIGN']

    # 将筛选后的数据保存到新的CSV文件中
    filtered_data.to_csv(output_file, index=False)

# 调用函数
input_file = 'Wednesday-workingHours.pcap_ISCX.csv'  # 请替换为您的输入文件名
output_file = 'Dos_BENIGN_all.csv'  # 请替换为您希望生成的输出文件名
filter_csv(input_file, output_file)
