import pandas as pd


def csv_to_formatted_txt(input_csv, output_txt):
    # 使用UTF-8编码读取CSV文件
    data = pd.read_csv(input_csv, encoding='utf-8')

    with open(output_txt, 'w', encoding='utf-8') as f:
        # 遍历每一行数据
        for index, row in data.iterrows():
            # 写入记录编号
            f.write(f"record{index + 1}：")

            # 写入字段名和字段值
            row_content = "，".join([f"{col}：{row[col]}" for col in data.columns])
            f.write(row_content)

            # 换行符
            f.write("\n")

    print(f"转换完成，结果已保存至 {output_txt}")

# 预设输入、输出文件路径
input_csv = "hulk_test_pure_1_20.csv"  # 输入CSV文件路径
output_txt = "hulk_test_pure_1_20.txt"  # 输出TXT文件路径

# 调用函数
csv_to_formatted_txt(input_csv, output_txt)
