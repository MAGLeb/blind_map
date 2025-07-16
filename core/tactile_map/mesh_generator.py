"""
3D mesh generation for tactile maps
"""

import numpy as np
from .constants import USE_PYVISTA


def create_flat_bottom_mesh(lon_grid, lat_grid, elevation, base_thickness=2.0):
    """Create 3D mesh with flat bottom for stable 3D printing"""
    print("Creating 3D mesh with flat bottom...")
    
    # Get dimensions
    ny, nx = elevation.shape
    
    # Create top surface points
    top_points = np.column_stack([
        lon_grid.ravel(),
        lat_grid.ravel(),
        elevation.ravel()
    ])
    
    # Create bottom surface points (flat base)
    bottom_elevation = np.full_like(elevation, -base_thickness)
    bottom_points = np.column_stack([
        lon_grid.ravel(),
        lat_grid.ravel(),
        bottom_elevation.ravel()
    ])
    
    # Combine all points
    all_points = np.vstack([top_points, bottom_points])
    
    # Create faces for top surface
    top_faces = []
    for i in range(ny - 1):
        for j in range(nx - 1):
            # Two triangles per quad
            p1 = i * nx + j
            p2 = i * nx + (j + 1)
            p3 = (i + 1) * nx + j
            p4 = (i + 1) * nx + (j + 1)
            
            # Triangle 1
            top_faces.append([p1, p2, p3])
            # Triangle 2
            top_faces.append([p2, p4, p3])
    
    # Create faces for bottom surface (reversed winding for correct normals)
    bottom_faces = []
    n_top = len(top_points)
    for i in range(ny - 1):
        for j in range(nx - 1):
            # Two triangles per quad
            p1 = n_top + i * nx + j
            p2 = n_top + i * nx + (j + 1)
            p3 = n_top + (i + 1) * nx + j
            p4 = n_top + (i + 1) * nx + (j + 1)
            
            # Triangle 1 (reversed winding)
            bottom_faces.append([p1, p3, p2])
            # Triangle 2 (reversed winding)
            bottom_faces.append([p2, p3, p4])
    
    # Create side faces (connecting top and bottom)
    side_faces = []
    
    # Front edge
    for j in range(nx - 1):
        p1_top = j
        p2_top = j + 1
        p1_bottom = n_top + j
        p2_bottom = n_top + j + 1
        
        side_faces.append([p1_top, p1_bottom, p2_top])
        side_faces.append([p2_top, p1_bottom, p2_bottom])
    
    # Back edge
    for j in range(nx - 1):
        p1_top = (ny - 1) * nx + j
        p2_top = (ny - 1) * nx + j + 1
        p1_bottom = n_top + (ny - 1) * nx + j
        p2_bottom = n_top + (ny - 1) * nx + j + 1
        
        side_faces.append([p1_top, p2_top, p1_bottom])
        side_faces.append([p2_top, p2_bottom, p1_bottom])
    
    # Left edge
    for i in range(ny - 1):
        p1_top = i * nx
        p2_top = (i + 1) * nx
        p1_bottom = n_top + i * nx
        p2_bottom = n_top + (i + 1) * nx
        
        side_faces.append([p1_top, p2_top, p1_bottom])
        side_faces.append([p2_top, p2_bottom, p1_bottom])
    
    # Right edge
    for i in range(ny - 1):
        p1_top = i * nx + (nx - 1)
        p2_top = (i + 1) * nx + (nx - 1)
        p1_bottom = n_top + i * nx + (nx - 1)
        p2_bottom = n_top + (i + 1) * nx + (nx - 1)
        
        side_faces.append([p1_top, p1_bottom, p2_top])
        side_faces.append([p2_top, p1_bottom, p2_bottom])
    
    # Combine all faces
    all_faces = np.vstack([top_faces, bottom_faces, side_faces])
    
    print(f"Created mesh with {len(all_points)} vertices and {len(all_faces)} faces")
    print(f"Base thickness: {base_thickness:.2f} mm")
    
    return {
        'vertices': all_points,
        'faces': all_faces,
        'lon': lon_grid,
        'lat': lat_grid,
        'elevation': elevation
    }


def create_3d_mesh(lon_grid, lat_grid, elevation):
    """Create 3D mesh using PyVista or fallback to basic mesh"""
    print("Creating 3D mesh...")
    
    if USE_PYVISTA:
        # Create mesh with flat bottom
        mesh_data = create_flat_bottom_mesh(lon_grid, lat_grid, elevation)
        
        # Create PyVista mesh from vertices and faces
        vertices = mesh_data['vertices']
        faces = mesh_data['faces']
        
        # Convert faces to PyVista format
        pv_faces = []
        for face in faces:
            pv_faces.extend([3] + face.tolist())
        
        # Create PyVista mesh
        import pyvista as pv
        mesh = pv.PolyData(vertices, pv_faces)
        
        return mesh
    else:
        # Create mesh with flat bottom for trimesh
        return create_flat_bottom_mesh(lon_grid, lat_grid, elevation)
