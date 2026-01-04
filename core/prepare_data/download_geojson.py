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
    'ITA', 'FRA', 'CHE', 'AUT', 'DEU', 'UKR', 'ROU', 'CYP',
    'SDN', 'AFG', 'TKM',
    'SSD', 'ETH', 'KAZ', 'PAK', 'DJI',
    'MDA', 'RUS',
    'MAR', 'TUN', 'DZA',
    'SVN', 'HUN', 'SVK', 'CZE', 'POL',
    'LTU', 'LVA', 'EST', 'BLR', 'FIN', 'SWE', 'NOR',
    'ESP', 'PRT', 'GBR', 'IRL', 'ISL', 'MLT',
    'UZB', 'KGZ', 'TJK',
    'IND', 'CHN', 'MNG',
    'NLD', 'BEL', 'LUX',
    'NER', 'TCD', 'NGA', 'CMR'
]

os.makedirs('data/countries', exist_ok=True)

def download_country(iso):
    """Downloads GeoJSON for a single country by ISO code"""
    fname = f"data/countries/{iso}.geojson"

    if os.path.exists(fname):
        print(f"✓ {iso} already exists, skipping")
        return fname, True

    adm_level = 'ADM1' if iso == 'AZE' else 'ADM0'
    url = f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{adm_level}/"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if 'gjDownloadURL' in data:
                r2 = requests.get(data['gjDownloadURL'], timeout=60)
                if r2.status_code == 200:
                    with open(fname, 'wb') as f:
                        f.write(r2.content)
                    print(f"✓ {iso} downloaded")
                    return fname, False
        print(f"✗ {iso} failed")
        return None, False
    except Exception as e:
        print(f"✗ {iso}: {e}")
        return None, False

def main():
    files = []
    for iso in ISO_CODES:
        result = download_country(iso)
        if result[0]:
            files.append(result[0])

    print(f"\n✓ {len(files)}/{len(ISO_CODES)} countries available")
    return len(files) > 0

if __name__ == "__main__":
    main()
