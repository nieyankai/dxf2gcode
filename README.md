# dxf2gcode_lib

A core Python library for converting DXF files (LINE, ARC, LWPOLYLINE) to standardized G-code, with support for configurable feed rate, delay, and coordinate modes.

## Features
- Parse DXF entities (LINE, ARC, Circle，LWPOLYLINE)
- Generate G-code with safe pen-up/pen-down logic
- Configurable parameters (feed rate, delay, units...)

## Installation
python -m build
pip install dist/dxf2gcode-0.1.4-py3-none-any.whl

## Usage
See example/cli.py for a command-line tool example.