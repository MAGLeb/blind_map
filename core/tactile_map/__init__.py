"""
Tactile map generation package for blind accessibility
"""

from .constants import *
from .elevation_processor import load_elevation_data, smooth_elevation_for_tactile, optimize_for_tactile_perception
from .water_processor import create_tactile_wave_pattern
from .boundary_processor import load_country_boundaries, create_tactile_boundary_mesh
from .mesh_generator import create_3d_mesh, create_flat_bottom_mesh, create_3d_mesh_with_boundaries
from .stl_exporter import export_to_stl
from .visualization import visualize_mesh
from .utils import degrees_to_mm, calculate_real_scale, print_map_info, print_tactile_recommendations, bresenham_line

__all__ = [
    'load_elevation_data',
    'smooth_elevation_for_tactile',
    'optimize_for_tactile_perception',
    'create_tactile_wave_pattern',
    'load_country_boundaries',
    'create_tactile_boundary_mesh',
    'create_3d_mesh',
    'create_flat_bottom_mesh',
    'create_3d_mesh_with_boundaries',
    'export_to_stl',
    'visualize_mesh',
    'degrees_to_mm',
    'calculate_real_scale',
    'print_map_info',
    'print_tactile_recommendations',
    'bresenham_line'
]
