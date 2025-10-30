'''
 Copyright © 2025 Yankai Nie. All rights reserved.
 No part of this work may be reproduced, distributed,
 or transmitted in any form or by any means without prior
 written permission of the copyright owner.
'''
import ezdxf
from ezdxf.entities import Point, Circle
import math
from typing import List, Dict, Union
from .config import Config

class DXFParser:
    def __init__(self, config: Config = None):
        self.config = config or Config()  # 接收外部配置，默认用默认配置

    def parse_point(self, entity: ezdxf.entities.Point) -> List[Dict]:
        x = point.dxf.location.x
        y = point.dxf.location.y
        return {
            "type": "point",
            "params": {
                "x": x,
                "y": y
            }
        }

    def parse_circle(self, entity: ezdxf.entities.Circle) -> List[Dict]:
        center = entity.dxf.center  # 圆心坐标 (x, y)
        radius = entity.dxf.radius  # 半径
        cx, cy = center.x, center.y

        segments = []
        start_x = cx + radius
        start_y = cy
        end_x = cx - radius
        end_y = cy

        segments.extend([
            {
                "type": "arc",
                "params": {
                    "start_x": start_x, "start_y": start_y,
                    "end_x": end_x, "end_y": end_y,
                    "center_x": cx, "center_y": cy, "g_code": "G02"
                }
            },
            {
                "type": "arc",
                "params": {
                    "start_x": end_x, "start_y": end_y,
                    "end_x": start_x, "end_y": start_y,
                    "center_x": cx, "center_y": cy, "g_code": "G02"
                }
            },
        ])

        return segments



    def parse_line(self, entity: ezdxf.entities.Line) -> Dict:
        """解析直线实体，返回标准化参数"""
        start = entity.dxf.start
        end = entity.dxf.end
        return {
            "type": "line",
            "params": {
                "start_x": start.x,
                "start_y": start.y,
                "end_x": end.x,
                "end_y": end.y
            }
        }

    def parse_arc(self, entity: ezdxf.entities.Arc) -> Dict:
        """解析圆弧实体，返回标准化参数（含G02/G03判断）"""
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = math.radians(entity.dxf.start_angle)
        end_angle = math.radians(entity.dxf.end_angle)

        # 计算起点/终点坐标
        start_x = center.x + radius * math.cos(start_angle)
        start_y = center.y + radius * math.sin(start_angle)
        end_x = center.x + radius * math.cos(end_angle)
        end_y = center.y + radius * math.sin(end_angle)

        # 叉积判断旋转方向（G02/G03）
        vec1_x = center.x - start_x
        vec1_y = center.y - start_y
        vec2_x = center.x - end_x
        vec2_y = center.y - end_y
        cross_product = vec1_x * vec2_y - vec1_y * vec2_x
        g_code = "G03" if cross_product > 0 else "G02"

        return {
            "type": "arc",
            "params": {
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "center_x": center.x,
                "center_y": center.y,
                "g_code": g_code
            }
        }

    def calculate_arc_center(self, P1, P2, bulge):
        x1, y1 = P1
        x2, y2 = P2

        # 计算弦向量的分量（V = P2 - P1）
        dx = x2 - x1  # 向量V的x分量
        dy = y2 - y1  # 向量V的y分量

        # 计算弦长（|V|）
        chord_length = math.hypot(dx, dy)
        if chord_length < 1e-9:
            raise ValueError("起点与终点重合，无法计算圆心")

        # 处理直线段（bulge=0无圆心）
        if abs(bulge) < 1e-9:
            raise ValueError("bulge=0为直线段，无圆心")

        # 计算弦中点M的坐标（M = P1 + V/2）
        mx = x1 + dx / 2  # 中点x
        my = y1 + dy / 2  # 中点y

        # 计算垂直于V的向量分量（逆时针方向：(-dy, dx)）
        perp_dx = -dy  # 垂直向量的x分量
        perp_dy = dx  # 垂直向量的y分量

        # 单位化垂直向量（除以弦长）
        u_perp_dx = perp_dx / chord_length  # 单位垂直向量x
        u_perp_dy = perp_dy / chord_length  # 单位垂直向量y

        # 确定方向
        sign_b = 1 if bulge > 0 else -1
        dir_dx = u_perp_dx * sign_b  # 最终方向向量x
        dir_dy = u_perp_dy * sign_b  # 最终方向向量y

        # 计算圆心到弦的距离h
        h = chord_length * (1 - bulge ** 2) / (4 * bulge)

        # 计算从M到圆心的偏移量（方向向量×h）
        offset_dx = dir_dx * h
        offset_dy = dir_dy * h

        # 圆心坐标 = 中点M + 偏移量
        cx = mx + offset_dx
        cy = my + offset_dy

        return (cx, cy)

    def parse_lwpolyline(self, entity: ezdxf.entities.LWPolyline) -> List[Dict]:
        """解析多段线，拆解为直线/圆弧，返回标准化参数列表"""
        segments = []
        vertices = entity
        if len(vertices) < 2:
            return segments

        for i in range(len(vertices) - 1):
            start_x, start_y, start_width, end_width, bulge = vertices[i]
            end_x, end_y, start_width1, end_width1, bulge1 = vertices[i + 1]

            # 圆弧段（凸度≠0）
            if bulge != 0:
                cx, cy = self.calculate_arc_center((start_x, start_y), (end_x, end_y), bulge)
                g_code = "G03" if bulge > 0 else "G02"

                segments.append({
                    "type": "arc",
                    "params": {
                        "start_x": start_x, "start_y": start_y,
                        "end_x": end_x, "end_y": end_y,
                        "center_x": cx, "center_y": cy, "g_code": g_code
                    }
                })
            # 直线段
            else:
                segments.append({
                    "type": "line",
                    "params": {
                        "start_x": start_x, "start_y": start_y,
                        "end_x": end_x, "end_y": end_y
                    }
                })
        if entity.is_closed:
            start_x, start_y, start_width, end_width, bulge = vertices[-1]
            end_x, end_y, start_width1, end_width1, bulge1 = vertices[0]
            segments.append({
                "type": "line",
                "params": {
                    "start_x": start_x, "start_y": start_y,
                    "end_x": end_x, "end_y": end_y
                }
            })

        return segments




    def parse_dxf(self, dxf_path: str) -> List[Dict]:
        """主解析函数：读取DXF，返回所有实体的标准化参数列表"""
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
        except Exception as e:
            raise ValueError(f"DXF读取失败：{str(e)}")

        entities = []
        # 只解析配置中允许的实体类型
        query_str = " ".join(self.config.valid_entities)
        for entity in msp.query(query_str):
            if isinstance(entity, ezdxf.entities.Line):
                entities.append(self.parse_line(entity))
            elif isinstance(entity, ezdxf.entities.Arc):
                entities.append(self.parse_arc(entity))
            elif isinstance(entity, ezdxf.entities.LWPolyline):
                entities.extend(self.parse_lwpolyline(entity))
            elif isinstance(entity, ezdxf.entities.Circle):
                entities.extend(self.parse_circle(entity))
        return entities