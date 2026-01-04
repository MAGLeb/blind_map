#!/usr/bin/env python3
"""
Диагностика проблемы с водными масками и координатами
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from core.create_3d_model.elevation_processor import load_elevation_data
from core.create_3d_model.water_processor import create_cached_water_mask_from_file
from core.config import MAP_BOUNDS

def main():
    print("=" * 60)
    print("ДИАГНОСТИКА ВОДНЫХ МАСОК И КООРДИНАТ")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    elevation_file = base_path / "data" / "input" / "ETOPO1_Bed_g_gmt4.grd"
    water_geojson = base_path / "data" / "output" / "water_areas.geojson"
    
    print(f"\n1. Проверка файлов:")
    print(f"   Elevation file exists: {elevation_file.exists()}")
    print(f"   Water GeoJSON exists: {water_geojson.exists()}")
    
    if not elevation_file.exists():
        print("   ❌ Файл высот не найден!")
        return
    
    print(f"\n2. MAP_BOUNDS из config:")
    print(f"   {MAP_BOUNDS}")
    print(f"   Format: (lon_min, lon_max, lat_max, lat_min)")
    
    # Загружаем сетку высот
    print(f"\n3. Загрузка сетки высот...")
    lon_grid, lat_grid, elevation = load_elevation_data(str(elevation_file))
    
    print(f"\n4. Информация о сетке:")
    print(f"   Shape: {lon_grid.shape}")
    print(f"   Longitude range: {lon_grid.min():.4f} .. {lon_grid.max():.4f}")
    print(f"   Latitude range:  {lat_grid.min():.4f} .. {lat_grid.max():.4f}")
    print(f"   Elevation range: {elevation.min():.2f} .. {elevation.max():.2f} m")
    
    # Проверяем, есть ли вода в elevation данных
    water_in_elevation = (elevation <= 0).sum()
    total_points = elevation.size
    water_percent_elev = (water_in_elevation / total_points) * 100
    print(f"\n5. Вода в elevation данных (elevation <= 0):")
    print(f"   Water points: {water_in_elevation}/{total_points} ({water_percent_elev:.2f}%)")
    
    if not water_geojson.exists():
        print(f"\n❌ Water GeoJSON не найден: {water_geojson}")
        return
    
    # Загружаем GeoJSON для проверки
    print(f"\n6. Проверка Water GeoJSON...")
    import geopandas as gpd
    water_gdf = gpd.read_file(water_geojson)
    print(f"   Features in GeoJSON: {len(water_gdf)}")
    print(f"   CRS: {water_gdf.crs}")
    print(f"   Bounds: {water_gdf.total_bounds}")
    
    if len(water_gdf) > 0:
        print(f"   First feature geometry type: {water_gdf.geometry.iloc[0].geom_type}")
        print(f"   First feature bounds: {water_gdf.geometry.iloc[0].bounds}")
    
    # Создаём водную маску
    print(f"\n7. Создание водной маски из GeoJSON...")
    cache_file = base_path / "data" / "cache" / "test_water_mask.pkl"
    if cache_file.exists():
        cache_file.unlink()
        print(f"   Удалён старый кэш: {cache_file}")
    
    water_mask = create_cached_water_mask_from_file(
        water_geojson,
        lon_grid, lat_grid,
        cache_file=cache_file
    )
    
    print(f"\n8. Результаты водной маски:")
    print(f"   Mask shape: {water_mask.shape}")
    print(f"   Water points in mask: {water_mask.sum()}/{water_mask.size}")
    water_percent_mask = (water_mask.sum() / water_mask.size) * 100
    print(f"   Water percentage: {water_percent_mask:.2f}%")
    
    # Сравнение
    print(f"\n9. Сравнение:")
    print(f"   Вода по elevation: {water_percent_elev:.2f}%")
    print(f"   Вода по GeoJSON маске: {water_percent_mask:.2f}%")
    print(f"   Разница: {abs(water_percent_elev - water_percent_mask):.2f}%")
    
    if water_percent_mask < 1.0:
        print(f"\n⚠️  ПРОБЛЕМА: Водная маска почти пуста ({water_percent_mask:.2f}%)!")
        print(f"   Возможные причины:")
        print(f"   1. Несовпадение координат между GeoJSON и сеткой")
        print(f"   2. Неправильная интерпретация MAP_BOUNDS")
        print(f"   3. Проблема с CRS в GeoJSON")
    else:
        print(f"\n✅ Водная маска создана успешно!")
    
    # Визуализация для проверки
    print(f"\n10. Сохранение диагностической визуализации...")
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Elevation
    im1 = axes[0].imshow(elevation, cmap='terrain', origin='lower', 
                        extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()])
    axes[0].set_title('Elevation Data')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    plt.colorbar(im1, ax=axes[0], label='Elevation (m)')
    
    # Water from elevation
    water_from_elev = elevation <= 0
    im2 = axes[1].imshow(water_from_elev, cmap='Blues', origin='lower',
                        extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()])
    axes[1].set_title(f'Water from Elevation (≤0m)\n{water_percent_elev:.1f}%')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    plt.colorbar(im2, ax=axes[1], label='Is Water')
    
    # Water mask from GeoJSON
    im3 = axes[2].imshow(water_mask, cmap='Blues', origin='lower',
                        extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()])
    axes[2].set_title(f'Water Mask from GeoJSON\n{water_percent_mask:.1f}%')
    axes[2].set_xlabel('Longitude')
    axes[2].set_ylabel('Latitude')
    plt.colorbar(im3, ax=axes[2], label='Is Water')
    
    plt.tight_layout()
    
    output_path = base_path / "data" / "debug" / "water_mask_diagnosis.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"   ✅ Сохранено: {output_path}")
    plt.close()
    
    print("\n" + "=" * 60)
    print("ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 60)

if __name__ == "__main__":
    main()
