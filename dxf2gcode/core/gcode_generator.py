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
            ""
        ]

    def generate_line_block(self, params: Dict, immediate: bool=False) -> List[str]:
        """生成直线G代码块"""
        init = [
            f"G00 Z{self.config.spindle_level}",
            "M05",
            f"G00 X{params['start_x']:.2f} Y{params['start_y']:.2f}",
            f"M03 S{self.config.spindle_speed}",
            f"G01 Z{self.config.working_level} F{self.config.pendown_speed}",
            f"G4 P{self.config.delay}",
        ]
        draw = [
            f"G01 X{params['end_x']:.2f} Y{params['end_y']:.2f} F{self.config.feed_rate}",
            ""
        ]
        if immediate:
            return draw
        else:
            return init + draw



    def generate_arc_block(self, params: Dict, immediate: bool=False) -> List[str]:
        """生成圆弧G代码块（计算I/J偏移）"""
        i = params['center_x'] - params['start_x']
        j = params['center_y'] - params['start_y']
        init = [
            f"G00 Z{self.config.spindle_level}",
            "M05",
            f"G00 X{params['start_x']:.2f} Y{params['start_y']:.2f}",
            f"M03 S{self.config.spindle_speed}",
            f"G01 Z{self.config.working_level} F{self.config.pendown_speed}",
            f"G4 P{self.config.delay}",
        ]
        draw = [
            f"{params['g_code']} X{params['end_x']:.2f} Y{params['end_y']:.2f} I{i:.2f} J{j:.2f} F{self.config.feed_rate}",
            ""
        ]
        if immediate:
            return draw
        else:
            return init + draw


    def generate_finish_code(self) -> List[str]:
        """生成结束G代码段"""
        finish = [
            f"G00 Z{self.config.spindle_level}",
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
        for idx, entity in enumerate(entities):
            entity0 = entities[idx - 1] if idx > 0 else None;
            if entity["type"] == "line":
                if entity0 and entity0["params"]["end_x"] == entity["params"]["start_x"] and entity0["params"]["end_y"] == entity["params"]["start_y"]:
                    full_gcode.extend(self.generate_line_block(entity["params"], immediate=True))
                else:
                    full_gcode.extend(self.generate_line_block(entity["params"]))
            elif entity["type"] == "arc":
                if entity0 and entity0["params"]["end_x"] == entity["params"]["start_x"] and entity0["params"]["end_y"] == entity["params"]["start_y"]:
                    full_gcode.extend(self.generate_arc_block(entity["params"], immediate=True))
                else:
                    full_gcode.extend(self.generate_arc_block(entity["params"]))
        # 拼接结束代码
        full_gcode.extend(self.generate_finish_code())
        return full_gcode