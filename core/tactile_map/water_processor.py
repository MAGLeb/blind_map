"""
Water area processing for tactile maps
"""

import numpy as np


def create_tactile_wave_pattern(water_mask, lon_grid, lat_grid):
    """
    Создает тактильный паттерн волн для водных областей
    
    Параметры оптимизированы для тактильного восприятия:
    - Высота волн: 0.3-0.5 мм (различимая, но не мешающая)
    - Расстояние между волнами: 3-5 мм (комфортно для пальца)
    - Направление: параллельные линии легче различать чем сетка
    """
    print("Creating tactile wave pattern...")
    
    # Расстояние между волнами в мм (оптимально для пальца)
    wave_spacing_mm = 4.0
    
    # Высота волн (должна быть меньше минимальной различимой высоты рельефа)
    wave_height = 0.3  # мм
    
    # Создаем параллельные волны (проще для восприятия чем сетка)
    # Используем координаты в мм
    wave_pattern = np.sin(2 * np.pi * lon_grid / wave_spacing_mm) * wave_height
    
    # Применяем только к водным областям
    wave_pattern = wave_pattern * water_mask
    
    print(f"Wave pattern: spacing={wave_spacing_mm}mm, height={wave_height}mm")
    print(f"Wave pattern range: {wave_pattern.min():.2f} to {wave_pattern.max():.2f} mm")
    
    return wave_pattern


def create_wave_pattern(water_mask, lon_grid, lat_grid, wave_height=1.0):
    """Create tactile wave pattern for water areas - DEPRECATED, use create_tactile_wave_pattern instead"""
    print("Warning: Using deprecated create_wave_pattern function")
    return create_tactile_wave_pattern(water_mask, lon_grid, lat_grid)
