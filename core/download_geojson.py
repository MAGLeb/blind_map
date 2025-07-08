import os
import requests
import json

# Список ISO-кодов
ISO_CODES = [
    'SRB', 'BIH', 'HRV', 'BGR', 'GRC', 'ALB', 'MKD', 'MNE', 'XKX',
    'TUR', 'ARM', 'AZE', 'GEO',
    'SYR', 'LBN', 'ISR', 'JOR', 'IRQ', 'IRN',
    'SAU', 'KWT', 'ARE', 'QAT', 'BHR', 'OMN', 'YEM',
    'EGY', 'LBY',
    # Дополнительные страны для расширенной карты
    'ITA', 'FRA', 'CHE', 'AUT', 'DEU', 'UKR', 'ROU', 'CYP', 
    'SDN', 'AFG', 'TKM',
    # Новые страны по запросу
    'SSD',  # Южный Судан
    'ETH',  # Эфиопия
    'KAZ',  # Казахстан
    'PAK',  # Пакистан
    'DJI',  # Джибути (для контекста Красного моря)
    # Дополнительные страны для заполнения белых участков
    'MDA',  # Молдова
    'RUS',  # Россия (Российская Федерация)
    # Страны для заполнения пробелов в Северной Африке и Европе
    'MAR',  # Марокко (западная часть Африки)
    'TUN',  # Тунис (между Ливией и Алжиром)
    'DZA',  # Алжир
    'SVN',  # Словения
    'HUN',  # Венгрия
    'SVK',  # Словакия
    'CZE',  # Чехия
    'POL',  # Польша
    'LTU',  # Литва
    'LVA',  # Латвия
    'EST',  # Эстония
    'BLR',  # Беларусь
    'FIN',  # Финляндия (северная часть)
    'SWE',  # Швеция (северо-западная часть)
    'NOR',  # Норвегия (для полноты Скандинавии)
    'ESP',  # Испания (юго-западная Европа)
    'PRT',  # Португалия
    'GBR',  # Великобритания (острова)
    'IRL',  # Ирландия
    'ISL',  # Исландия
    'MLT',  # Мальта
    'UZB',  # Узбекистан (Центральная Азия)
    'KGZ',  # Киргизия
    'TJK',  # Таджикистан
    'IND',  # Индия (восточная граница с Пакистаном)
    'CHN',  # Китай (северо-восток от Казахстана)
    'MNG',  # Монголия (между Россией и Китаем)
    # Additional countries by request
    'NLD',  # Netherlands
    'BEL',  # Belgium
    'LUX',  # Luxembourg
    'NER',  # Niger
    'TCD',  # Chad
    'NGA',  # Nigeria
    'CMR'   # Cameroon
]

# Папка для скачанных файлов
os.makedirs('data/countries', exist_ok=True)

def download_country(iso):
    """Скачивает GeoJSON для одной страны по ISO-коду"""
    fname = f"data/countries/{iso}.geojson"
    
    # Проверяем, не скачан ли уже файл
    if os.path.exists(fname):
        print(f"✓ {iso} already exists, skipping download")
        return fname, True  # True означает, что файл уже существовал
    
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
                
                print(f"Downloading {iso} from {geojson_url}...")
                r2 = requests.get(geojson_url, timeout=60)
                if r2.status_code == 200:
                    with open(fname, 'wb') as f:
                        f.write(r2.content)
                    print(f"✓ {iso} downloaded successfully")
                    return fname, False  # False означает новая загрузка
                else:
                    print(f"✗ Failed to download GeoJSON for {iso}")
                    return None, False
                
            else:
                print(f"✗ No GeoJSON URL found for {iso}")
                return None, False
        else:
            print(f"✗ Failed to get metadata for {iso}: {r.status_code}")
            return None, False
    except Exception as e:
        print(f"✗ Error downloading {iso}: {e}")
        return None, False

def main():
    """Основная функция для скачивания всех стран"""
    files = []
    existing_files = []
    new_downloads = []
    failed_downloads = []
    
    print(f"Starting download for {len(ISO_CODES)} countries...")
    
    for iso in ISO_CODES:
        result = download_country(iso)
        if result[0]:  # Если файл получен (или уже существовал)
            files.append(result[0])
            if result[1]:  # Если файл уже существовал
                existing_files.append(iso)
            else:  # Если файл был скачан сейчас
                new_downloads.append(iso)
        else:
            failed_downloads.append(iso)
    
    print(f"\n=== Download Summary ===")
    print(f"✓ Total files available: {len(files)}")
    print(f"🆕 New downloads: {len(new_downloads)}")
    print(f"📁 Already existed: {len(existing_files)}")
    print(f"❌ Failed downloads: {len(failed_downloads)}")
    
    if new_downloads:
        print(f"\nNewly downloaded countries:")
        for iso in new_downloads:
            print(f"  - {iso}")
    
    if existing_files:
        print(f"\nSkipped (already existed):")
        for iso in existing_files:
            print(f"  - {iso}")
    
    if failed_downloads:
        print(f"\nFailed to download:")
        for iso in failed_downloads:
            print(f"  - {iso}")
    
    if not files:
        print("No GeoJSON files available.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Download completed! Run 'python scripts/merge_geojson.py' to merge files.")
    else:
        print("\n❌ Download failed.")
