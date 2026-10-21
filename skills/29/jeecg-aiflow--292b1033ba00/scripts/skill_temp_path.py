"""
跨平台临时目录路径获取脚本
用法:
    python skill_temp_path.py                  # 返回临时目录路径
    python skill_temp_path.py -f config.json   # 返回完整文件路径
"""
import argparse
import os
import tempfile

SKILL_NAME = "jeecg-aiflow"

def get_temp_dir():
    d = os.path.join(tempfile.gettempdir(), SKILL_NAME)
    os.makedirs(d, exist_ok=True)
    return d

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="文件名（拼接在临时目录下）")
    args = parser.parse_args()
    d = get_temp_dir()
    if args.file:
        print(os.path.join(d, args.file))
    else:
        print(d)
