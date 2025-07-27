"""
Water area processing for tactile maps
"""

import numpy as np
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from core.constants import WAVE_HEIGHT_MM, WAVE_INTERVAL_MM, WAVE_WIDTH_MM, WAVE_SEGMENT_LENGTH_MM


def create_tactile_wave_lines(water_mask, lon_grid, lat_grid):
    """
    Создает множество мелких синусоидальных волн в водных областях
    
    Возвращает список коротких волновых сегментов:
    - Форма: Короткие синусоидальные сегменты
    - Высота: 1.2мм (снижено на 20%)
    - Ширина: 2.5мм (увеличено на 2мм для лучшего тактильного восприятия)
    - Интервал: 15мм между рядами волн (больше волн)
    - Длина сегмента: 10мм каждый (максимум 1см)
    - Только в водных областях (строгая проверка)
    """
    print("Creating multiple small sinusoidal wave segments...")
    
    # Получаем координатные границы карты
    lon_min, lon_max = lon_grid.min(), lon_grid.max()
    lat_min, lat_max = lat_grid.min(), lat_grid.max()
    
    # Размеры карты в градусах
    map_width_deg = lon_max - lon_min
    map_height_deg = lat_max - lat_min
    
    print(f"Map bounds: {lon_min:.3f} to {lon_max:.3f} lon, {lat_min:.3f} to {lat_max:.3f} lat")
    print(f"Map size: {map_width_deg:.3f} x {map_height_deg:.3f} degrees")
    
    # Параметры волн в мм
    wave_height = WAVE_HEIGHT_MM  # 1.2мм (снижено на 20%)
    wave_interval_mm = WAVE_INTERVAL_MM  # 15мм (больше волн)
    wave_width_mm = WAVE_WIDTH_MM  # 2.5мм (толще на 2мм)
    segment_length_mm = WAVE_SEGMENT_LENGTH_MM  # 10мм (максимум 1см)
    
    # Конвертируем размеры из мм в градусы
    map_width_mm = 400.0  # примерная ширина карты в мм
    mm_to_deg_ratio = map_width_deg / map_width_mm
    wave_interval_deg = wave_interval_mm * mm_to_deg_ratio
    segment_length_deg = segment_length_mm * mm_to_deg_ratio
    
    print(f"Wave interval: {wave_interval_mm}mm = {wave_interval_deg:.6f} degrees")
    print(f"Segment length: {segment_length_mm}mm = {segment_length_deg:.6f} degrees")
    
    # Список всех волновых сегментов
    wave_lines = []
    
    # Создаем ряды волн
    current_lat = lat_min + wave_interval_deg
    total_segments = 0
    
    while current_lat < lat_max - wave_interval_deg:
        # Создаем сегменты волн в текущем ряду
        current_lon = lon_min
        
        while current_lon < lon_max - segment_length_deg:
            # Проверяем, есть ли вода в области этого сегмента
            segment_has_water = False
            
            # Проверяем несколько точек в области сегмента
            test_points = 5
            for i in range(test_points):
                test_lon = current_lon + (i / (test_points - 1)) * segment_length_deg
                test_lat = current_lat
                
                # Находим индексы в сетке
                lat_idx = np.searchsorted(lat_grid[:, 0], test_lat)
                lon_idx = np.searchsorted(lon_grid[0, :], test_lon)
                
                # Проверяем границы и воду
                if (0 <= lat_idx < water_mask.shape[0] and 
                    0 <= lon_idx < water_mask.shape[1]):
                    if water_mask[lat_idx, lon_idx]:
                        segment_has_water = True
                        break
            
            # Создаем сегмент только если в области есть вода
            if segment_has_water:
                # Создаем точки для синусоидального сегмента
                num_points = 15  # количество точек на сегмент
                lon_points = np.linspace(current_lon, current_lon + segment_length_deg, num_points)
                
                # Синусоидальное смещение
                amplitude_deg = wave_interval_deg * 0.05  # Уменьшена амплитуда в 3 раза (0.15 / 3 = 0.05)
                frequency = 2.0  # 2 полных цикла на сегмент
                
                lat_points = current_lat + amplitude_deg * np.sin(
                    frequency * 2 * np.pi * (lon_points - current_lon) / segment_length_deg
                )
                
                # Создаем точки сегмента, проверяя каждую на принадлежность воде
                line_points = []
                for lon, lat in zip(lon_points, lat_points):
                    # Точная проверка воды для каждой точки
                    lat_idx = np.searchsorted(lat_grid[:, 0], lat)
                    lon_idx = np.searchsorted(lon_grid[0, :], lon)
                    
                    if (0 <= lat_idx < water_mask.shape[0] and 
                        0 <= lon_idx < water_mask.shape[1] and 
                        water_mask[lat_idx, lon_idx]):
                        line_points.append([lon, lat, wave_height])
                
                # Добавляем сегмент если в нем достаточно точек
                if len(line_points) > 3:  # минимум 4 точки для создания волны
                    wave_lines.append({
                        'points': np.array(line_points),
                        'height': wave_height,
                        'width': wave_width_mm
                    })
                    total_segments += 1
            
            # Переходим к следующему сегменту с небольшим промежутком
            current_lon += segment_length_deg * 1.5  # 50% перекрытие между возможными позициями
        
        current_lat += wave_interval_deg
    
    print(f"Created {total_segments} small wave segments")
    print(f"Wave parameters: height={wave_height}mm, width={wave_width_mm}mm, segment_length={segment_length_mm}mm")
    print(f"Waves are strictly limited to water areas only")
    
    return wave_lines


def create_tactile_wave_pattern(water_mask, lon_grid, lat_grid):
    """
    Обратная совместимость - возвращает пустой паттерн
    Волны теперь создаются как отдельная геометрия через create_tactile_wave_lines
    """
    print("Wave pattern will be created as separate geometry (not elevation modification)")
    return np.zeros_like(water_mask, dtype=float)


def create_wave_pattern(water_mask, lon_grid, lat_grid, wave_height=1.0):
    """Create tactile wave pattern for water areas - DEPRECATED, use create_tactile_wave_pattern instead"""
    print("Warning: Using deprecated create_wave_pattern function")
    return create_tactile_wave_pattern(water_mask, lon_grid, lat_grid)
