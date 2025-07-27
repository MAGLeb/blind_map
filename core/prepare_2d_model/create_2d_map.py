#!/usr/bin/env python3
"""
Создание финальной визуализации обогащенной карты
Показывает только итоговый результат: страны + береговая линия + моря
Поддерживает фиксированные границы карты для контроля области отображения
"""

import os
import sys
import math
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from shapely.geometry import box

# Добавляем путь к конфигурации
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.config import (MAP_BOUNDS, FIGURE_SIZE, DPI, 
                              COUNTRY_COLOR, COUNTRY_EDGE_COLOR, COUNTRY_EDGE_WIDTH,
                              SEA_COLOR, SEA_EDGE_COLOR, SEA_EDGE_WIDTH)
from core.prepare_2d_model.water_processor import (load_or_create_water_areas, create_water_from_countries)

def create_final_map(input_file='data/output/merged_countries.geojson', 
                    output_file='data/previews/tactile_map.png',
                    zoom_factor=1.0,
                    fixed_bounds=None,
                    fast_mode=True):
    """Создает финальную карту для тактильного использования
    
    Args:
        input_file: путь к файлу с обогащенной картой
        output_file: путь для сохранения итоговой карты
        zoom_factor: коэффициент масштабирования (1.0 = полная карта, 2.0 = увеличение в 2 раза)
        fixed_bounds: фиксированные границы карты (minx, miny, maxx, maxy) в градусах
                     Если None, используются границы из конфигурации
        fast_mode: если True, пытается загрузить готовые водные области из файла
    """
    
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден")
        return False
    
    try:
        # Загружаем обогащенную карту
        gdf = gpd.read_file(input_file)
        print(f"✅ Загружена обогащенная карта: {len(gdf)} объектов")
        
        # Устанавливаем фиксированные границы карты
        if fixed_bounds is None:
            fixed_bounds = MAP_BOUNDS
            print(f"🗺️  Используются стандартные границы: {fixed_bounds}")
        else:
            print(f"🗺️  Используются заданные границы: {fixed_bounds}")
        
        minx, miny, maxx, maxy = fixed_bounds
        
        # Создаем геометрию для обрезки (прямоугольник с фиксированными границами)
        clip_box = box(minx, miny, maxx, maxy)
        
        # Обрезаем все данные по фиксированным границам
        print("✂️  Обрезаем данные по фиксированным границам...")
        gdf_clipped = gdf.clip(clip_box)
        print(f"✅ После обрезки: {len(gdf_clipped)} объектов")
        
        # Разделяем по типам объектов (уже обрезанные)
        countries = gdf_clipped[gdf_clipped['feature_type'] == 'country'] if 'feature_type' in gdf_clipped.columns else gdf_clipped
        seas = gdf_clipped[gdf_clipped['feature_type'] == 'sea'] if 'feature_type' in gdf_clipped.columns else None
        
        # Создаем водные области эффективно
        print("🌊 Обрабатываем водные области...")
        if fast_mode:
            # Пытаемся загрузить готовые водные области
            water_gdf = load_or_create_water_areas(
                countries_file=input_file,
                water_file='data/output/water_areas.geojson',
                fixed_bounds=fixed_bounds,
                force_recreate=False
            )
        else:
            # Создаем водные области на лету
            water_gdf = create_water_from_countries(countries, fixed_bounds)
        
        if water_gdf is not None:
            print(f"🌊 Водные области готовы")
        else:
            print("⚠️  Водные области не созданы")
        
        # Создаем простую карту с фиксированными размерами
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # Белый фон
        ax.set_facecolor('white')
        
        # 1. Сначала водные области (если есть)
        if water_gdf is not None and len(water_gdf) > 0:
            water_gdf.plot(ax=ax, color=SEA_COLOR, 
                          edgecolor=SEA_EDGE_COLOR, linewidth=SEA_EDGE_WIDTH, zorder=1)
            print(f"🌊 Водные области: отображены")
        
        # 2. Потом моря (если они есть как отдельные объекты)
        if seas is not None and len(seas) > 0:
            seas.plot(ax=ax, color=SEA_COLOR, 
                     edgecolor=SEA_EDGE_COLOR, linewidth=SEA_EDGE_WIDTH, zorder=1)
            print(f"🌊 Моря: {len(seas)} объектов")
        
        # 3. Потом страны
        if len(countries) > 0:
            countries.plot(ax=ax, color=COUNTRY_COLOR, 
                          edgecolor=COUNTRY_EDGE_COLOR, linewidth=COUNTRY_EDGE_WIDTH, zorder=2)
            print(f"🗺️  Страны: {len(countries)} регионов")
        
        # 3. Береговая линия поверх всего (убрано)
        # if coastline is not None and len(coastline) > 0:
        #     coastline.plot(ax=ax, color='#0d47a1', linewidth=2, zorder=3)
        #     print(f"🏖️  Береговая линия: {len(coastline)} объектов")
        
        # Настройки карты
        ax.set_title('Тактильная карта: Балканы, Кавказ и Ближний Восток', 
                    fontsize=18, fontweight='bold', pad=20)
        
        # Убираем оси для чистого вида
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Добавляем рамку
        for spine in ax.spines.values():
            spine.set_edgecolor('#666666')
            spine.set_linewidth(2)
        
        # Равные пропорции
        ax.set_aspect('equal')
        
        # ФИКСИРОВАННЫЕ границы карты (НЕ зависят от содержимого)
        # Применяем масштабирование к фиксированным границам
        if zoom_factor != 1.0:
            # Находим центр фиксированной области
            center_x = (minx + maxx) / 2
            center_y = (miny + maxy) / 2
            
            # Вычисляем новые размеры с учетом масштабирования
            width = (maxx - minx) / zoom_factor
            height = (maxy - miny) / zoom_factor
            
            # Новые границы от центра
            new_minx = center_x - width / 2
            new_maxx = center_x + width / 2
            new_miny = center_y - height / 2
            new_maxy = center_y + height / 2
        else:
            new_minx, new_miny, new_maxx, new_maxy = minx, miny, maxx, maxy
            width = maxx - minx
            height = maxy - miny
        
        # Добавляем небольшой отступ (2% от ширины)
        margin = width * 0.02
        ax.set_xlim(new_minx - margin, new_maxx + margin)
        ax.set_ylim(new_miny - margin, new_maxy + margin)
        
        # Обновляем заголовок с информацией о масштабе
        if zoom_factor != 1.0:
            ax.set_title(f'Тактильная карта (масштаб x{zoom_factor:.1f}): Балканы, Кавказ и Ближний Восток', 
                        fontsize=18, fontweight='bold', pad=20)
        else:
            ax.set_title('Тактильная карта: Балканы, Кавказ и Ближний Восток', 
                        fontsize=18, fontweight='bold', pad=20)
        
        # Изменяем имя файла для масштабированных версий
        if zoom_factor != 1.0:
            base_name = os.path.splitext(output_file)[0]
            ext = os.path.splitext(output_file)[1]
            output_file = f"{base_name}_zoom_{zoom_factor:.1f}x{ext}"
        
        # Сохраняем с параметрами из конфига
        plt.tight_layout()
        plt.savefig(output_file, dpi=DPI, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"✅ Финальная карта сохранена: {output_file}")
        
        # Показываем статистику
        print(f"\n📊 СТАТИСТИКА КАРТЫ:")
        print(f"  Фиксированная область: {maxx - minx:.1f}° × {maxy - miny:.1f}°")
        print(f"  От {minx:.1f}°E до {maxx:.1f}°E")
        print(f"  От {miny:.1f}°N до {maxy:.1f}°N")
        if zoom_factor != 1.0:
            print(f"  Масштаб: x{zoom_factor}")
            print(f"  Показываемая область: {width:.1f}° × {height:.1f}°")
            print(f"  Центр увеличения: {(minx + maxx) / 2:.1f}°E, {(miny + maxy) / 2:.1f}°N")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания карты: {e}")
        return False

def main(zoom_factor=1.0, bounds=None, fast_mode=True):
    """Основная функция"""
    print("🎨 СОЗДАНИЕ ФИНАЛЬНОЙ ТАКТИЛЬНОЙ КАРТЫ")
    print("=" * 50)
    
    if fast_mode:
        print("⚡ Быстрый режим: используем готовые водные области (если есть)")
    
    if zoom_factor != 1.0:
        print(f"🔍 Масштаб: x{zoom_factor}")
    
    if bounds:
        print(f"🗺️  Фиксированные границы: {bounds}")
    
    # Убираем автоматическое создание водных областей - это не задача этого файла
    # Если нужно создать водные области, используйте отдельный скрипт:
    # python core/water_processor.py
    
    # Создаем финальную карту
    success = create_final_map(zoom_factor=zoom_factor, fixed_bounds=bounds, fast_mode=fast_mode)
    
    if success:
        print(f"\n🎉 ГОТОВО!")
        if zoom_factor != 1.0:
            print(f"📁 Файл: data/previews/tactile_map_zoom_{zoom_factor:.1f}x.png")
        else:
            print("📁 Файл: data/previews/tactile_map.png")
        print("🎯 Карта готова для тактильного использования")
        print("   - Фиксированная область отображения")
        print("   - Четкие границы стран")
        print("   - Крупные моря")
        print("   - Высокое разрешение для печати")
    else:
        print("\n❌ Не удалось создать карту")

if __name__ == "__main__":
    import sys
    
    # Проверяем аргументы командной строки
    zoom_factor = 1.0
    custom_bounds = None
    
    if len(sys.argv) > 1:
        try:
            zoom_factor = float(sys.argv[1])
            if zoom_factor <= 0:
                print("❌ Zoom factor must be positive!")
                print("💡 Usage: python scripts/create_final_map.py [zoom_factor]")
                print("   zoom_factor examples: 1.0 (full map), 1.5 (1.5x zoom), 2.0 (2x zoom), 3.0 (3x zoom)")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid zoom factor! Must be a number.")
            print("💡 Usage: python scripts/create_final_map.py [zoom_factor]")
            print("   zoom_factor examples: 1.0 (full map), 1.5 (1.5x zoom), 2.0 (2x zoom), 3.0 (3x zoom)")
            sys.exit(1)
    
    # Можете здесь задать свои границы
    # Примеры координат:
    # Балканы + Кавказ + часть Ближнего Востока (без полной России):
    # custom_bounds = (15, 35, 75, 55)
    
    # Если хотите включить только южную часть России:
    # custom_bounds = (15, 35, 85, 60)
    
    # Более узкая область (только Балканы + Турция):
    # custom_bounds = (15, 35, 45, 50)
    
    # Флаги для работы скрипта
    # save_water удален - используйте отдельный скрипт core/water_processor.py
    
    main(zoom_factor, custom_bounds)
    
    print(f"\n💡 Для настройки области карты:")
    print(f"   Отредактируйте переменную MAP_BOUNDS в config/map_bounds.py")
    print(f"   Или раскомментируйте custom_bounds в этом файле")
    print(f"   Формат: (minx, miny, maxx, maxy) в градусах")
    print(f"   Текущие границы: {MAP_BOUNDS}")
    
    print(f"\n💡 Для ускорения работы:")
    print(f"   1. Сначала запустите: python core/water_processor.py")
    print(f"   2. Это создаст файл data/output/water_areas.geojson")
    print(f"   3. Потом основной скрипт будет работать быстрее")
    
    if zoom_factor != 1.0:
        print(f"\n💡 Usage examples:")
        print(f"   python core/create_final_map.py        # Full map")
        print(f"   python core/create_final_map.py 1.5    # 1.5x zoom")
        print(f"   python core/create_final_map.py 2.0    # 2x zoom")
        print(f"   python core/create_final_map.py 3.0    # 3x zoom")
