'''
 Copyright © 2025 Yankai Nie. All rights reserved.
 No part of this work may be reproduced, distributed,
 or transmitted in any form or by any means without prior
 written permission of the copyright owner.
'''
import os
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)
from dxf2gcode.core import Config, DXFParser, GCodeGenerator

def batch_convert_dxf_to_gcode():
    """批量转换当前目录下的所有DXF文件为GCode"""
    # 配置参数（使用默认配置，可根据需要修改）
    config = Config()
    config.feed_rate = 200  # 进给速度
    config.delay = 0.2      # 落笔延时
    config.home_after_finish = True  # 结束后回原点

    # 获取当前目录下所有.dxf文件
    current_dir = os.getcwd()  # 当前工作目录
    dxf_files = [
        f for f in os.listdir(current_dir)
        if f.lower().endswith(".dxf") and os.path.isfile(f)
    ]

    if not dxf_files:
        print("⚠️ 当前目录下未找到任何DXF文件！")
        return

    # 初始化解析器和生成器
    parser = DXFParser(config)
    generator = GCodeGenerator(config)

    # 批量转换
    print(f"📌 发现 {len(dxf_files)} 个DXF文件，开始转换...")
    for dxf_file in dxf_files:
        try:
            # 生成输出文件名（同目录、同名，后缀改为.gcode）
            gcode_file = os.path.splitext(dxf_file)[0] + ".gcode"

            # 解析DXF
            print(f"\n处理文件：{dxf_file}")
            entities = parser.parse_dxf(dxf_file)
            if not entities:
                print(f"  ⚠️ 无有效实体，跳过该文件")
                continue

            # 生成GCode
            gcode_lines = generator.generate_gcode(entities)

            # 保存GCode
            with open(gcode_file, "w", encoding="utf-8") as f:
                f.write("\n".join(gcode_lines))
            print(f"  ✅ 已生成：{gcode_file}")

        except Exception as e:
            print(f"  ❌ 转换失败：{str(e)}")

    print("\n🎉 批量转换完成！")

if __name__ == "__main__":
    batch_convert_dxf_to_gcode()