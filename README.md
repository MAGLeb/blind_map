# Blind Map — Tactile Map for the Visually Impaired

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![3D Printing](https://img.shields.io/badge/3D%20Printing-PLA-orange.svg)
![Region](https://img.shields.io/badge/Region-Europe%20%7C%20Middle%20East-green.svg)

3D-printable map for learning geography by touch.

![Preview](preview.png)

## Features

- **Tactile terrain** — mountains and plains you can feel
- **Raised borders** — walls between countries for easy identification
- **Wave pattern** — distinguishes sea from land
- **Capital markers** — hemisphere bumps mark capital cities
- **7-segment numbers** — each country numbered for reference
- **Braille legend** — separate card with country names
- **Puzzle connectors** — 4 cards snap together

## Specification

### Dimensions

| Parameter | Value |
|-----------|-------|
| Map size | 400×320 mm |
| Cards | 4 pcs (2×2) + legend |
| Card size | 200×160 mm |
| Base thickness | 6 mm |

### Region

- Bounds: 5°—70° E, 12°—55° N
- Includes: Balkans, Caucasus, Middle East, North Africa
- 24 numbered countries

### Tactile Elements

| Element | Height | Size | Note |
|---------|--------|------|------|
| **Country borders** | 5 mm | width 2.5 mm | Walls between countries |
| **Terrain** | 0—10 mm | — | Mountains, plains |
| **Water (sea)** | 2 mm | waves every 4 mm | Sinusoidal waves |
| **Capitals** | 2 mm | ⌀3 mm | Hemisphere (bump) |
| **Country numbers** | 1.5 mm | 7-segment | Near capital |

### Puzzle Connectors

| Parameter | Value |
|-----------|-------|
| Tab (protrusion) | 8×4×3 mm |
| Slot (hole) | +0.5 mm clearance |
| Position | Bottom part of base |

### Legend (separate card)

- Numbers 1-24 with country names (Braille)
- Texture samples: waves (sea), wall (border), bump (capital)

## Data Preparation

Data files are not included (too large). To download:

```bash
# 1. Download country borders from geoBoundaries
python core/prepare_data/download_geojson.py

# 2. Merge into single file
python core/prepare_data/merge_geojson.py

# 3. Download ETOPO1 elevation manually:
#    https://www.ngdc.noaa.gov/mgg/global/
#    Place as: data/input/ETOPO1_Bed_g_gmt4.grd
```

| Data | Source |
|------|--------|
| **Country borders** | [geoBoundaries](https://www.geoboundaries.org/) |
| **Elevation** | [NOAA ETOPO1](https://www.ngdc.noaa.gov/mgg/global/) |

## Project Structure

```
blind_map/
├── core/
│   ├── config.py          # Map region
│   ├── constants.py       # Parameters
│   ├── generate.py        # STL generator
│   └── prepare_data/      # Data download scripts
│       ├── download_geojson.py
│       └── merge_geojson.py
├── data/                  # Not in repo
│   ├── input/             # ETOPO1 elevation
│   ├── output/            # STL files
│   └── countries/         # GeoJSON files
└── README.md
```

## 3D Printing

- **Material**: PLA
- **Infill**: 15-20%
- **Layer**: 0.2 mm
