import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd

def load_merged_geojson(file_path='data/merged_countries.geojson'):
    """Загружает объединённый GeoJSON файл"""
    if not os.path.exists(file_path):
        print(f"File {file_path} not found. Run merge_geojson.py first.")
        return None
    
    try:
        gdf = gpd.read_file(file_path)
        print(f"✓ Loaded {len(gdf)} administrative regions from {file_path}")
        return gdf
    except Exception as e:
        print(f"✗ Error loading {file_path}: {e}")
        return None

def create_basic_map(gdf, figsize=(15, 10)):
    """Создает базовую карту"""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Границы регионов
    gdf.boundary.plot(ax=ax, linewidth=0.8, color='black')
    
    # Заливка регионов разными цветами
    colors = plt.cm.Set3(np.linspace(0, 1, len(gdf)))
    gdf.plot(ax=ax, color=colors, alpha=0.3, edgecolor='black', linewidth=0.5)
    
    ax.set_title("Границы выбранных стран (Балканы, Ближний Восток, Кавказ)", fontsize=14)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Равные пропорции
    ax.set_aspect('equal')
    
    return fig, ax

def add_grid_overlay(ax, gdf, grid_size=(3, 2)):
    """Добавляет сетку для разделения на A5 карточки"""
    # Получаем границы области
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    minx, miny, maxx, maxy = bounds
    
    # Размеры ячейки сетки
    cell_width = (maxx - minx) / grid_size[0]
    cell_height = (maxy - miny) / grid_size[1]
    
    # Рисуем сетку
    for i in range(grid_size[0] + 1):
        x = minx + i * cell_width
        ax.axvline(x, color='red', linestyle='--', alpha=0.7, linewidth=2)
    
    for j in range(grid_size[1] + 1):
        y = miny + j * cell_height
        ax.axhline(y, color='red', linestyle='--', alpha=0.7, linewidth=2)
    
    # Подписываем ячейки
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            cell_x = minx + (i + 0.5) * cell_width
            cell_y = miny + (j + 0.5) * cell_height
            card_num = j * grid_size[0] + i + 1
            
            ax.text(cell_x, cell_y, f'A5-{card_num}', 
                   ha='center', va='center', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   fontsize=10, fontweight='bold', color='red')
    
    return bounds, cell_width, cell_height

def save_visualization(fig, output_path='data/merged_countries_preview.png'):
    """Сохраняет визуализацию"""
    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"✓ Preview image saved to {output_path}")

def show_map_info(gdf):
    """Показывает информацию о карте"""
    bounds = gdf.total_bounds
    print(f"\n📊 Map Information:")
    print(f"   Total features: {len(gdf)}")
    
    # Подсчитываем регионы по странам
    if 'source_file' in gdf.columns:
        country_counts = gdf['source_file'].value_counts()
        print(f"   Countries and their feature counts:")
        for country, count in country_counts.items():
            print(f"   - {country}: {count} features")
    
    print(f"   Bounds: {bounds}")
    print(f"   Width: {bounds[2] - bounds[0]:.2f}°")
    print(f"   Height: {bounds[3] - bounds[1]:.2f}°")
    print(f"   CRS: {gdf.crs}")

def main():
    """Основная функция для создания визуализации"""
    # Загружаем данные
    gdf = load_merged_geojson()
    if gdf is None:
        return False
    
    # Показываем информацию о карте
    show_map_info(gdf)
    
    # Создаем базовую карту
    print("\nCreating visualization...")
    fig, ax = create_basic_map(gdf)
    
    # Добавляем сетку для A5 карточек
    bounds, cell_width, cell_height = add_grid_overlay(ax, gdf)
    
    # Сохраняем изображение
    save_visualization(fig)
    
    # Показываем карту
    plt.show()
    
    print("\n✓ Visualization completed!")
    print(f"✓ Grid size: 3x2 (6 A5 cards)")
    print(f"✓ Cell size: {cell_width:.2f}° x {cell_height:.2f}°")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Map visualization ready!")
    else:
        print("\n❌ Visualization failed.")
