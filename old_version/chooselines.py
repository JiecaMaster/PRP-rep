import datetime


def extract_lines_with_timestamps(input_file, output_file, start_time, end_time):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 提取前两行
    selected_lines = lines[:2]

    # 检查每行的时间戳是否在给定的时间范围内
    for line in lines[2:]:  # 从第三行开始检查
        timestamp_str = line.split('\t')[0]  # 获取时间戳部分
        timestamp = datetime.datetime.fromtimestamp(float(timestamp_str))  # 将时间戳转换为 datetime 对象
        if start_time <= timestamp <= end_time:
            selected_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(selected_lines)


# 使用函数
input_file = 'ftp.txt'  # 输入文件名
output_file = 'ftp_select.txt'  # 输出文件名
start_time = datetime.datetime.fromtimestamp(1499278320.0)  # 开始时间戳
end_time = datetime.datetime.fromtimestamp(1499279520.0)  # 结束时间戳
extract_lines_with_timestamps(input_file, output_file, start_time, end_time)

