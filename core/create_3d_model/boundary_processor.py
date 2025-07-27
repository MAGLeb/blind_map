"""
Country boundary processing for tactile maps
"""

import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import sys
import os

# Add the core directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MAP_BOUNDS
from ..constants import BOUNDARY_HEIGHT_MM, BOUNDARY_WIDTH_MM, PROGRESS_REPORT_INTERVAL


def load_country_boundaries(file_path):
    """
    Загружает границы стран из GeoJSON файла
    
    Возвращает:
    - gdf: GeoDataFrame с границами стран, обрезанными по границам карты
    """
    print("Loading country boundaries...")
    
    gdf = gpd.read_file(file_path)
    
    # Создаем полигон границ карты
    minx, miny, maxx, maxy = MAP_BOUNDS
    bounds_polygon = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
    
    # Обрезаем по границам карты
    gdf_clipped = gdf.clip(bounds_polygon)
    
    return gdf_clipped


def _get_elevation_at_point(x, y, lon_grid, lat_grid, elevation):
    """
    Получает высоту рельефа в точке
    
    Возвращает:
    - elevation: высота в мм
    """
    x_distances = np.abs(lon_grid[0, :] - x)
    y_distances = np.abs(lat_grid[:, 0] - y)
    
    x_idx = np.argmin(x_distances)
    y_idx = np.argmin(y_distances)
    
    if 0 <= x_idx < lon_grid.shape[1] and 0 <= y_idx < lat_grid.shape[0]:
        return elevation[y_idx, x_idx]
    else:
        return np.mean(elevation[elevation > 0])


def _process_country_polygons(geom):
    """
    Извлекает все полигоны из геометрии страны
    
    Возвращает:
    - polygons: список полигонов
    """
    polygons = []
    if geom.geom_type == 'Polygon':
        polygons.append(geom)
    elif geom.geom_type == 'MultiPolygon':
        polygons.extend(geom.geoms)
    return polygons


def create_tactile_boundary_mesh(gdf, lon_grid, lat_grid, elevation):
    """
    Создает тактильные границы как непрерывные стены из полигонов
    
    Параметры:
    - gdf: GeoDataFrame стран
    - lon_grid, lat_grid: координатные сетки
    - elevation: высоты рельефа
    
    Возвращает:
    - tuple: (boundary_points, boundary_faces) для интеграции в 3D модель
    """
    print("Creating tactile boundary mesh (CONTINUOUS POLYGON WALLS)...")
    
    from .utils import degrees_to_mm
    from .mesh_generator import create_polygon_wall
    
    all_boundary_points = []
    all_boundary_faces = []
    point_offset = 0
    
    # Обрабатываем каждую страну
    for counter, (idx, row) in enumerate(gdf.iterrows(), 1):
        geom = row.geometry
        if geom is None:
            continue
            
        if counter % PROGRESS_REPORT_INTERVAL == 0 or counter == len(gdf):
            print(f"Processing country {counter}/{len(gdf)}")
        
        # Получаем все полигоны страны
        polygons = _process_country_polygons(geom)
        
        # Создаем стену для каждого полигона
        for poly in polygons:
            coords = list(poly.exterior.coords)
            if len(coords) < 4:  # Минимум для замкнутого полигона
                continue
            
            # Конвертируем в мм и получаем высоты
            coords_mm = []
            base_elevations = []
            
            for lon, lat in coords:
                x_mm, y_mm = degrees_to_mm(lon, lat, MAP_BOUNDS)
                elevation_at_point = _get_elevation_at_point(x_mm, y_mm, lon_grid, lat_grid, elevation)
                coords_mm.append((x_mm, y_mm))
                base_elevations.append(elevation_at_point)
            
            # Создаем непрерывную стену из полигона
            wall_points, wall_faces = create_polygon_wall(
                coords_mm, base_elevations, BOUNDARY_HEIGHT_MM, BOUNDARY_WIDTH_MM
            )
            
            if len(wall_points) > 0:
                all_boundary_points.append(wall_points)
                # Сдвигаем индексы граней
                wall_faces_shifted = wall_faces + point_offset
                all_boundary_faces.append(wall_faces_shifted)
                point_offset += len(wall_points)
    
    # Объединяем все точки и грани
    if all_boundary_points:
        combined_points = np.vstack(all_boundary_points)
        combined_faces = np.vstack(all_boundary_faces)
        print(f"Created {len(combined_points)} boundary points and {len(combined_faces)} boundary faces")
        return combined_points, combined_faces
    else:
        print("No boundary points created")
        return np.array([]), np.array([])


def create_boundary_mesh(gdf, lon_grid, lat_grid, elevation, boundary_width=0.01, boundary_height=2.0):
    """
    УСТАРЕВШАЯ ФУНКЦИЯ - используйте create_tactile_boundary_mesh
    """
    print("Warning: create_boundary_mesh is deprecated. Use create_tactile_boundary_mesh instead.")
    return create_tactile_boundary_mesh(gdf, lon_grid, lat_grid, elevation)
