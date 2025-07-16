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
from .constants import BOUNDARY_HEIGHT_MM, BOUNDARY_WIDTH_MM
from .utils import calculate_grid_resolution, mm_to_pixels


def load_country_boundaries(file_path):
    """Load country boundaries from GeoJSON file"""
    print("Loading country boundaries...")
    
    gdf = gpd.read_file(file_path)
    
    # Filter boundaries within map bounds
    minx, miny, maxx, maxy = MAP_BOUNDS
    bounds_polygon = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
    
    # Clip to map bounds
    gdf_clipped = gdf.clip(bounds_polygon)
    
    return gdf_clipped


def create_tactile_boundary_mesh(gdf, lon_grid, lat_grid, elevation):
    """
    Создает тактильные границы стран с точными размерами в миллиметрах
    
    Параметры:
    - Высота границ: BOUNDARY_HEIGHT_MM ПОВЕРХ рельефа
    - Ширина границ: BOUNDARY_WIDTH_MM (точно в миллиметрах)
    - Границы возвышаются над рельефом для четкого тактильного различения
    """
    from .utils import degrees_to_mm
    from scipy.ndimage import binary_dilation
    
    print("Creating tactile boundary mesh...")
    
    # Вычисляем разрешение сетки
    mm_per_pixel = calculate_grid_resolution(lon_grid, lat_grid)
    print(f"Grid resolution: {mm_per_pixel:.3f} mm/pixel")
    
    # Преобразуем ширину границ из мм в пиксели
    boundary_width_pixels = mm_to_pixels(BOUNDARY_WIDTH_MM, mm_per_pixel)
    print(f"Boundary width: {BOUNDARY_WIDTH_MM} mm = {boundary_width_pixels} pixels")
    
    # Тактильные параметры для границ
    boundary_height = BOUNDARY_HEIGHT_MM  # мм (тонкие, но различимые границы ПОВЕРХ рельефа)
    
    # Create boundary mask
    boundary_mask = np.zeros_like(elevation, dtype=bool)
    
    # Get grid dimensions and coordinates
    height, width = elevation.shape
    
    print(f"Grid dimensions: {height}x{width}")
    print(f"Processing {len(gdf)} countries...")
    
    # Process each country boundary
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue
            
        print(f"Processing boundary {idx+1}/{len(gdf)}")
        
        # Extract boundary coordinates
        boundary_coords = []
        if geom.geom_type == 'Polygon':
            boundary_coords.append(list(geom.exterior.coords))
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                boundary_coords.append(list(poly.exterior.coords))
        
        # For each boundary line, convert to grid coordinates
        for coords in boundary_coords:
            if len(coords) < 2:
                continue
                
            # Convert boundary coordinates to mm and then to grid indices
            for i in range(len(coords) - 1):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[i + 1]
                
                # Convert to mm coordinates
                x1_mm, y1_mm = degrees_to_mm(lon1, lat1, MAP_BOUNDS)
                x2_mm, y2_mm = degrees_to_mm(lon2, lat2, MAP_BOUNDS)
                
                # Find number of points along segment
                num_points = max(10, int(np.sqrt((x2_mm-x1_mm)**2 + (y2_mm-y1_mm)**2) / 2))
                
                if num_points > 1:
                    x_points = np.linspace(x1_mm, x2_mm, num_points)
                    y_points = np.linspace(y1_mm, y2_mm, num_points)
                    
                    # Find closest grid points
                    for x_mm, y_mm in zip(x_points, y_points):
                        # Find closest grid indices
                        x_distances = np.abs(lon_grid[0, :] - x_mm)
                        y_distances = np.abs(lat_grid[:, 0] - y_mm)
                        
                        lon_idx = np.argmin(x_distances)
                        lat_idx = np.argmin(y_distances)
                        
                        # Mark boundary
                        if 0 <= lat_idx < height and 0 <= lon_idx < width:
                            boundary_mask[lat_idx, lon_idx] = True
    
    # Расширяем границы для создания нужной ширины в миллиметрах
    if boundary_width_pixels > 1:
        structure = np.ones((boundary_width_pixels, boundary_width_pixels))
        boundary_mask = binary_dilation(boundary_mask, structure=structure, iterations=1)
    
    # Создаем возвышение границ ПОВЕРХ рельефа
    # Границы поднимаются на фиксированную высоту над рельефом
    boundary_elevation = np.zeros_like(elevation)
    boundary_elevation[boundary_mask] = boundary_height  # Фиксированная высота над рельефом
    
    print(f"Boundary parameters: height={boundary_height}mm ABOVE terrain, width={BOUNDARY_WIDTH_MM}mm ({boundary_width_pixels}px)")
    print(f"Boundary coverage: {np.sum(boundary_mask) / boundary_mask.size * 100:.2f}%")
    
    return boundary_elevation


def create_boundary_mesh(gdf, lon_grid, lat_grid, elevation, boundary_width=0.01, boundary_height=2.0):
    """Create 3D mesh for country boundaries - DEPRECATED, use create_tactile_boundary_mesh instead"""
    print("Warning: Using deprecated create_boundary_mesh function")
    return create_tactile_boundary_mesh(gdf, lon_grid, lat_grid, elevation)
