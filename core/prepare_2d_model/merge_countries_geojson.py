import os
import json
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

def load_downloaded_files():
    """Загружает список скачанных файлов"""
    files_list_path = 'data/downloaded_files.json'
    
    if os.path.exists(files_list_path):
        with open(files_list_path, 'r') as f:
            return json.load(f)
    else:
        # Если файл списка не существует, ищем все .geojson файлы
        countries_dir = 'data/countries'
        if os.path.exists(countries_dir):
            files = []
            for fname in os.listdir(countries_dir):
                if fname.endswith('.geojson'):
                    files.append(os.path.join(countries_dir, fname))
            return files
        else:
            return []

def merge_geojson_files(files):
    """Объединяет список GeoJSON файлов в один GeoDataFrame"""
    print("Merging GeoJSON files...")
    gdfs = []
    
    for f in files:
        try:
            gdf = gpd.read_file(f)
            # Добавляем информацию о файле для отладки
            iso_code = os.path.basename(f).replace('.geojson', '')
            gdf['source_file'] = iso_code
            gdfs.append(gdf)
            print(f"✓ Loaded {os.path.basename(f)} with {len(gdf)} features")
        except Exception as e:
            print(f"✗ Error loading {f}: {e}")
    
    if not gdfs:
        print("No valid GeoJSON files to merge.")
        return None
    
    # Объединяем все GeoDataFrame
    merged = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    
    return merged
    
def save_merged_geojson(merged_gdf, output_path='data/output/merged_countries.geojson'):
    """Сохраняет объединённый GeoDataFrame в файл"""
    print(f"Saving merged GeoJSON to {output_path}...")
    merged_gdf.to_file(output_path, driver="GeoJSON")
    print("✓ Merged GeoJSON saved")

def main():
    """Основная функция для объединения GeoJSON файлов"""
    # Загружаем список файлов
    files = load_downloaded_files()
    
    if not files:
        print("No GeoJSON files found. Run 'python scripts/download_geojson.py' first.")
        return False
    
    print(f"Found {len(files)} GeoJSON files to merge")
    
    # Объединяем файлы
    merged_data = merge_geojson_files(files)
    
    if merged_data is None:
        return False
    
    # Сохраняем объединенные данные как есть
    save_merged_geojson(merged_data)
    
    print(f"\n✓ Successfully processed {len(files)} country files")
    print(f"✓ Total features: {len(merged_data)}")
    
    # Подсчитываем регионы Азербайджана
    if 'source_file' in merged_data.columns:
        aze_regions = merged_data[merged_data['source_file'] == 'AZE']
        if len(aze_regions) > 0:
            print(f"✓ Azerbaijan regions: {len(aze_regions)}")
    
    print(f"✓ Coordinate system: {merged_data.crs}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Merge completed! Run 'python scripts/visualize_map.py' to create visualization.")
    else:
        print("\n❌ Merge failed.")
