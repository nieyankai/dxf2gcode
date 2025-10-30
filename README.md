# dxf2gcode_lib

DXF文件转G代码python库，支持直线、圆弧、多段线和圆，支持进尺速度、停顿时间和坐标模式等参数设置
目前仅支持XY平面绘图，未来会扩展任意平面绘制和3D绘制

## 核心特性
- 解析 DXF 图形实体 (直线，圆弧， 圆，多段线)
- 生成的G代码包含了必要的抬刀落刀安全逻辑
- 可配置参数 (进给速率, 落刀延迟, 坐标模式，单位，进给模式，主刀转速，抬到高度，操作平面，落笔速度，实体过滤)

## 安装方式
- python -m build
- pip install dist/dxf2gcode-{version}-py3-none-any.whl

## 使用方法
- 参考 example文件夹下的示例代码test.py
- 安装完dxf2gcode库之后，把想要转化的.dxf文件放在与test.py同路径
- 执行test.py可以自动把当前目录下所有dxf文件转G代码

