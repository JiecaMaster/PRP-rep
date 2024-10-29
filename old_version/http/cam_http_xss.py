import csv
import os

def choose_fields_and_filter(input_file_path, output_file_path):
    # 要保留的字段名
    fields_to_keep = [ 'id.orig_h', 'id.resp_h','uri','referrer']

    # 读取输入文件并写入到输出文件
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w', newline='') as outfile:
        # 读取第一行，确定字段的索引位置
        header = infile.readline().strip().split('\t')
        indices_to_keep = []
        missing_fields = []
        #忽略第2行
        infile.readline()

        # 确定需要保留的字段索引
        for field in fields_to_keep:
            if field in header:
                indices_to_keep.append(header.index(field))
            else:
                missing_fields.append(field)

        # 如果有缺失的字段，打印出来并继续处理其它字段
        if missing_fields:
            print(f"以下字段在文件中未找到，将被忽略：{missing_fields}")

        # 创建csv writer对象，指定字段名
        writer = csv.DictWriter(outfile, fieldnames=[fields_to_keep[i] for i in range(len(fields_to_keep)) if fields_to_keep[i] not in missing_fields], delimiter='\t')
        writer.writeheader()
        
        # 处理数据行
        for line in infile:
            data = line.strip().split('\t')
            # 检查数据行是否有足够的字段
            if len(data) >= len(header):
                # 根据索引提取需要的字段
                filtered_data = {fields_to_keep[i]: data[indices_to_keep[i]] for i in range(len(indices_to_keep))}
                writer.writerow(filtered_data)
            else:
                print(f"警告: 数据行字段不足，已忽略此行：{line}")

    print(f"处理完成，输出文件保存在：{output_file_path}")

def process_log_file(input_filename, output_filename):
    # 以UTF-8编码打开输入文件并读取所有行
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 处理每一行
    processed_lines = []
    headers = lines[0].strip().split('\t')  # 获取字段名列表
    for line_number, line in enumerate(lines[1:], start=1):  # 从第二行开始处理，行数从1开始
        # 去掉换行符，并按照制表符分割行
        fields = line.strip().split('\t')
        # 将每个字段名和值用冒号连接，并用中括号包围，字段之间用逗号分隔，并在末尾添加分号
        processed_fields = []
        for header, field in zip(headers, fields):
            processed_fields.append(f'{header}: {field}')
        processed_line = f'record{line_number}: [' + ', '.join(processed_fields) + '];'
        processed_lines.append(processed_line)

    # 以UTF-8编码打开输出文件，并将处理后的每一行写入
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for processed_line in processed_lines:
            output_file.write(processed_line + '\n')

def main():
    # 设置输入和输出文件的路径
    input_file_path = 'http.txt'
    intermediate_file_path = 'http_xss_mid.txt'
    output_file_path = 'http_xss.txt'

    # 执行功能
    choose_fields_and_filter(input_file_path, intermediate_file_path)
    # 检查中间文件是否生成
    if os.path.exists(intermediate_file_path) and os.path.getsize(intermediate_file_path) > 0:
        # 执行日志文件处理功能
        process_log_file(intermediate_file_path, output_file_path)
        print(f"最终处理完成，输出文件保存在：{output_file_path}")
    else:
        print(f"中间文件 {intermediate_file_path} 生成失败或为空，无法继续处理。")

if __name__ == "__main__":
    main()

