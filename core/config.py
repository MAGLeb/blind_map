#!/usr/bin/env python3
"""
Фиксированные параметры карты
"""

# Фиксированная область карты (minx, miny, maxx, maxy) в градусах
# Балканы + Кавказ + Ближний Восток
MAP_BOUNDS = (5, 12, 70, 55)

# Простые фиксированные параметры
FIGURE_SIZE = (30, 22)  # размер фигуры в дюймах (ширина, высота)
DPI = 150              # качество изображения (уменьшили для быстроты)

# Стили карты
COUNTRY_COLOR = 'lightgray'
COUNTRY_EDGE_COLOR = 'black'
COUNTRY_EDGE_WIDTH = 1.5

SEA_COLOR = 'lightblue'
SEA_EDGE_COLOR = 'darkblue'
SEA_EDGE_WIDTH = 1.0
