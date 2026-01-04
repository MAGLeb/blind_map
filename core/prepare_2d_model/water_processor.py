#!/usr/bin/env python3
"""
Модуль для создания и анализа водных областей в пределах карты.
"""

import os
import sys
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from core.config import MAP_BOUNDS


def _normalize_bounds(bounds):
    """
    Приводит проектные границы (lon_min, lon_max, lat_max, lat_min) к (minx, miny, maxx, maxy).
    """
    if bounds is None or len(bounds) != 4:
        raise ValueError(f"Bad bounds: {bounds}")
    lon_min, lon_max, lat_max, lat_min = bounds
    if lat_max < lat_min:
        lat_max, lat_min = lat_min, lat_max
    if lon_max < lon_min:
        lon_max, lon_min = lon_min, lon_max
    return (float(lon_min), float(lat_min), float(lon_max), float(lat_max))


def create_water_areas(input_file='data/output/merged_countries.geojson',
                      output_file='data/output/water_areas.geojson',
                      fixed_bounds=None):
    """
    Создаёт GeoJSON водных областей как разность окна карты и объединённой суши.
    """
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден")
        return False
    try:
        gdf = gpd.read_file(input_file)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            gdf = gdf.to_crs("EPSG:4326")
        bounds = fixed_bounds if fixed_bounds is not None else MAP_BOUNDS
        minx, miny, maxx, maxy = _normalize_bounds(bounds)
        clip_box = box(minx, miny, maxx, maxy)
        print(f"✅ Используем границы: lon[{minx},{maxx}] lat[{miny},{maxy}]")
        countries_clipped = gdf.clip(clip_box)
        print(f"✅ После обрезки стран: {len(countries_clipped)} объектов")
        if len(countries_clipped) == 0:
            water_gdf = gpd.GeoDataFrame([{"feature_type": "water", "name": "Water Areas"}],
                                         geometry=[clip_box], crs="EPSG:4326")
        else:
            countries_clipped["geometry"] = countries_clipped.buffer(0)
            countries_union = unary_union(countries_clipped.geometry)
            water_geometry = clip_box.difference(countries_union)
            if water_geometry.is_empty:
                print("⚠️  Водная область пуста")
                return False
            water_geometry_simplified = water_geometry.simplify(tolerance=0.01, preserve_topology=True)
            km2 = water_geometry_simplified.area * 111320 * 111320
            water_gdf = gpd.GeoDataFrame([{
                "feature_type": "water",
                "name": "Water Areas",
                "area_sq_km": km2
            }], geometry=[water_geometry_simplified], crs="EPSG:4326")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        water_gdf.to_file(output_file, driver="GeoJSON")
        print(f"✅ Водные области сохранены: {output_file}")
        if "area_sq_km" in water_gdf.columns:
            print(f"🌊 Площадь водных областей: {water_gdf.iloc[0]['area_sq_km']:.0f} кв.км")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания водных областей: {e}")
        return False


def load_or_create_water_areas(countries_file='data/output/merged_countries.geojson',
                              water_file='data/output/water_areas.geojson',
                              fixed_bounds=None,
                              force_recreate=False):
    """
    Загружает готовые водные области или создаёт новые при необходимости.
    """
    if force_recreate or not os.path.exists(water_file):
        print("🌊 Создаём водные области…")
        ok = create_water_areas(countries_file, water_file, fixed_bounds)
        if not ok:
            return None
    try:
        water_gdf = gpd.read_file(water_file)
        if water_gdf.crs is None:
            water_gdf = water_gdf.set_crs("EPSG:4326")
        else:
            water_gdf = water_gdf.to_crs("EPSG:4326")
        print(f"✅ Загружены водные области: {len(water_gdf)} объектов")
        return water_gdf
    except Exception as e:
        print(f"❌ Ошибка загрузки водных областей: {e}")
        return None


def create_water_from_countries(countries_gdf, fixed_bounds=None):
    """
    Возвращает GeoDataFrame воды из GeoDataFrame стран без записи на диск.
    """
    try:
        if countries_gdf is None or len(countries_gdf) == 0:
            print("❌ Нет стран для создания водной области")
            return None
        if countries_gdf.crs is None:
            countries_gdf = countries_gdf.set_crs("EPSG:4326")
        else:
            countries_gdf = countries_gdf.to_crs("EPSG:4326")
        bounds = fixed_bounds if fixed_bounds is not None else MAP_BOUNDS
        minx, miny, maxx, maxy = _normalize_bounds(bounds)
        clip_box = box(minx, miny, maxx, maxy)
        countries_clipped = countries_gdf.clip(clip_box)
        if len(countries_clipped) == 0:
            return gpd.GeoDataFrame([{"feature_type": "water", "name": "Water Areas"}],
                                    geometry=[clip_box], crs="EPSG:4326")
        countries_clipped["geometry"] = countries_clipped.buffer(0)
        countries_union = unary_union(countries_clipped.geometry)
        water_geometry = clip_box.difference(countries_union)
        if water_geometry.is_empty:
            print("⚠️  Водная область пуста")
            return None
        water_geometry_simplified = water_geometry.simplify(tolerance=0.01, preserve_topology=True)
        km2 = water_geometry_simplified.area * 111320 * 111320
        return gpd.GeoDataFrame([{
            "feature_type": "water",
            "name": "Water Areas",
            "area_sq_km": km2
        }], geometry=[water_geometry_simplified], crs="EPSG:4326")
    except Exception as e:
        print(f"❌ Ошибка создания водных областей: {e}")
        return None


def analyze_land_water_ratio(input_file='data/output/merged_countries.geojson',
                             fixed_bounds=None):
    """
    Анализирует соотношение суши и воды в пределах карты.
    """
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден")
        return None
    try:
        gdf = gpd.read_file(input_file)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            gdf = gdf.to_crs("EPSG:4326")
        bounds = fixed_bounds if fixed_bounds is not None else MAP_BOUNDS
        minx, miny, maxx, maxy = _normalize_bounds(bounds)
        clip_box = box(minx, miny, maxx, maxy)
        total_area = clip_box.area
        countries_clipped = gdf.clip(clip_box)
        if len(countries_clipped) == 0:
            land_area = 0.0
        else:
            countries_clipped["geometry"] = countries_clipped.buffer(0)
            land_area = unary_union(countries_clipped.geometry).area
        water_area = total_area - land_area
        km2 = 111320 * 111320
        land_percent = (land_area / total_area) * 100 if total_area else 0.0
        water_percent = (water_area / total_area) * 100 if total_area else 0.0
        stats = {
            "total_area_degrees": total_area,
            "land_area_degrees": land_area,
            "water_area_degrees": water_area,
            "total_area_km2": total_area * km2,
            "land_area_km2": land_area * km2,
            "water_area_km2": water_area * km2,
            "land_percent": land_percent,
            "water_percent": water_percent,
            "bounds_norm": (minx, miny, maxx, maxy)
        }
        print("\n📊 АНАЛИЗ:")
        print(f"  Lon: {minx:.1f}..{maxx:.1f}  Lat: {miny:.1f}..{maxy:.1f}")
        print(f"  Суша: {stats['land_area_km2']:,.0f} км² ({land_percent:.1f}%)")
        print(f"  Вода: {stats['water_area_km2']:,.0f} км² ({water_percent:.1f}%)")
        return stats
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return None


def main():
    """
    Точка входа для создания и анализа водных областей.
    """
    print("🌊 СОЗДАНИЕ И АНАЛИЗ ВОДНЫХ ОБЛАСТЕЙ")
    print("=" * 50)
    bounds = MAP_BOUNDS
    print(f"🗺️  Границы обработки (проектные): {bounds}")
    stats = analyze_land_water_ratio(fixed_bounds=bounds)
    print("\n🌊 СОЗДАНИЕ ФАЙЛА ВОДНЫХ ОБЛАСТЕЙ:")
    ok = create_water_areas(
        input_file='data/output/merged_countries.geojson',
        output_file='data/output/water_areas.geojson',
        fixed_bounds=bounds
    )
    if ok:
        print("\n🎉 ГОТОВО!")
        print("📁 Файлы созданы:")
        print("   - data/output/water_areas.geojson")
    else:
        print("\n❌ Не удалось создать водные области")


if __name__ == "__main__":
    main()
