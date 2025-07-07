#!/usr/bin/env python3
"""
Скрипт для загрузки конкретных водоёмов и рек из OpenStreetMap
Получает полные геометрии (полигоны и линии) для важных объектов
"""

import json
import time
import overpy
from pathlib import Path

def get_region_bounds():
    """Границы нашего региона"""
    return {
        "west": 12.0,   # Хорватия
        "east": 63.0,   # Иран
        "south": 12.0,  # Йемен
        "north": 47.0   # Граница с Украиной/Россией
    }

def create_bbox_string(bounds):
    """Создает строку bbox для Overpass API"""
    return f"{bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']}"

def query_overpass(query, max_retries=3):
    """Выполняет запрос к Overpass API с повторными попытками"""
    api = overpy.Overpass()
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting query (try {attempt + 1}/{max_retries})...")
            result = api.query(query)
            return result
        except Exception as e:
            print(f"Query failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Waiting 10 seconds before retry...")
                time.sleep(10)
            else:
                print("All attempts failed")
                return None

def download_major_rivers():
    """Загружает основные реки из OSM"""
    bounds = get_region_bounds()
    bbox = create_bbox_string(bounds)
    
    # Запрос для крупных рек
    query = f"""
    [out:json][timeout:60];
    (
      // Основные реки по названиям
      way["waterway"="river"]["name"~"^(Дунай|Danube|Dunav|Dunărea)$"]({bbox});
      way["waterway"="river"]["name"~"^(Евфрат|Euphrates|Firat)$"]({bbox});
      way["waterway"="river"]["name"~"^(Тигр|Tigris|Dicle)$"]({bbox});
      way["waterway"="river"]["name"~"^(Кура|Kura|Mtkvari)$"]({bbox});
      way["waterway"="river"]["name"~"^(Аракс|Arax|Aras)$"]({bbox});
      way["waterway"="river"]["name"~"^(Иордан|Jordan|Yarden)$"]({bbox});
      way["waterway"="river"]["name"~"^(Сава|Sava|Save)$"]({bbox});
      way["waterway"="river"]["name"~"^(Марица|Maritsa|Meriç)$"]({bbox});
      way["waterway"="river"]["name"~"^(Нил|Nile|Nil)$"]({bbox});
      way["waterway"="river"]["name"~"^(Драва|Drava|Dráva)$"]({bbox});
      way["waterway"="river"]["name"~"^(Тиса|Tisza|Tisa)$"]({bbox});
      
      // Крупные реки без точного названия
      way["waterway"="river"]["width"~"^[0-9]{2,}"]({bbox});
      relation["waterway"="river"]({bbox});
    );
    out geom;
    """
    
    print("Downloading major rivers from OpenStreetMap...")
    result = query_overpass(query)
    
    if not result:
        print("Failed to download rivers")
        return None
    
    # Конвертируем в GeoJSON
    features = []
    
    # Обрабатываем ways (линии)
    for way in result.ways:
        if len(way.nd) < 2:
            continue
            
        coordinates = []
        for node in way.nd:
            coordinates.append([float(node.lon), float(node.lat)])
        
        feature = {
            "type": "Feature",
            "properties": {
                "name": way.tags.get("name", "Unknown River"),
                "name_en": way.tags.get("name:en", ""),
                "waterway": way.tags.get("waterway", "river"),
                "osm_id": way.id,
                "category": "river"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            }
        }
        features.append(feature)
    
    # Обрабатываем relations (сложные реки)
    for relation in result.relations:
        # Для relations нужна более сложная обработка
        # Пока просто добавляем метаданные
        feature = {
            "type": "Feature",
            "properties": {
                "name": relation.tags.get("name", "Unknown River"),
                "name_en": relation.tags.get("name:en", ""),
                "waterway": relation.tags.get("waterway", "river"),
                "osm_id": relation.id,
                "category": "river_relation",
                "note": "Complex river relation - needs special processing"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0]  # Placeholder
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    print(f"✓ Downloaded {len(features)} river features")
    return geojson

def download_major_lakes():
    """Загружает основные озёра из OSM"""
    bounds = get_region_bounds()
    bbox = create_bbox_string(bounds)
    
    query = f"""
    [out:json][timeout:60];
    (
      // Озёра по названиям
      way["natural"="water"]["name"~"^(Охридское|Ohrid|Ohri)"]({bbox});
      way["natural"="water"]["name"~"^(Преспа|Prespa|Prespes)"]({bbox});
      way["natural"="water"]["name"~"^(Скадарское|Skadar|Shkodër)"]({bbox});
      way["natural"="water"]["name"~"^(Ван|Van Gölü)"]({bbox});
      way["natural"="water"]["name"~"^(Севан|Sevan|Ծովակ)"]({bbox});
      way["natural"="water"]["name"~"^(Мертвое|Dead Sea|Yam HaMelah)"]({bbox});
      way["natural"="water"]["name"~"^(Тивериадское|Galilee|Kinneret)"]({bbox});
      way["natural"="water"]["name"~"^(Резайе|Urmia|Orumiyeh)"]({bbox});
      
      // Крупные озёра
      way["natural"="water"]["area"~"^[0-9]{8,}"]({bbox});
      relation["natural"="water"]({bbox});
    );
    out geom;
    """
    
    print("Downloading major lakes from OpenStreetMap...")
    result = query_overpass(query)
    
    if not result:
        print("Failed to download lakes")
        return None
    
    features = []
    
    # Обрабатываем ways (полигоны озёр)
    for way in result.ways:
        if len(way.nd) < 3:
            continue
            
        coordinates = []
        for node in way.nd:
            coordinates.append([float(node.lon), float(node.lat)])
        
        # Замыкаем полигон
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        
        feature = {
            "type": "Feature",
            "properties": {
                "name": way.tags.get("name", "Unknown Lake"),
                "name_en": way.tags.get("name:en", ""),
                "natural": way.tags.get("natural", "water"),
                "osm_id": way.id,
                "category": "lake"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    print(f"✓ Downloaded {len(features)} lake features")
    return geojson

def download_seas_and_gulfs():
    """Загружает моря и заливы из OSM"""
    bounds = get_region_bounds()
    bbox = create_bbox_string(bounds)
    
    query = f"""
    [out:json][timeout:60];
    (
      // Моря и заливы
      way["natural"="bay"]({bbox});
      way["place"="sea"]({bbox});
      relation["natural"="bay"]({bbox});
      relation["place"="sea"]({bbox});
      
      // Конкретные моря по названиям
      way["name"~"^(Черное|Black Sea|Karadeniz)"]({bbox});
      way["name"~"^(Средиземное|Mediterranean|Akdeniz)"]({bbox});
      way["name"~"^(Каспийское|Caspian|Hazar)"]({bbox});
      way["name"~"^(Красное|Red Sea|Kızıl Deniz)"]({bbox});
      way["name"~"^(Персидский|Persian Gulf|Basra Körfezi)"]({bbox});
    );
    out geom;
    """
    
    print("Downloading seas and gulfs from OpenStreetMap...")
    result = query_overpass(query)
    
    if not result:
        print("Failed to download seas")
        return None
    
    features = []
    
    # Обрабатываем ways
    for way in result.ways:
        if len(way.nd) < 3:
            continue
            
        coordinates = []
        for node in way.nd:
            coordinates.append([float(node.lon), float(node.lat)])
        
        # Замыкаем полигон
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        
        feature = {
            "type": "Feature",
            "properties": {
                "name": way.tags.get("name", "Unknown Sea"),
                "name_en": way.tags.get("name:en", ""),
                "place": way.tags.get("place", ""),
                "natural": way.tags.get("natural", ""),
                "osm_id": way.id,
                "category": "sea"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    print(f"✓ Downloaded {len(features)} sea features")
    return geojson

def save_geojson(data, filename):
    """Сохраняет GeoJSON в файл"""
    if not data or not data.get("features"):
        print(f"⚠ No data to save for {filename}")
        return False
    
    filepath = Path("data") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {filename} with {len(data['features'])} features")
    return True

def main():
    """Основная функция"""
    print("=== Downloading Water Features from OpenStreetMap ===")
    print("This may take several minutes...")
    
    # Загружаем каждый тип данных
    downloads = [
        ("rivers", download_major_rivers, "osm_rivers.geojson"),
        ("lakes", download_major_lakes, "osm_lakes.geojson"),
        ("seas", download_seas_and_gulfs, "osm_seas.geojson")
    ]
    
    successful = 0
    
    for name, download_func, filename in downloads:
        print(f"\n--- Processing {name} ---")
        try:
            data = download_func()
            if save_geojson(data, filename):
                successful += 1
            
            # Пауза между запросами
            print("Waiting 5 seconds before next request...")
            time.sleep(5)
            
        except Exception as e:
            print(f"✗ Error processing {name}: {e}")
    
    print(f"\n🎉 Successfully downloaded {successful}/{len(downloads)} feature types!")
    
    if successful > 0:
        print("\nNext steps:")
        print("1. Check the downloaded files in data/ folder")
        print("2. Run visualization script to see the results")
        print("3. Consider merging with country boundaries")
    else:
        print("\nNo data downloaded. This might be due to:")
        print("- Network connectivity issues")
        print("- OpenStreetMap server limitations")
        print("- Query timeout")
        print("- Missing data in the specified region")

if __name__ == "__main__":
    main()
