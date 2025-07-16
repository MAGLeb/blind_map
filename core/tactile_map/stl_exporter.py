"""
STL export functionality for tactile maps
"""

import numpy as np
from .constants import USE_PYVISTA


def export_to_stl(mesh, output_path):
    """Export mesh to STL file"""
    print(f"Exporting to STL: {output_path}")
    
    if USE_PYVISTA:
        # PyVista mesh - export directly
        mesh.save(output_path)
        print(f"Successfully exported PyVista mesh to {output_path}")
        
    elif USE_PYVISTA == False:  # Using trimesh
        # Get vertices and faces from mesh data
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        # Create trimesh object
        import trimesh
        mesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Export to STL
        mesh_obj.export(output_path)
        print(f"Successfully exported trimesh to {output_path}")
        
    else:
        print("Warning: No 3D library available for STL export. Creating basic PLY file instead.")
        # Create a basic PLY file as fallback
        if isinstance(mesh, dict):
            vertices = mesh['vertices']
            faces = mesh['faces']
        else:
            vertices = np.column_stack([
                mesh['lon'].ravel(),
                mesh['lat'].ravel(),
                mesh['elevation'].ravel()
            ])
            faces = []
        
        ply_path = output_path.replace('.stl', '.ply')
        with open(ply_path, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(vertices)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            
            if len(faces) > 0:
                f.write(f"element face {len(faces)}\n")
                f.write("property list uchar int vertex_indices\n")
            
            f.write("end_header\n")
            
            for vertex in vertices:
                f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
            
            for face in faces:
                f.write(f"3 {face[0]} {face[1]} {face[2]}\n")
        
        print(f"Successfully exported PLY file to {ply_path}")
