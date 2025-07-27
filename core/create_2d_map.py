#!/usr/bin/env python3
"""
Создание 2D карты для тактильного использования
Объединяет границы стран и водные области в единое изображение
"""

import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# Добавляем путь к конфигурации
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import (MAP_BOUNDS, FIGURE_SIZE, DPI, 
                   COUNTRY_COLOR, COUNTRY_EDGE_COLOR, COUNTRY_EDGE_WIDTH,
                   SEA_COLOR, SEA_EDGE_COLOR, SEA_EDGE_WIDTH)

def create_2d_map(countries_file='data/output/merged_countries.geojson', 
                  water_file='data/output/water_areas.geojson',
                  output_file='data/previews/tactile_map.png',
                  zoom_factor=1.0,
                  fixed_bounds=None):
    """Создает 2D карту для тактильного использования
    
    Args:
        countries_file: путь к файлу с границами стран
        water_file: путь к файлу с водными областями (опционально)
        output_file: путь для сохранения карты
        zoom_factor: коэффициент масштабирования (1.0 = полная карта)
        fixed_bounds: фиксированные границы карты (minx, miny, maxx, maxy)
    """
    
    if not os.path.exists(countries_file):
        print(f"❌ Файл {countries_file} не найден")
        return False
    
    try:
        # Загружаем границы стран
        countries_gdf = gpd.read_file(countries_file)
        print(f"✅ Загружены границы стран: {len(countries_gdf)} объектов")
        
        # Пытаемся загрузить водные области
        water_gdf = None
        if os.path.exists(water_file):
            water_gdf = gpd.read_file(water_file)
            print(f"✅ Загружены водные области: {len(water_gdf)} объектов")
        else:
            print(f"⚠️  Файл {water_file} не найден, создаем карту без водных областей")
        
        # Устанавливаем границы карты
        if fixed_bounds is None:
            fixed_bounds = MAP_BOUNDS
        
        minx, miny, maxx, maxy = fixed_bounds
        
        # Применяем масштабирование
        if zoom_factor != 1.0:
            center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2
            width, height = (maxx - minx) / zoom_factor, (maxy - miny) / zoom_factor
            minx = center_x - width / 2
            maxx = center_x + width / 2
            miny = center_y - height / 2
            maxy = center_y + height / 2
        
        # Создаем фигуру
        fig, ax = plt.subplots(1, 1, figsize=FIGURE_SIZE, dpi=DPI)
        ax.set_aspect('equal')
        
        # Рисуем водные области (если есть)
        if water_gdf is not None and not water_gdf.empty:
            water_gdf.plot(ax=ax, 
                          color=SEA_COLOR, 
                          edgecolor=SEA_EDGE_COLOR, 
                          linewidth=SEA_EDGE_WIDTH,
                          alpha=0.8)
            print("✅ Водные области добавлены на карту")
        
        # Рисуем границы стран
        countries_gdf.plot(ax=ax, 
                          color=COUNTRY_COLOR, 
                          edgecolor=COUNTRY_EDGE_COLOR, 
                          linewidth=COUNTRY_EDGE_WIDTH)
        print("✅ Границы стран добавлены на карту")
        
        # Устанавливаем границы отображения
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
        
        # Убираем оси и подписи
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
        
        # Убираем отступы
        plt.tight_layout(pad=0)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Создаем выходную папку если нужно
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем карту
        plt.savefig(output_file, dpi=DPI, bbox_inches='tight', 
                   pad_inches=0, facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"✅ 2D карта сохранена: {output_file}")
        print(f"📏 Границы карты: {minx:.2f}, {miny:.2f}, {maxx:.2f}, {maxy:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании 2D карты: {e}")
        return False

def main():
    """Основная функция"""
    
    print("�️  СОЗДАНИЕ 2D КАРТЫ")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent
    
    # Пути к файлам
    countries_file = base_path / "data/output/merged_countries.geojson"
    water_file = base_path / "data/output/water_areas.geojson"
    output_file = base_path / "data/previews/tactile_map.png"
    
    # Проверяем входные файлы
    print("\n📁 ПРОВЕРКА ВХОДНЫХ ФАЙЛОВ:")
    print("-" * 30)
    
    if not countries_file.exists():
        print(f"❌ Файл границ стран не найден: {countries_file}")
        print("� Запустите сначала скрипты загрузки и объединения стран")
        return False
    
    print(f"✅ Файл границ стран найден: {countries_file}")
    
    if water_file.exists():
        print(f"✅ Файл водных областей найден: {water_file}")
    else:
        print(f"⚠️  Файл водных областей не найден: {water_file}")
        print("💡 Для добавления водных областей запустите water_processor.py")
    
    # Создаем 2D карту
    print("\n🎨 СОЗДАНИЕ 2D КАРТЫ:")
    print("-" * 30)
    
    success = create_2d_map(
        countries_file=str(countries_file),
        water_file=str(water_file),
        output_file=str(output_file)
    )
    
    if success:
        print("\n🎉 2D карта успешно создана!")
        print(f"📁 Результат: {output_file}")
    else:
        print("\n❌ Ошибка при создании 2D карты")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
