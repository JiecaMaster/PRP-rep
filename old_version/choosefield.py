import csv

# 输入和输出文件路径
input_file_path = 'ftp.txt'
output_file_path = 'ftp_select.txt'

# 要保留的字段名
fields_to_keep = ['ts', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p', 'method', 'host', 'uri', 'referrer', 'status_code', 'status_msg', 'orig_mime_types', 'resp_mime_types']

# 读取输入文件并写入到输出文件
with open(input_file_path, 'r') as infile, open(output_file_path, 'w', newline='') as outfile:
    # 读取第一行，确定字段的索引位置
    header = infile.readline().strip().split('\t')
    indices_to_keep = []
    missing_fields = []

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



