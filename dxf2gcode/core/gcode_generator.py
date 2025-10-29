'''
 Copyright © 2025 Yankai Nie. All rights reserved.
 No part of this work may be reproduced, distributed,
 or transmitted in any form or by any means without prior
 written permission of the copyright owner.
'''
from typing import List, Dict
from .config import Config

class GCodeGenerator:
    def __init__(self, config: Config = None):
        self.config = config or Config()

    def generate_init_code(self) -> List[str]:
        """生成初始化G代码段"""
        return [
            f"{self.config.coord_mode} {self.config.unit} {self.config.speed_mode}",
            "M05",
            "G28 X0 Y0",
            ""
        ]

    def generate_line_block(self, params: Dict) -> List[str]:
        """生成直线G代码块"""
        return [
            "M05",
            f"G00 X{params['start_x']} Y{params['start_y']}",
            f"M03 S{self.config.spindle_speed}",
            f"G01 Z{self.config.paper_level} {self.config.pendown_speed}",
            f"G4 P{self.config.delay}",
            f"G01 X{params['end_x']} Y{params['end_y']} F{self.config.feed_rate}",
            f"G00 Z0",
            "M05",
            ""
        ]

    def generate_arc_block(self, params: Dict) -> List[str]:
        """生成圆弧G代码块（计算I/J偏移）"""
        i = params['center_x'] - params['start_x']
        j = params['center_y'] - params['start_y']
        return [
            "M05",
            f"G00 X{params['start_x']} Y{params['start_y']}",
            f"M03 S{self.config.spindle_speed}",
            f"G01 Z{self.config.paper_level} {self.config.pendown_speed}",
            f"G4 P{self.config.delay}",
            f"{params['g_code']} X{params['end_x']} Y{params['end_y']} I{i:.2f} J{j:.2f} F{self.config.feed_rate}",
            f"G00 Z0",
            "M05",
            ""
        ]

    def generate_finish_code(self) -> List[str]:
        """生成结束G代码段"""
        finish = [
            "M05",
        ]
        if self.config.home_after_finish:
            finish.append("G00 X0 Y0")
        finish.append("M30")
        return finish

    def generate_gcode(self, entities: List[Dict]) -> List[str]:
        """主生成函数：接收实体参数，返回完整G代码列表"""
        if not entities:
            raise ValueError("无有效绘图实体，无法生成G代码")

        full_gcode = []
        # 拼接初始化代码
        full_gcode.extend(self.generate_init_code())
        # 拼接每个实体的代码块
        for idx, entity in enumerate(entities, 1):
            if entity["type"] == "line":
                full_gcode.extend(self.generate_line_block(entity["params"]))
            elif entity["type"] == "arc":
                full_gcode.extend(self.generate_arc_block(entity["params"]))
        # 拼接结束代码
        full_gcode.extend(self.generate_finish_code())
        return full_gcode