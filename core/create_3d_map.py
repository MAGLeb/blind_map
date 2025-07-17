#!/usr/bin/env python3
"""
3D tactile map generator for blind accessibility
Creates a 3D printable STL file with elevation data, wave patterns, and country boundaries

This is the main entry point that uses the decomposed tactile_map package.
"""

from pathlib import Path
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the decomposed modules
from tactile_map import (
    load_elevation_data,
    smooth_elevation_for_tactile,
    create_tactile_wave_pattern,
    load_country_boundaries,
    create_tactile_boundary_mesh,
    create_3d_mesh,
    create_3d_mesh_with_boundaries,
    export_to_stl,
    visualize_mesh,
    print_map_info,
    print_tactile_recommendations,
    calculate_real_scale
)

from tactile_map.constants import (
    MAX_ELEVATION_MM,
    BASE_THICKNESS_MM,
    FULL_WIDTH_MM,
    FULL_HEIGHT_MM,
    CARD_WIDTH_MM,
    CARD_HEIGHT_MM,
    GRID_COLS,
    GRID_ROWS,
    BOUNDARY_HEIGHT_MM
)

from config import MAP_BOUNDS


def main():
    """Main function to create 3D tactile map"""
    print("=== 3D TACTILE MAP GENERATOR ===")
    
    # Print map information and tactile recommendations
    print_map_info()
    print_tactile_recommendations()
    
    # File paths
    base_path = Path(__file__).parent.parent
    elevation_file = base_path / "data" / "ETOPO1_Bed_g_gmt4.grd"
    boundaries_file = base_path / "data" / "output" / "merged_countries.geojson"
    output_file = base_path / "data" / "output" / "terrain_model.stl"
    
    # Check if files exist
    if not elevation_file.exists():
        print(f"Error: Elevation file not found: {elevation_file}")
        return
    
    if not boundaries_file.exists():
        print(f"Error: Boundaries file not found: {boundaries_file}")
        return
    
    try:
        # 1. Load elevation data
        print("\nStep 1: Loading elevation data...")
        lon_grid, lat_grid, elevation = load_elevation_data(str(elevation_file))
        print(f"Elevation data shape: {elevation.shape}")
        print(f"Elevation range: {elevation.min():.2f} to {elevation.max():.2f}")
        
        # Apply advanced smoothing for tactile accessibility
        print("Step 2: Applying advanced smoothing for tactile accessibility...")
        elevation_smoothed = smooth_elevation_for_tactile(elevation, smooth_factor=3.0, preserve_features=True)
        
        # Normalize positive elevations to 0-MAX_ELEVATION_MM
        land_mask = elevation_smoothed > 0
        if land_mask.any():
            land_elevation = elevation_smoothed[land_mask]
            elevation_scaled = elevation_smoothed.copy()
            elevation_scaled[land_mask] = (land_elevation / land_elevation.max()) * MAX_ELEVATION_MM
        else:
            elevation_scaled = elevation_smoothed
        
        # Set sea level to 0
        elevation_scaled[elevation_scaled <= 0] = 0
        
        print(f"Optimized elevation range: {elevation_scaled.min():.2f} to {elevation_scaled.max():.2f} mm")
        
        # 4. Create water mask (areas where elevation < 0)
        print("Step 4: Processing water areas...")
        water_mask = elevation < 0
        water_percentage = water_mask.sum() / water_mask.size * 100
        print(f"Water coverage: {water_percentage:.1f}%")
        
        # 5. Set water areas to 0 elevation
        elevation_processed = elevation_scaled.copy()
        
        # 6. Add tactile wave pattern to water areas
        print("Step 5: Adding tactile wave pattern...")
        wave_pattern = create_tactile_wave_pattern(water_mask, lon_grid, lat_grid)
        elevation_processed += wave_pattern
        
        # 7. Load country boundaries
        print("Step 6: Loading country boundaries...")
        gdf = load_country_boundaries(str(boundaries_file))
        print(f"Number of boundary features: {len(gdf)}")
        
        # 7. Create vector boundary lines
        print("Step 7: Creating vector boundary lines...")
        boundary_data = create_tactile_boundary_mesh(gdf, lon_grid, lat_grid, elevation_processed)
        
        # 8. Create 3D mesh with vector boundaries
        print("Step 8: Creating 3D mesh with boundaries...")
        mesh = create_3d_mesh_with_boundaries(lon_grid, lat_grid, elevation_processed, boundary_data)
        
        # 9. Export to STL
        print("Step 9: Exporting to STL...")
        export_to_stl(mesh, str(output_file))
        
        # 10. Visualize
        print("Step 10: Visualizing...")
        visualize_mesh(mesh, "3D Tactile Map - Optimized for Blind Users")
        
        # Final summary
        print(f"\n✓ 3D tactile map created successfully!")
        print(f"✓ STL file saved to: {output_file}")
        print(f"✓ Map bounds: {MAP_BOUNDS}")
        print(f"✓ Grid resolution: {lon_grid.shape}")
        print(f"✓ Model dimensions: {FULL_WIDTH_MM}x{FULL_HEIGHT_MM}x{MAX_ELEVATION_MM + BASE_THICKNESS_MM} mm")
        
        # Print card layout information
        print(f"\n=== CARD LAYOUT ===")
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                card_num = row * GRID_COLS + col + 1
                x_start = col * CARD_WIDTH_MM
                y_start = row * CARD_HEIGHT_MM
                x_end = x_start + CARD_WIDTH_MM
                y_end = y_start + CARD_HEIGHT_MM
                print(f"  Card {card_num}: {x_start:3.0f}-{x_end:3.0f}mm x {y_start:3.0f}-{y_end:3.0f}mm")
        
        # Calculate and display scale information
        scale_w, scale_h, real_w, real_h = calculate_real_scale()
        print(f"\n=== SCALE INFORMATION ===")
        print(f"Real territory covered: {real_w:.0f}x{real_h:.0f} km")
        print(f"Scale: 1:{scale_w:.0f} (width), 1:{scale_h:.0f} (height)")
        print(f"1mm on map = {scale_w/1000:.1f}km in reality")
        
        # Tactile accessibility summary
        print(f"\n=== TACTILE ACCESSIBILITY SUMMARY ===")
        print(f"• Elevation levels: 6-8 distinct tactile levels")
        print(f"• Height differences: ≥0.8mm (minimum detectable)")
        print(f"• Country boundaries: {BOUNDARY_HEIGHT_MM}mm ABOVE terrain (clearly detectable)")
        print(f"• Maximum terrain height: {MAX_ELEVATION_MM}mm")
        print(f"• Maximum boundary height: {MAX_ELEVATION_MM + BOUNDARY_HEIGHT_MM}mm")
        print(f"• Wave texture: 0.4mm height, 5.0mm spacing")
        print(f"• Base thickness: {BASE_THICKNESS_MM}mm (stable for handling)")
        print(f"• Total model height: {MAX_ELEVATION_MM + BOUNDARY_HEIGHT_MM + BASE_THICKNESS_MM}mm")
        print("• Flat bottom for stable 3D printing")
        print("• Country boundaries raised above terrain for clear tactile distinction")
        print("• Optimized for finger-tip tactile exploration")
        
    except Exception as e:
        print(f"Error creating 3D map: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
