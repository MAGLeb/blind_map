import os
import requests
import json

# Список ISO-кодов
ISO_CODES = [
    'SRB', 'BIH', 'HRV', 'BGR', 'GRC', 'ALB', 'MKD', 'MNE', 'XKX',
    'TUR', 'ARM', 'AZE', 'GEO',
    'SYR', 'LBN', 'ISR', 'JOR', 'IRQ', 'IRN',
    'SAU', 'KWT', 'ARE', 'QAT', 'BHR', 'OMN', 'YEM',
    'EGY', 'LBY'
]

# Папка для скачанных файлов
os.makedirs('data/countries', exist_ok=True)

def download_country(iso):
    """Скачивает GeoJSON для одной страны по ISO-коду"""
    # Для Азербайджана используем ADM1 (регионы), для остальных - ADM0 (границы стран)
    if iso == 'AZE':
        adm_level = 'ADM1'
        print(f"Using ADM1 (regions) for Azerbaijan")
    else:
        adm_level = 'ADM0'
        print(f"Using ADM0 (country boundaries) for {iso}")
    
    url = f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{adm_level}/"
    print(f"Requesting {adm_level} GeoJSON for {iso} from {url}")
    
    try:
        r = requests.get(url, timeout=30)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            # API возвращает JSON с метаданными, включая ссылку на GeoJSON
            data = r.json()
            if 'gjDownloadURL' in data:
                geojson_url = data['gjDownloadURL']
                fname = f"data/countries/{iso}.geojson"
                
                print(f"Downloading {iso} from {geojson_url}...")
                r2 = requests.get(geojson_url, timeout=60)
                if r2.status_code == 200:
                    with open(fname, 'wb') as f:
                        f.write(r2.content)
                    print(f"✓ {iso} downloaded successfully")
                else:
                    print(f"✗ Failed to download GeoJSON for {iso}")
                    return None
                
                return fname
            else:
                print(f"✗ No GeoJSON URL found for {iso}")
                return None
        else:
            print(f"✗ Failed to get metadata for {iso}: {r.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error downloading {iso}: {e}")
        return None

def main():
    """Основная функция для скачивания всех стран"""
    files = []
    print(f"Starting download for {len(ISO_CODES)} countries...")
    
    for iso in ISO_CODES:
        f = download_country(iso)
        if f:
            files.append(f)
    
    print(f"\n✓ Successfully downloaded {len(files)} countries")
    
    if not files:
        print("No GeoJSON files downloaded.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Download completed! Run 'python scripts/merge_geojson.py' to merge files.")
    else:
        print("\n❌ Download failed.")
