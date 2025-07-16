"""
Elevation data processing for tactile maps
"""

import numpy as np
import xarray as xr
import sys
import os

# Add the core directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MAP_BOUNDS

from .constants import MAX_ELEVATION_MM, MIN_TACTILE_DIFFERENCE_MM
from .utils import degrees_to_mm


def load_elevation_data(file_path):
    """Load elevation data from NetCDF file and convert to numpy arrays with mm coordinates"""
    print("Loading elevation data...")
    
    # Load NetCDF file
    ds = xr.open_dataset(file_path)
    
    # Extract coordinates and elevation data
    # The exact variable names might vary, so we'll try common ones
    elevation_var = None
    for var in ['z', 'elevation', 'Band1', 'topo']:
        if var in ds.variables:
            elevation_var = var
            break
    
    if elevation_var is None:
        # Take the first data variable
        elevation_var = list(ds.data_vars)[0]
    
    print(f"Using elevation variable: {elevation_var}")
    
    # Extract data within map bounds
    minx, miny, maxx, maxy = MAP_BOUNDS
    print(f"Map bounds: {MAP_BOUNDS}")
    
    # Get coordinate variable names
    lon_var = 'x' if 'x' in ds.coords else 'longitude' if 'longitude' in ds.coords else 'lon'
    lat_var = 'y' if 'y' in ds.coords else 'latitude' if 'latitude' in ds.coords else 'lat'
    
    # Select data within bounds
    ds_bounded = ds.sel(
        {lon_var: slice(minx, maxx), lat_var: slice(miny, maxy)}
    )
    
    print(f"Original dataset shape: {ds[elevation_var].shape}")
    print(f"Bounded dataset shape: {ds_bounded[elevation_var].shape}")
    
    # Subsample data to reduce size for 3D printing (every 20th point for better performance)
    step = 20
    ds_subsampled = ds_bounded.isel(
        {lon_var: slice(None, None, step), lat_var: slice(None, None, step)}
    )
    
    # Extract arrays
    lon = ds_subsampled[lon_var].values
    lat = ds_subsampled[lat_var].values
    elevation = ds_subsampled[elevation_var].values
    
    print(f"Subsampled shape: {elevation.shape}")
    print(f"Elevation range: {elevation.min():.1f} to {elevation.max():.1f} meters")
    
    # Convert coordinates to mm
    lon_mm = np.zeros_like(lon)
    lat_mm = np.zeros_like(lat)
    
    for i, lon_val in enumerate(lon):
        x_mm, _ = degrees_to_mm(lon_val, 0, MAP_BOUNDS)
        lon_mm[i] = x_mm
    
    for i, lat_val in enumerate(lat):
        _, y_mm = degrees_to_mm(0, lat_val, MAP_BOUNDS)
        lat_mm[i] = y_mm
    
    # Create coordinate meshgrids in mm
    lon_grid, lat_grid = np.meshgrid(lon_mm, lat_mm)
    
    return lon_grid, lat_grid, elevation


def smooth_elevation_for_tactile(elevation, smooth_factor=2.0, preserve_features=True):
    """
    Smooth elevation data for tactile accessibility while preserving important features
    
    Args:
        elevation: 2D numpy array of elevation data
        smooth_factor: Gaussian smoothing sigma value (higher = more smoothing)
        preserve_features: Whether to preserve major elevation features
    
    Returns:
        Smoothed elevation array
    """
    from scipy.ndimage import gaussian_filter, median_filter
    
    print(f"Smoothing elevation data (sigma={smooth_factor})...")
    
    # First apply median filter to reduce noise while preserving edges
    elevation_denoised = median_filter(elevation, size=3)
    
    # Then apply Gaussian smoothing for general smoothing
    elevation_smoothed = gaussian_filter(elevation_denoised, sigma=smooth_factor)
    
    if preserve_features:
        # Preserve major features by blending original and smoothed data
        # Higher elevations get less smoothing to preserve mountain ranges
        elevation_normalized = (elevation - elevation.min()) / (elevation.max() - elevation.min())
        blend_factor = 0.3 + 0.7 * elevation_normalized  # 0.3 to 1.0 blending
        
        # Blend: more smoothing in flat areas, less in mountains
        elevation_final = (1 - blend_factor) * elevation_smoothed + blend_factor * elevation
    else:
        elevation_final = elevation_smoothed
    
    return elevation_final


def optimize_for_tactile_perception(elevation):
    """
    Оптимизирует высоты для тактильного восприятия слепыми пользователями
    
    Основано на исследованиях тактильного восприятия:
    - Минимальная различимая высота: 0.8-1.0 мм
    - Оптимальная высота для рельефа: 3-6 мм
    - Максимальная комфортная высота: 8-10 мм
    - Количество различимых уровней: 6-8
    
    Args:
        elevation: 2D numpy array of elevation data
        
    Returns:
        Optimized elevation array
    """
    print("Optimizing elevation for tactile perception...")
    
    # Определяем количество тактильных уровней (6-8 оптимально)
    num_tactile_levels = 6
    
    # Находим только положительные высоты (суша)
    land_mask = elevation > 0
    if not np.any(land_mask):
        return elevation
    
    land_elevation = elevation[land_mask]
    
    # Создаем тактильные уровни
    min_elev = land_elevation.min()
    max_elev = land_elevation.max()
    
    # Создаем уровни с минимальным различимым интервалом
    tactile_levels = np.linspace(MIN_TACTILE_DIFFERENCE_MM, 
                                MAX_ELEVATION_MM, 
                                num_tactile_levels)
    
    # Квантизируем высоты к ближайшим тактильным уровням
    elevation_optimized = elevation.copy()
    
    for i, level in enumerate(tactile_levels):
        if i == 0:
            # Самый низкий уровень
            mask = (land_elevation >= min_elev) & (land_elevation < (tactile_levels[i+1] if i+1 < len(tactile_levels) else max_elev))
            elevation_optimized[land_mask] = np.where(mask, level, elevation_optimized[land_mask])
        elif i == len(tactile_levels) - 1:
            # Самый высокий уровень
            mask = land_elevation >= tactile_levels[i-1] + (tactile_levels[i] - tactile_levels[i-1]) / 2
            elevation_optimized[land_mask] = np.where(mask, level, elevation_optimized[land_mask])
        else:
            # Средние уровни
            lower_bound = tactile_levels[i-1] + (tactile_levels[i] - tactile_levels[i-1]) / 2
            upper_bound = tactile_levels[i] + (tactile_levels[i+1] - tactile_levels[i]) / 2
            
            # Преобразуем обратно в оригинальный диапазон для сравнения
            orig_lower = min_elev + (lower_bound - MIN_TACTILE_DIFFERENCE_MM) * (max_elev - min_elev) / (MAX_ELEVATION_MM - MIN_TACTILE_DIFFERENCE_MM)
            orig_upper = min_elev + (upper_bound - MIN_TACTILE_DIFFERENCE_MM) * (max_elev - min_elev) / (MAX_ELEVATION_MM - MIN_TACTILE_DIFFERENCE_MM)
            
            mask = (land_elevation >= orig_lower) & (land_elevation < orig_upper)
            elevation_optimized[land_mask] = np.where(mask, level, elevation_optimized[land_mask])
    
    print(f"Tactile levels: {tactile_levels}")
    print(f"Height differences: {np.diff(tactile_levels)}")
    print(f"Optimized elevation range: {elevation_optimized.min():.2f} to {elevation_optimized.max():.2f} mm")
    
    return elevation_optimized
