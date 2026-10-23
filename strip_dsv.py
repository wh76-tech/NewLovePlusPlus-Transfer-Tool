#!/usr/bin/env python3
"""
strip_dsv.py
剥离 DraStic / DeSmuME 导出的 NDS 存档尾部 122 字节标识，输出标准 .sav 格式。
"""

import sys
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DESMUME_FOOTER_MAGIC = b'|-DESMUME SAVE-|'
FOOTER_SIZE = 122

def convert_dsv_to_sav(input_path='lpp.dsv', output_path='lpp.sav', pad_512k=False):
    if not os.path.isfile(input_path):
        print(f"[-] 输入文件未找到: {input_path}")
        return False

    with open(input_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    print(f"[*] 输入文件: {input_path} (大小: {file_size} 字节 / 0x{file_size:X})")

    if data.endswith(DESMUME_FOOTER_MAGIC):
        print(f"[+] 检测到 DeSmuME / DraStic 尾部签名: {DESMUME_FOOTER_MAGIC.decode('ascii')}")
        raw_data = data[:-FOOTER_SIZE]
        print(f"[+] 剥离尾部 {FOOTER_SIZE} 字节标识，保留前 {len(raw_data)} 字节 (0x{len(raw_data):X})")
    else:
        print("[-] 未在末尾检测到 DeSmuME 标识，直接使用原始数据")
        raw_data = data

    raw_len = len(raw_data)
    # LovePlus+ 官方卡带原装 EEPROM/Flash 大小为 256KB (262,144 字节 = 0x40000)
    if raw_len == 262144:
        print("[*] 存档尺寸为 256KB (262,144 字节 / 0x40000)，与《LovePlus+》官方卡带 SPI 芯片规格完全一致。")
    elif raw_len >= 524288:
        print("[*] 存档尺寸大于等于 512KB，截取前 524,288 字节 (0x80000)。")
        raw_data = raw_data[:524288]

    if pad_512k and len(raw_data) < 524288:
        print(f"[*] 按参数填充至 512KB (0x80000)...")
        raw_data = raw_data.ljust(524288, b'\x00')

    with open(output_path, 'wb') as f:
        f.write(raw_data)

    print(f"[+] 成功输出标准存档: {output_path} (大小: {len(raw_data)} 字节 / 0x{len(raw_data):X})")
    return True

if __name__ == '__main__':
    in_file = sys.argv[1] if len(sys.argv) > 1 else 'lpp.dsv'
    out_file = sys.argv[2] if len(sys.argv) > 2 else 'lpp.sav'
    pad = '--pad512' in sys.argv
    convert_dsv_to_sav(in_file, out_file, pad_512k=pad)
