"""
Water area processing for tactile maps
"""

import numpy as np


def create_tactile_wave_pattern(water_mask, lon_grid, lat_grid):
    """
    Создает тактильный паттерн волн для водных областей
    
    Новый паттерн:
    - Множество маленьких прямоугольных волн длиной 1 см
    - Высота волн: 2.0 мм (хорошо различимая)
    - Ширина изгибается синусоидально
    - Плотное покрытие водных областей
    """
    print("Creating tactile wave pattern...")
    print(f"Grid shapes - lon: {lon_grid.shape}, lat: {lat_grid.shape}")
    print(f"Lon range: {lon_grid.min():.3f} to {lon_grid.max():.3f}")
    print(f"Lat range: {lat_grid.min():.3f} to {lat_grid.max():.3f}")
    
    # Поскольку координаты в градусах, нужно нормализовать к индексам сетки
    rows, cols = lon_grid.shape
    
    # Создаем координаты в "пикселях" - от 0 до размера сетки
    x_indices = np.arange(cols)
    y_indices = np.arange(rows)
    x_grid, y_grid = np.meshgrid(x_indices, y_indices)
    
    # Параметры волн
    wave_length_pixels = 10  # длина каждой волны = 1 см в пикселях
    wave_height = 2.0  # мм - высота волн
    wave_spacing = 15  # расстояние между рядами волн
    
    # Параметры синусоидального изгиба
    bend_frequency = 0.2  # частота изгиба (как часто изгибается)
    bend_amplitude = 5.0  # амплитуда изгиба в пикселях
    
    # Инициализируем паттерн волн
    wave_pattern = np.zeros_like(x_grid, dtype=float)
    
    # Создаем ряды волн
    for row_offset in range(0, rows, wave_spacing):
        # Для каждого ряда создаем синусоидальный изгиб
        for y in range(max(0, row_offset - 2), min(rows, row_offset + 3)):
            # Синусоидальное смещение по x для создания изгиба
            x_offset = bend_amplitude * np.sin(bend_frequency * y)
            
            # Создаем прямоугольные волны вдоль этой линии
            for x_start in range(0, cols, wave_length_pixels * 2):
                # Центр волны с учетом изгиба
                wave_center_x = x_start + x_offset
                
                # Прямоугольная волна: от wave_center_x до wave_center_x + wave_length_pixels
                x_start_int = int(max(0, wave_center_x))
                x_end_int = int(min(cols, wave_center_x + wave_length_pixels))
                
                if x_start_int < x_end_int and 0 <= y < rows:
                    # Создаем прямоугольную волну
                    wave_pattern[y, x_start_int:x_end_int] = wave_height
    
    # Создаем дополнительные ряды волн со смещением для плотности
    for row_offset in range(wave_spacing//2, rows, wave_spacing):
        for y in range(max(0, row_offset - 1), min(rows, row_offset + 2)):
            # Синусоидальное смещение с другой фазой
            x_offset = bend_amplitude * np.sin(bend_frequency * y + np.pi/3)
            
            for x_start in range(wave_length_pixels, cols, wave_length_pixels * 2):
                wave_center_x = x_start + x_offset
                
                x_start_int = int(max(0, wave_center_x))
                x_end_int = int(min(cols, wave_center_x + wave_length_pixels))
                
                if x_start_int < x_end_int and 0 <= y < rows:
                    # Немного меньшая высота для вариативности
                    wave_pattern[y, x_start_int:x_end_int] = wave_height * 0.8
    
    # Применяем только к водным областям
    wave_pattern = wave_pattern * water_mask
    
    print(f"Wave pattern: length={wave_length_pixels}px, height={wave_height}mm, spacing={wave_spacing}px")
    print(f"Wave pattern range: {wave_pattern.min():.2f} to {wave_pattern.max():.2f} mm")
    print(f"Water areas found: {water_mask.sum()} pixels ({water_mask.sum()/water_mask.size*100:.1f}%)")
    
    return wave_pattern


def create_wave_pattern(water_mask, lon_grid, lat_grid, wave_height=1.0):
    """Create tactile wave pattern for water areas - DEPRECATED, use create_tactile_wave_pattern instead"""
    print("Warning: Using deprecated create_wave_pattern function")
    return create_tactile_wave_pattern(water_mask, lon_grid, lat_grid)
