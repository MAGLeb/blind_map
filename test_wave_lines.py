#!/usr/bin/env python3
"""
Тестируем создание волновых линий
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from core.create_3d_model.elevation_processor import load_elevation_data
from core.create_3d_model.water_processor import (
    create_cached_water_mask_from_file,
    create_tactile_wave_lines,
    create_tactile_wave_pattern
)
from core.config import MAP_BOUNDS

def main():
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ ВОЛНОВЫХ ЛИНИЙ")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    elevation_file = base_path / "data" / "input" / "ETOPO1_Bed_g_gmt4.grd"
    water_geojson = base_path / "data" / "output" / "water_areas.geojson"
    cache_file = base_path / "data" / "cache" / "water_mask_from_file.pkl"
    
    print(f"\n1. MAP_BOUNDS: {MAP_BOUNDS}")
    
    # Загружаем сетку
    print(f"\n2. Загрузка сетки высот...")
    lon_grid, lat_grid, elevation = load_elevation_data(str(elevation_file))
    print(f"   Shape: {lon_grid.shape}")
    print(f"   Lon range: {lon_grid.min():.2f} - {lon_grid.max():.2f} mm")
    print(f"   Lat range: {lat_grid.min():.2f} - {lat_grid.max():.2f} mm")
    
    # Создаём водную маску
    print(f"\n3. Создание водной маски...")
    water_mask = create_cached_water_mask_from_file(
        water_geojson,
        lon_grid, lat_grid,
        cache_file=cache_file
    )
    water_percent = (water_mask.sum() / water_mask.size) * 100
    print(f"   Вода: {water_mask.sum()}/{water_mask.size} ({water_percent:.2f}%)")
    
    # Создаём волновой паттерн
    print(f"\n4. Создание волнового паттерна...")
    wave_pattern = create_tactile_wave_pattern(water_mask, lon_grid, lat_grid)
    wave_nonzero = (wave_pattern > 0).sum()
    print(f"   Ненулевые значения: {wave_nonzero}/{wave_pattern.size}")
    print(f"   Диапазон высот: {wave_pattern.min():.4f} - {wave_pattern.max():.4f} mm")
    
    # Создаём волновые линии
    print(f"\n5. Создание волновых линий...")
    wave_lines = create_tactile_wave_lines(water_mask, lon_grid, lat_grid, elevation)
    print(f"   Создано сегментов: {len(wave_lines)}")
    
    if len(wave_lines) > 0:
        total_points = sum(len(w['points']) for w in wave_lines)
        print(f"   Всего точек: {total_points}")
        print(f"   Точек на сегмент (среднее): {total_points / len(wave_lines):.1f}")
        
        # Показываем первые 3 сегмента
        for i, wave in enumerate(wave_lines[:3]):
            pts = wave['points']
            # Точки теперь в формате (lon, lat, height)
            heights = [p[2] for p in pts]
            print(f"   Сегмент {i+1}: {len(pts)} точек, высоты {min(heights):.3f} - {max(heights):.3f} mm")
            print(f"              width={wave.get('width', 'N/A')}mm, max_height={wave.get('height', 'N/A')}mm")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЁН УСПЕШНО")
    print("=" * 60)

if __name__ == "__main__":
    main()
