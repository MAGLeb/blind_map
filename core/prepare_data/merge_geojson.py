import os
import geopandas as gpd
import pandas as pd

def merge_geojson_files():
    """Merges all GeoJSON files from data/countries into one"""
    countries_dir = 'data/countries'
    output_path = 'data/output/merged_countries.geojson'

    files = [os.path.join(countries_dir, f) for f in os.listdir(countries_dir) if f.endswith('.geojson')]

    if not files:
        print("No GeoJSON files found. Run download_geojson.py first.")
        return False

    print(f"Merging {len(files)} files...")
    gdfs = []

    for f in files:
        try:
            gdf = gpd.read_file(f)
            gdf['source_file'] = os.path.basename(f).replace('.geojson', '')
            gdfs.append(gdf)
        except Exception as e:
            print(f"✗ {f}: {e}")

    if not gdfs:
        return False

    merged = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)

    os.makedirs('data/output', exist_ok=True)
    merged.to_file(output_path, driver="GeoJSON")

    print(f"✓ Saved {len(merged)} features to {output_path}")
    return True

if __name__ == "__main__":
    merge_geojson_files()
