#!/usr/bin/env python3
"""
Скрипт для загрузки полноценных геометрий водоёмов, рек и горных хребтов
Использует Natural Earth Data для получения полигонов и линий
"""

import os
import requests
import json
import zipfile
import tempfile
import shutil
from pathlib import Path

def download_and_extract_zip(url, extract_to, filename_prefix=""):
    """Скачивает и распаковывает ZIP-архив"""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        # Создаем временный файл для ZIP
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_zip_path = tmp_file.name
        
        # Извлекаем ZIP
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Удаляем временный файл
        os.unlink(tmp_zip_path)
        
        print(f"✓ Extracted to {extract_to}")
        return True
        
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def filter_features_by_region(features, bounds):
    """Фильтрует объекты по региональным границам"""
    filtered = []
    west, east, south, north = bounds["west"], bounds["east"], bounds["south"], bounds["north"]
    
    for feature in features:
        geometry = feature.get('geometry', {})
        if geometry.get('type') == 'Point':
            coords = geometry.get('coordinates', [])
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                if west <= lon <= east and south <= lat <= north:
                    filtered.append(feature)
        elif geometry.get('type') in ['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']:
            # Для сложных геометрий проверяем пересечение с bbox
            # Упрощенная проверка - если хотя бы одна точка попадает в регион
            if intersects_with_region(geometry, bounds):
                filtered.append(feature)
    
    return filtered

def intersects_with_region(geometry, bounds):
    """Проверяет пересечение геометрии с региональными границами"""
    west, east, south, north = bounds["west"], bounds["east"], bounds["south"], bounds["north"]
    
    def check_coordinates(coords):
        """Рекурсивная проверка координат"""
        if isinstance(coords[0], (int, float)):
            # Это точка [lon, lat]
            lon, lat = coords[0], coords[1]
            return west <= lon <= east and south <= lat <= north
        else:
            # Это массив точек или многоуровневый массив
            for coord in coords:
                if check_coordinates(coord):
                    return True
            return False
    
    return check_coordinates(geometry.get('coordinates', []))

def download_natural_earth_features():
    """Загружает основные географические объекты из Natural Earth"""
    
    # Создаем папки
    data_dir = Path("data")
    natural_earth_dir = data_dir / "natural_earth"
    natural_earth_dir.mkdir(parents=True, exist_ok=True)
    
    # Границы нашего региона
    bounds = {
        "west": 12.0,   # Хорватия
        "east": 63.0,   # Иран
        "south": 12.0,  # Йемен
        "north": 47.0   # Граница с Украиной/Россией
    }
    
    # URLs для Natural Earth данных (50m разрешение для хорошего качества)
    downloads = [
        {
            "name": "lakes",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_lakes.zip",
            "file": "ne_50m_lakes.shp",
            "output": "lakes.geojson"
        },
        {
            "name": "rivers",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_rivers_lake_centerlines.zip",
            "file": "ne_50m_rivers_lake_centerlines.shp",
            "output": "rivers.geojson"
        },
        {
            "name": "ocean",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_ocean.zip",
            "file": "ne_50m_ocean.shp",
            "output": "ocean.geojson"
        },
        {
            "name": "coastline",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_coastline.zip",
            "file": "ne_50m_coastline.shp",
            "output": "coastline.geojson"
        },
        {
            "name": "geography_marine_polys",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_geography_marine_polys.zip",
            "file": "ne_50m_geography_marine_polys.shp",
            "output": "seas.geojson"
        },
        {
            "name": "geography_regions_polys",
            "url": "https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_geography_regions_polys.zip",
            "file": "ne_50m_geography_regions_polys.shp",
            "output": "regions.geojson"
        }
    ]
    
    successful_downloads = []
    
    for item in downloads:
        print(f"\n=== Downloading {item['name']} ===")
        
        # Создаем временную папку для каждого скачивания
        temp_dir = natural_earth_dir / f"temp_{item['name']}"
        temp_dir.mkdir(exist_ok=True)
        
        # Скачиваем и распаковываем
        if download_and_extract_zip(item['url'], temp_dir):
            # Ищем шейп-файл
            shp_file = temp_dir / item['file']
            
            if shp_file.exists():
                print(f"✓ Found shapefile: {shp_file}")
                
                # Конвертируем в GeoJSON (нужно установить fiona/geopandas)
                try:
                    import geopandas as gpd
                    
                    # Читаем шейп-файл
                    gdf = gpd.read_file(shp_file)
                    
                    # Фильтруем по региону
                    print(f"Original features: {len(gdf)}")
                    
                    # Фильтруем по bounding box
                    filtered_gdf = gdf.cx[bounds["west"]:bounds["east"], bounds["south"]:bounds["north"]]
                    print(f"Filtered features: {len(filtered_gdf)}")
                    
                    if len(filtered_gdf) > 0:
                        # Сохраняем в GeoJSON
                        output_file = data_dir / item['output']
                        filtered_gdf.to_file(output_file, driver='GeoJSON')
                        
                        print(f"✓ Saved {item['output']} with {len(filtered_gdf)} features")
                        successful_downloads.append(item['output'])
                    else:
                        print(f"⚠ No features found in region for {item['name']}")
                        
                except ImportError:
                    print("⚠ geopandas not installed. Installing...")
                    os.system("pip install geopandas")
                    print("Please re-run the script after installation")
                    
                except Exception as e:
                    print(f"✗ Error processing {item['name']}: {e}")
            else:
                print(f"✗ Shapefile not found: {shp_file}")
        
        # Удаляем временную папку
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return successful_downloads

def create_custom_water_bodies():
    """Создает кастомные водоёмы для нашего региона"""
    
    # Определяем важные моря и заливы с приблизительными границами
    water_bodies = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Черное море",
                    "name_en": "Black Sea",
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [28.0, 41.0], [41.0, 41.0], [41.0, 47.0], [28.0, 47.0], [28.0, 41.0]
                    ]]
                }
            },
            {
                "type": "Feature", 
                "properties": {
                    "name": "Каспийское море",
                    "name_en": "Caspian Sea",
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [47.0, 37.0], [55.0, 37.0], [55.0, 47.0], [47.0, 47.0], [47.0, 37.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Средиземное море",
                    "name_en": "Mediterranean Sea", 
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [12.0, 30.0], [42.0, 30.0], [42.0, 47.0], [12.0, 47.0], [12.0, 30.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Персидский залив",
                    "name_en": "Persian Gulf",
                    "type": "gulf"
                },
                "geometry": {
                    "type": "Polygon", 
                    "coordinates": [[
                        [48.0, 24.0], [56.0, 24.0], [56.0, 30.0], [48.0, 30.0], [48.0, 24.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Красное море",
                    "name_en": "Red Sea",
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [32.0, 12.0], [43.0, 12.0], [43.0, 30.0], [32.0, 30.0], [32.0, 12.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Адриатическое море",
                    "name_en": "Adriatic Sea",
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [12.0, 39.0], [20.0, 39.0], [20.0, 46.0], [12.0, 46.0], [12.0, 39.0]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Эгейское море",
                    "name_en": "Aegean Sea",
                    "type": "sea"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [23.0, 35.0], [29.0, 35.0], [29.0, 41.0], [23.0, 41.0], [23.0, 35.0]
                    ]]
                }
            }
        ]
    }
    
    # Сохраняем кастомные водоёмы
    output_file = "data/custom_water_bodies.geojson"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(water_bodies, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Created {output_file} with {len(water_bodies['features'])} water bodies")
    return output_file

def main():
    """Основная функция"""
    print("=== Downloading Natural Features for Tactile Map ===")
    
    # Создаем кастомные водоёмы (как fallback)
    custom_water = create_custom_water_bodies()
    
    # Пытаемся скачать данные Natural Earth
    try:
        downloaded = download_natural_earth_features()
        
        if downloaded:
            print(f"\n✓ Successfully downloaded {len(downloaded)} feature types:")
            for item in downloaded:
                print(f"  - {item}")
        else:
            print("\n⚠ No Natural Earth data downloaded, using custom water bodies only")
            
    except Exception as e:
        print(f"\n✗ Error during Natural Earth download: {e}")
        print("Using custom water bodies only")
    
    print(f"\n🎉 Natural features download completed!")
    print("Next steps:")
    print("1. Install geopandas if not already installed: pip install geopandas")
    print("2. Re-run this script to download Natural Earth data")
    print("3. Run visualization script to see the results")

if __name__ == "__main__":
    main()
