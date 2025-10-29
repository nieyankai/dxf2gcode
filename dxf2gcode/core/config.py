'''
 Copyright © 2025 Yankai Nie. All rights reserved.
 No part of this work may be reproduced, distributed,
 or transmitted in any form or by any means without prior
 written permission of the copyright owner.
'''
class Config:
    """核心配置类，参数可通过实例修改"""
    def __init__(self):
        # 基础配置
        self.feed_rate = 200  # 绘图进给速度（mm/min）
        self.delay = 0.2       # 落笔延时（秒）
        self.coord_mode = "G90"  # 坐标模式：G90（绝对）/ G91（相对）
        self.unit = "G21"       # 单位：G21（毫米）/ G20（英寸）
        self.speed_mode = "G94" # 进给模式：G94（mm/min）
        self.spindle_speed = 300  # 主轴转速（r/min），用于M03指令的S参数
        # 笔纸距离
        self.paper_level = 0
        self.pendown_speed = 50  #落笔速度
        # 结束配置
        self.home_after_finish = True  # 结束后回原点
        # 过滤配置
        self.valid_entities = ["LINE", "ARC", "LWPOLYLINE", "POINT"]  # 支持的实体类型

# 默认配置实例（外部可直接导入修改）
default_config = Config()