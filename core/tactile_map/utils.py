"""
Utilities for tactile map generation
"""

import numpy as np
import math
import sys
import os

# Add the core directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MAP_BOUNDS

from .constants import FULL_WIDTH_MM, FULL_HEIGHT_MM, CARD_WIDTH_MM, CARD_HEIGHT_MM, GRID_COLS, GRID_ROWS, BASE_THICKNESS_MM, MAX_ELEVATION_MM, MIN_TACTILE_DIFFERENCE_MM, BOUNDARY_HEIGHT_MM, WAVE_HEIGHT_MM, WAVE_SPACING_MM


def degrees_to_mm(lon_deg, lat_deg, bounds):
    """
    Преобразует координаты из градусов в миллиметры для 3D-печати
    """
    minx, miny, maxx, maxy = bounds
    
    # Нормализуем координаты к диапазону [0, 1]
    lon_norm = (lon_deg - minx) / (maxx - minx)
    lat_norm = (lat_deg - miny) / (maxy - miny)
    
    # Преобразуем в миллиметры
    x_mm = lon_norm * FULL_WIDTH_MM
    y_mm = lat_norm * FULL_HEIGHT_MM
    
    return x_mm, y_mm


def calculate_real_scale():
    """
    Рассчитывает реальный масштаб карты
    """
    minx, miny, maxx, maxy = MAP_BOUNDS
    
    # Центральная широта для расчета
    lat_center = (miny + maxy) / 2
    
    # Размер в км
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat_center))
    km_per_deg_lat = 111.32
    
    real_width_km = (maxx - minx) * km_per_deg_lon
    real_height_km = (maxy - miny) * km_per_deg_lat
    
    # Масштаб
    scale_width = (real_width_km * 1000) / (FULL_WIDTH_MM / 1000)
    scale_height = (real_height_km * 1000) / (FULL_HEIGHT_MM / 1000)
    
    return scale_width, scale_height, real_width_km, real_height_km


def print_map_info():
    """
    Выводит информацию о размерах карты
    """
    scale_w, scale_h, real_w, real_h = calculate_real_scale()
    
    print(f"=== ИНФОРМАЦИЯ О КАРТЕ ===")
    print(f"Размеры полной карты: {FULL_WIDTH_MM}x{FULL_HEIGHT_MM} мм")
    print(f"Размеры одной карточки: {CARD_WIDTH_MM}x{CARD_HEIGHT_MM} мм")
    print(f"Количество карточек: {GRID_COLS}x{GRID_ROWS} = {GRID_COLS*GRID_ROWS}")
    print(f"Реальная территория: {real_w:.0f}x{real_h:.0f} км")
    print(f"Масштаб: 1:{scale_w:.0f} (ширина), 1:{scale_h:.0f} (высота)")
    print(f"Толщина основания: {BASE_THICKNESS_MM} мм")
    print(f"Максимальная высота рельефа: {MAX_ELEVATION_MM} мм")
    print(f"========================")


def print_tactile_recommendations():
    """
    Выводит рекомендации по тактильному восприятию
    """
    print("\n=== ТАКТИЛЬНЫЕ РЕКОМЕНДАЦИИ ===")
    print("Основано на исследованиях тактильного восприятия:")
    print(f"• Минимальная различимая высота: {MIN_TACTILE_DIFFERENCE_MM} мм")
    print(f"• Максимальная высота рельефа: {MAX_ELEVATION_MM} мм")
    print(f"• Высота границ стран: {BOUNDARY_HEIGHT_MM} мм")
    print(f"• Высота волн: {WAVE_HEIGHT_MM} мм")
    print(f"• Расстояние между волнами: {WAVE_SPACING_MM} мм")
    print(f"• Толщина основания: {BASE_THICKNESS_MM} мм")
    print("\nОптимальные параметры для осязания:")
    print("• Количество различимых уровней высот: 6-8")
    print("• Минимальная ширина линий: 2-3 мм")
    print("• Оптимальное расстояние между элементами: 3-5 мм")
    print("• Максимальная комфортная высота: 8-10 мм")
    print("• Угол наклона поверхности: < 45° для стабильности")
    print("===============================")


def bresenham_line(y0, x0, y1, x1):
    """Bresenham's line algorithm for drawing lines on a grid"""
    points = []
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    x, y = x0, y0
    
    x_inc = 1 if x1 > x0 else -1
    y_inc = 1 if y1 > y0 else -1
    
    error = dx - dy
    
    while True:
        points.append((y, x))
        
        if x == x1 and y == y1:
            break
            
        e2 = 2 * error
        
        if e2 > -dy:
            error -= dy
            x += x_inc
            
        if e2 < dx:
            error += dx
            y += y_inc
    
    return points


def calculate_grid_resolution(lon_grid, lat_grid):
    """
    Вычисляет разрешение сетки в миллиметрах на пиксель
    """
    # Размеры сетки в пикселях
    grid_height, grid_width = lon_grid.shape
    
    # Размеры карты в миллиметрах
    map_width_mm = FULL_WIDTH_MM
    map_height_mm = FULL_HEIGHT_MM
    
    # Разрешение в мм/пиксель
    mm_per_pixel_x = map_width_mm / grid_width
    mm_per_pixel_y = map_height_mm / grid_height
    
    # Используем среднее значение для квадратных пикселей
    mm_per_pixel = (mm_per_pixel_x + mm_per_pixel_y) / 2
    
    return mm_per_pixel


def mm_to_pixels(mm_value, mm_per_pixel):
    """
    Преобразует размер в миллиметрах в пиксели
    """
    return max(1, int(round(mm_value / mm_per_pixel)))
