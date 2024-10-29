import os
import subprocess

file_mapping = {
    "ssh": ["ssh/cam_ssh_bruteforce.py", "ssh/ssh_bruteforce.py"],
    "conn": ["conn/select_ftp.py", "conn/choose_and_map_ftp.py", "conn/ftp_bruteforce.py", "conn/select_http.py", "conn/cam_conn_dos.py", "conn/conn_dos.py", "conn/cam_conn_scan.py", "conn/conn_scan.py"],
    "http": ["http/cam_http_dos.py", "http/http_dos.py", "http/cam_http_bruteforce.py", "http/http_bruteforce.py", "http/cam_http_xss.py", "http/http_xss.py", "http/cam_http_sql.py", "http/http_sql.py", "http/cam_http_botnet.py", "http/http_botnet.py"],
    "notice": ["notice.py"],
}

def run_files(file_names):
    for file_name in file_names:
        if os.path.exists(file_name):
            try:
                # 运行子进程并等待完成
                subprocess.run(["python", file_name], check=True)
            except subprocess.CalledProcessError as e:
                print(f"运行文件 {file_name} 时出错：{e}")
        else:
            print(f"文件 {file_name} 不存在。")

def main():
    try:
        # 提示用户输入数字
        choice = input("本系统需要使用者根据说明提供相应的流量记录，以判断是否存在恶意流量信息及其来源,如果输入的流量信息来源为ssh.log，就输入ssh：")

        # 获取对应的文件列表
        files_to_run = file_mapping.get(choice)

        if files_to_run:
            run_files(files_to_run)
        else:
            print("无效的选择，请输入有效的字符。")
    except ValueError:
        print("请输入有效的字符。")

if __name__ == "__main__":
    main()