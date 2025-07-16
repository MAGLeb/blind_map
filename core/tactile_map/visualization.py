"""
Visualization functionality for tactile maps
"""

import numpy as np
import matplotlib.pyplot as plt
from .constants import USE_PYVISTA


def visualize_mesh(mesh, title="3D Tactile Map"):
    """Visualize the 3D mesh"""
    print("Visualizing mesh...")
    
    if USE_PYVISTA:
        import pyvista as pv
        plotter = pv.Plotter()
        plotter.add_mesh(mesh, show_edges=True, color='lightgray')
        plotter.add_title(title)
        plotter.show_axes()
        plotter.show()
    else:
        # Fallback to matplotlib 3D plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if isinstance(mesh, dict) and 'vertices' in mesh:
            # New mesh structure with flat bottom
            vertices = mesh['vertices']
            
            # Separate top and bottom vertices
            n_vertices = len(vertices) // 2
            top_vertices = vertices[:n_vertices]
            bottom_vertices = vertices[n_vertices:]
            
            # Plot top surface
            elevation = mesh['elevation']
            step = max(1, elevation.shape[0] // 50)
            
            X = mesh['lon'][::step, ::step]
            Y = mesh['lat'][::step, ::step]
            Z = elevation[::step, ::step]
            
            ax.plot_surface(X, Y, Z, alpha=0.8, cmap='terrain')
            
            # Plot bottom surface
            Z_bottom = np.full_like(Z, bottom_vertices[0, 2])
            ax.plot_surface(X, Y, Z_bottom, alpha=0.3, color='gray')
            
        else:
            # Old mesh structure fallback
            step = max(1, mesh['elevation'].shape[0] // 100)
            
            X = mesh['lon'][::step, ::step]
            Y = mesh['lat'][::step, ::step]
            Z = mesh['elevation'][::step, ::step]
            
            ax.plot_surface(X, Y, Z, alpha=0.7, cmap='terrain')
        
        ax.set_title(title)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation')
        
        plt.tight_layout()
        plt.show()
