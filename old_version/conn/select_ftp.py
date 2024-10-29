def filter_ftp_records(input_filename, output_filename):
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        # 读取前两行并直接写入输出文件
        headers = [next(infile) for _ in range(2)]
        outfile.writelines(headers)
        
        # 遍历文件中剩余的行
        for line in infile:
            # 分割每一行以获取字段
            fields = line.split('\t')
            # 检查service字段是否为'ftp'
            if len(fields) > 7 and fields[7] == 'ftp':
                outfile.write(line)

# 输入文件名和输出文件名
input_filename = 'conn.txt'
output_filename = 'conn_ftp_select.txt'

# 调用函数
filter_ftp_records(input_filename, output_filename)
