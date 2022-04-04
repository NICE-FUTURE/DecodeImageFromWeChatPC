"""
dat文件和源图片文件就是用某个数按字节异或了一下，异或回来就可以了，
A ^ B = C
B ^ C = A
A ^ C = B
假设png文件头是A，dat文件是C，用A和C文件头的字节异或就可以得出B，因
为图片的格式以png，jpg，gif为主，通过这三种文件格式的头两个字节和待
转换文件的头两个字节一一异或的结果相等就找到B了，同时也知道了文件的
格式
"""


import os
import re
import argparse
import binascii
from typing import Tuple


def get_top_2hex(path:str) -> str:
    """
    获取文件的前两个16进制数
    """
    data = open(path,'rb')
    hexstr = binascii.b2a_hex(data.read(2))
    return str(hexstr[:2], 'utf8'), str(hexstr[2:4], 'utf8')


def parse(dir:str) -> Tuple[int, str]:
    """
    JPG文件头16进制为0xFFD8FF
    PNG文件头16进制为0x89504E
    GIF文件头16进制为0x474946
    """
    firstV, nextV = get_top_2hex(dir)
    firstV = int(firstV, 16)
    nextV = int(nextV, 16)
    coder = firstV ^ 0xFF
    kind = 'jpg'

    if firstV ^ 0xFF == nextV ^ 0xD8:
        coder = firstV ^ 0xFF
        kind = 'jpg'
    elif firstV ^ 0x89 == nextV ^ 0x50:
        coder = firstV ^ 0x89
        kind = 'png'
    elif firstV ^ 0x47 == nextV ^ 0x49:
        coder = firstV ^ 0x47
        kind = 'gif'
    
    return coder, kind


def convert(file_path:str, filename:str, save_dir:str) -> None:
    coder, kind = parse(file_path)

    dat = open(file_path, "rb")
    save_path = os.path.join(save_dir, filename.replace("dat", kind))
    pic = open(save_path, "wb")

    for cur in dat:
        for item in cur:
            pic.write(bytes([item ^ coder]))

    dat.close()
    pic.close()


def main(root_dir):
    dir_pattern = r"^[0-9]+-[0-9]+$"
    dat_pattern = r"^.*\.dat$"
    sub_dirs = [item for item in os.listdir(root_dir) if re.fullmatch(dir_pattern, item) is not None]
    dir_total = len(sub_dirs)
    if dir_total == 0:
        sub_dirs = [""]
    for i, sub_dir in enumerate(sub_dirs):
        cur_dir = os.path.join(root_dir, sub_dir)
        cur_save_dir = os.path.join(root_dir, sub_dir+"-decode")
        os.makedirs(cur_save_dir)
        filenames = [item for item in os.listdir(cur_dir) if re.fullmatch(dat_pattern, item) is not None]
        file_total = len(filenames)
        for j, filename in enumerate(filenames):
            print("{:<2}/{:<2} {:<4}/{:<4} {}".format(i, dir_total, j, file_total, filename), end="\r")
            dat_path = os.path.join(cur_dir, filename)
            convert(dat_path, filename, cur_save_dir)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Decode dat files.")
    parser.add_argument("--root", type=str, help="The root dir. Example: 'C:/Users/Administrator/Documents/WeChat Files/wxid_xxxxxx/FileStorage/Image/'")
    args = parser.parse_args()
    main(args.root)