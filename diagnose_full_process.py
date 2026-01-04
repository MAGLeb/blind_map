#!/usr/bin/env python3
"""
Полная диагностика процесса создания 3D карты
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from core.create_3d_model.elevation_processor import load_elevation_data, smooth_elevation_for_tactile
from core.create_3d_model.water_processor import create_cached_water_mask_from_file
from core.create_3d_model.boundary_processor import load_country_boundaries
from core.config import MAP_BOUNDS
from core.constants import MAX_ELEVATION_MM

def main():
    print("=" * 70)
    print("ПОЛНАЯ ДИАГНОСТИКА ПРОЦЕССА СОЗДАНИЯ 3D КАРТЫ")
    print("=" * 70)
    
    base_path = Path(__file__).parent
    elevation_file = base_path / "data" / "input" / "ETOPO1_Bed_g_gmt4.grd"
    water_geojson = base_path / "data" / "output" / "water_areas.geojson"
    boundaries_file = base_path / "data" / "output" / "merged_countries.geojson"
    
    print(f"\n1. MAP_BOUNDS: {MAP_BOUNDS}")
    print(f"   Формат: (lon_min, lat_min, lon_max, lat_max)")
    print(f"   Значения: lon={MAP_BOUNDS[0]}-{MAP_BOUNDS[2]}°, lat={MAP_BOUNDS[1]}-{MAP_BOUNDS[3]}°")
    
    # Шаг 1: Загрузка elevation
    print(f"\n2. Загрузка elevation данных...")
    lon_grid, lat_grid, elevation = load_elevation_data(str(elevation_file))
    print(f"   Shape: {elevation.shape}")
    print(f"   Lon grid: {lon_grid.min():.2f} - {lon_grid.max():.2f} (в мм)")
    print(f"   Lat grid: {lat_grid.min():.2f} - {lat_grid.max():.2f} (в мм)")
    print(f"   Elevation: {elevation.min():.0f} - {elevation.max():.0f} метров")
    
    # Проверяем высоты
    land_points = (elevation > 0).sum()
    water_points = (elevation <= 0).sum()
    print(f"   Суша (>0m): {land_points} точек ({land_points/elevation.size*100:.1f}%)")
    print(f"   Вода (≤0m): {water_points} точек ({water_points/elevation.size*100:.1f}%)")
    
    # Шаг 2: Сглаживание
    print(f"\n3. Сглаживание elevation...")
    elevation_smoothed = smooth_elevation_for_tactile(elevation, smooth_factor=3.0, preserve_features=True)
    
    # Нормализация
    land_mask = elevation_smoothed > 0
    if land_mask.any():
        land_elevation = elevation_smoothed[land_mask]
        elevation_scaled = elevation_smoothed.copy()
        elevation_scaled[land_mask] = (land_elevation / land_elevation.max()) * MAX_ELEVATION_MM
    else:
        elevation_scaled = elevation_smoothed
    
    elevation_scaled[elevation_scaled <= 0] = 0
    print(f"   После масштабирования: {elevation_scaled.min():.2f} - {elevation_scaled.max():.2f} мм")
    
    # Статистика по высотам
    unique_heights = np.unique(elevation_scaled[elevation_scaled > 0])
    print(f"   Уникальных высот на суше: {len(unique_heights)}")
    if len(unique_heights) > 0:
        print(f"   Примеры высот: {unique_heights[:10]}")
    
    # Шаг 3: Водная маска из elevation
    print(f"\n4. Создание водной маски из ELEVATION...")
    water_mask_from_elev = (elevation <= 0)
    water_pct_elev = water_mask_from_elev.sum() / water_mask_from_elev.size * 100
    print(f"   Вода из elevation: {water_mask_from_elev.sum()}/{water_mask_from_elev.size} ({water_pct_elev:.2f}%)")
    
    # Шаг 4: Водная маска из GeoJSON
    print(f"\n5. Загрузка водной маски из GeoJSON...")
    cache_file = base_path / "data" / "cache" / "water_mask_diagnostic.pkl"
    if cache_file.exists():
        cache_file.unlink()
    
    water_mask_from_geojson = create_cached_water_mask_from_file(
        water_geojson,
        lon_grid, lat_grid,
        cache_file=cache_file
    )
    water_pct_geojson = water_mask_from_geojson.sum() / water_mask_from_geojson.size * 100
    print(f"   Вода из GeoJSON: {water_mask_from_geojson.sum()}/{water_mask_from_geojson.size} ({water_pct_geojson:.2f}%)")
    
    # Шаг 5: Границы стран
    print(f"\n6. Загрузка границ стран...")
    gdf = load_country_boundaries(str(boundaries_file))
    print(f"   Загружено: {len(gdf)} объектов")
    
    if len(gdf) > 0:
        bounds = gdf.total_bounds
        print(f"   Bounds GeoJSON: {bounds}")
        print(f"   Формат: [minx, miny, maxx, maxy]")
        
        # Проверяем, в каких единицах границы
        if bounds[2] > 360 or bounds[3] > 180:
            print(f"   ⚠️ Координаты в миллиметрах!")
        else:
            print(f"   ⚠️ Координаты в градусах!")
    
    # Шаг 6: Проверка совпадения координат
    print(f"\n7. АНАЛИЗ ПРОБЛЕМЫ:")
    print(f"   Lon grid (мм): {lon_grid.min():.2f} - {lon_grid.max():.2f}")
    print(f"   Lat grid (мм): {lat_grid.min():.2f} - {lat_grid.max():.2f}")
    
    if len(gdf) > 0:
        print(f"   GeoJSON bounds: {gdf.total_bounds}")
        
        # Проверяем пересечение
        geojson_minx, geojson_miny, geojson_maxx, geojson_maxy = gdf.total_bounds
        grid_minx, grid_maxx = lon_grid.min(), lon_grid.max()
        grid_miny, grid_maxy = lat_grid.min(), lat_grid.max()
        
        x_overlap = not (geojson_maxx < grid_minx or geojson_minx > grid_maxx)
        y_overlap = not (geojson_maxy < grid_miny or geojson_miny > grid_maxy)
        
        print(f"   X overlap: {x_overlap}")
        print(f"   Y overlap: {y_overlap}")
        
        if not x_overlap or not y_overlap:
            print(f"   ❌ ПРОБЛЕМА: Границы стран НЕ ПЕРЕСЕКАЮТСЯ с сеткой!")
            print(f"   Это объясняет, почему границ не видно на карте.")
    
    # Шаг 7: Проверка применения высот к мешу
    print(f"\n8. Проверка высот на меше:")
    print(f"   Elevation_scaled shape: {elevation_scaled.shape}")
    print(f"   Lon_grid shape: {lon_grid.shape}")
    print(f"   Lat_grid shape: {lat_grid.shape}")
    
    if elevation_scaled.shape != lon_grid.shape:
        print(f"   ❌ ПРОБЛЕМА: Размеры не совпадают!")
    else:
        print(f"   ✅ Размеры совпадают")
    
    # Проверяем, есть ли вообще вариация в высотах
    height_variance = np.var(elevation_scaled)
    print(f"   Дисперсия высот: {height_variance:.4f}")
    if height_variance < 0.01:
        print(f"   ❌ ПРОБЛЕМА: Высоты почти одинаковые (плоская поверхность)!")
    
    print("\n" + "=" * 70)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 70)
    
    if water_pct_geojson > 90:
        print("1. ❌ Водная маска из GeoJSON покрывает >90% карты - это НЕПРАВИЛЬНО")
        print("   Рекомендация: Использовать водную маску из elevation (elevation <= 0)")
    
    if not (x_overlap and y_overlap):
        print("2. ❌ Границы стран не пересекаются с сеткой")
        print("   Рекомендация: Проверить преобразование координат в boundary_processor")
    
    if height_variance < 0.01:
        print("3. ❌ Нет вариации высот на меше")
        print("   Рекомендация: Проверить, как elevation_scaled применяется к мешу")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
