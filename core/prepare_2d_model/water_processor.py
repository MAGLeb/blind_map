#!/usr/bin/env python3
"""
Модуль для создания и обработки водных областей
Отделен от основного создания карты для улучшения производительности
"""

import os
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union
import sys

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.config import MAP_BOUNDS


def create_water_areas(input_file='data/output/merged_countries.geojson',
                      output_file='data/output/water_areas.geojson',
                      fixed_bounds=None):
    """Создает водные области как разность между границами карты и странами
    
    Args:
        input_file: путь к файлу со странами
        output_file: путь для сохранения водных областей
        fixed_bounds: фиксированные границы карты (minx, miny, maxx, maxy) в градусах
    
    Returns:
        bool: успешность создания файла
    """
    
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден")
        return False
    
    try:
        # Загружаем страны
        gdf = gpd.read_file(input_file)
        print(f"✅ Загружено стран: {len(gdf)} объектов")
        
        # Устанавливаем границы карты
        if fixed_bounds is None:
            fixed_bounds = MAP_BOUNDS
        
        minx, miny, maxx, maxy = fixed_bounds
        clip_box = box(minx, miny, maxx, maxy)
        
        # Обрезаем страны по границам
        countries_clipped = gdf.clip(clip_box)
        print(f"✅ После обрезки стран: {len(countries_clipped)} объектов")
        
        if len(countries_clipped) > 0:
            # Объединяем все страны в одну геометрию
            countries_union = unary_union(countries_clipped.geometry)
            
            # Создаем водную область как разность
            water_geometry = clip_box.difference(countries_union)
            
            # Упрощаем геометрию для уменьшения размера файла
            # Используем tolerance ~1км (примерно 0.01 градуса)
            water_geometry_simplified = water_geometry.simplify(tolerance=0.01, preserve_topology=True)
            
            if not water_geometry_simplified.is_empty:
                # Создаем GeoDataFrame для воды
                water_gdf = gpd.GeoDataFrame([{
                    'feature_type': 'water',
                    'name': 'Water Areas',
                    'area_sq_km': water_geometry_simplified.area * 111320 * 111320  # приблизительный перевод в кв.км
                }], geometry=[water_geometry_simplified], crs='EPSG:4326')
                
                # Сохраняем
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                water_gdf.to_file(output_file, driver='GeoJSON')
                
                print(f"✅ Водные области сохранены: {output_file}")
                print(f"🌊 Площадь водных областей: {water_geometry_simplified.area * 111320 * 111320:.0f} кв.км")
                print(f"📐 Геометрия упрощена для уменьшения размера файла")
                
                return True
            else:
                print("⚠️  Водная область пуста")
                return False
        else:
            print("❌ Нет стран для создания водной области")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка создания водных областей: {e}")
        return False


def load_or_create_water_areas(countries_file='data/output/merged_countries.geojson',
                              water_file='data/output/water_areas.geojson',
                              fixed_bounds=None,
                              force_recreate=False):
    """Загружает существующие водные области или создает новые при необходимости
    
    Args:
        countries_file: путь к файлу со странами
        water_file: путь к файлу с водными областями
        fixed_bounds: фиксированные границы карты
        force_recreate: принудительно пересоздать водные области
    
    Returns:
        GeoDataFrame или None: водные области
    """
    
    # Проверяем, нужно ли создавать водные области
    if force_recreate or not os.path.exists(water_file):
        print("🌊 Создаем водные области...")
        success = create_water_areas(countries_file, water_file, fixed_bounds)
        if not success:
            return None
    
    # Загружаем водные области
    try:
        if os.path.exists(water_file):
            water_gdf = gpd.read_file(water_file)
            print(f"✅ Загружены водные области: {len(water_gdf)} объектов")
            return water_gdf
        else:
            print("⚠️  Файл водных областей не найден")
            return None
    except Exception as e:
        print(f"❌ Ошибка загрузки водных областей: {e}")
        return None


def create_water_from_countries(countries_gdf, fixed_bounds=None):
    """Создает водные области из GeoDataFrame стран (без сохранения в файл)
    
    Args:
        countries_gdf: GeoDataFrame со странами
        fixed_bounds: фиксированные границы карты
    
    Returns:
        GeoDataFrame или None: водные области
    """
    
    try:
        # Устанавливаем границы карты
        if fixed_bounds is None:
            fixed_bounds = MAP_BOUNDS
        
        minx, miny, maxx, maxy = fixed_bounds
        clip_box = box(minx, miny, maxx, maxy)
        
        # Обрезаем страны по границам
        countries_clipped = countries_gdf.clip(clip_box)
        
        if len(countries_clipped) > 0:
            # Объединяем все страны в одну геометрию
            countries_union = unary_union(countries_clipped.geometry)
            
            # Создаем водную область как разность
            water_geometry = clip_box.difference(countries_union)
            
            # Упрощаем геометрию для лучшей производительности
            water_geometry_simplified = water_geometry.simplify(tolerance=0.01, preserve_topology=True)
            
            if not water_geometry_simplified.is_empty:
                # Создаем GeoDataFrame для воды
                water_gdf = gpd.GeoDataFrame([{
                    'feature_type': 'water',
                    'name': 'Water Areas',
                    'area_sq_km': water_geometry_simplified.area * 111320 * 111320
                }], geometry=[water_geometry_simplified], crs='EPSG:4326')
                
                return water_gdf
            else:
                print("⚠️  Водная область пуста")
                return None
        else:
            print("❌ Нет стран для создания водной области")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания водных областей: {e}")
        return None


def analyze_land_water_ratio(input_file='data/output/merged_countries.geojson',
                             fixed_bounds=None):
    """Анализирует соотношение суши и воды на карте
    
    Args:
        input_file: путь к файлу со странами
        fixed_bounds: фиксированные границы карты
    
    Returns:
        dict: статистика с площадями и процентами
    """
    
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден")
        return None
    
    try:
        # Загружаем страны
        gdf = gpd.read_file(input_file)
        
        # Устанавливаем границы карты
        if fixed_bounds is None:
            fixed_bounds = MAP_BOUNDS
        
        minx, miny, maxx, maxy = fixed_bounds
        clip_box = box(minx, miny, maxx, maxy)
        
        # Общая площадь карты
        total_area = clip_box.area
        
        # Обрезаем страны по границам
        countries_clipped = gdf.clip(clip_box)
        
        if len(countries_clipped) > 0:
            # Площадь суши
            countries_union = unary_union(countries_clipped.geometry)
            land_area = countries_union.area
            
            # Площадь воды
            water_area = total_area - land_area
            
            # Проценты
            land_percent = (land_area / total_area) * 100
            water_percent = (water_area / total_area) * 100
            
            # Переводим в приблизительные квадратные километры
            # (грубое приближение: 1 градус ≈ 111 км)
            km_factor = 111320 * 111320
            
            stats = {
                'total_area_degrees': total_area,
                'land_area_degrees': land_area,
                'water_area_degrees': water_area,
                'total_area_km2': total_area * km_factor,
                'land_area_km2': land_area * km_factor,
                'water_area_km2': water_area * km_factor,
                'land_percent': land_percent,
                'water_percent': water_percent,
                'bounds': fixed_bounds
            }
            
            print(f"\n📊 АНАЛИЗ СООТНОШЕНИЯ СУШИ И ВОДЫ:")
            print(f"  Общая площадь карты: {stats['total_area_km2']:,.0f} кв.км")
            print(f"  Суша: {stats['land_area_km2']:,.0f} кв.км ({land_percent:.1f}%)")
            print(f"  Вода: {stats['water_area_km2']:,.0f} кв.км ({water_percent:.1f}%)")
            print(f"  Границы: {minx:.1f}° - {maxx:.1f}° E, {miny:.1f}° - {maxy:.1f}° N")
            
            return stats
        else:
            print("❌ Нет стран в указанных границах")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return None


def main():
    """Основная функция для создания и анализа водных областей"""
    
    print("🌊 СОЗДАНИЕ И АНАЛИЗ ВОДНЫХ ОБЛАСТЕЙ")
    print("=" * 50)
    
    # Используем границы по умолчанию или можно задать свои
    custom_bounds = None
    # custom_bounds = (15, 35, 75, 55)  # Пример: Балканы + Кавказ + часть Ближнего Востока
    
    bounds = custom_bounds if custom_bounds else MAP_BOUNDS
    
    print(f"🗺️  Границы обработки: {bounds}")
    
    # 1. Анализируем соотношение суши и воды
    print("\n🔍 АНАЛИЗ СООТНОШЕНИЯ СУШИ И ВОДЫ:")
    stats = analyze_land_water_ratio(fixed_bounds=bounds)
    
    # 2. Создаем файл с водными областями
    print("\n🌊 СОЗДАНИЕ ФАЙЛА ВОДНЫХ ОБЛАСТЕЙ:")
    success = create_water_areas(
        input_file='data/output/merged_countries.geojson',
        output_file='data/output/water_areas.geojson',
        fixed_bounds=bounds
    )
    
    if success:
        print(f"\n🎉 ГОТОВО!")
        print("📁 Файлы созданы:")
        print("   - data/output/water_areas.geojson")
        print("🎯 Водные области готовы для использования")
        print("   - Можно быстро загружать в create_final_map.py")
        print("   - Не нужно пересчитывать каждый раз")
    else:
        print("\n❌ Не удалось создать водные области")
    
    print(f"\n💡 Для изменения границ:")
    print(f"   Отредактируйте переменную custom_bounds в этом файле")
    print(f"   Формат: (minx, miny, maxx, maxy) в градусах")
    print(f"   Текущие границы: {bounds}")


if __name__ == "__main__":
    main()
