"""
3D mesh generation for tactile maps
"""

import numpy as np
from ..constants import USE_PYVISTA, BOUNDARY_HEIGHT_MM, BOUNDARY_WIDTH_MM


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


def create_3d_mesh_with_boundaries(lon_grid, lat_grid, elevation, boundary_data):
    """
    Создает 3D модель с рельефом и границами
    
    Параметры:
    - lon_grid, lat_grid: координатные сетки
    - elevation: высоты рельефа
    - boundary_data: данные границ (точки и грани)
    
    Возвращает:
    - объединенная 3D модель с рельефом и границами
    """
    print("Creating 3D mesh with boundaries...")
    
    # Создаем базовый меш рельефа
    terrain_mesh_data = create_flat_bottom_mesh(lon_grid, lat_grid, elevation)
    
    # Проверяем формат данных границ
    if isinstance(boundary_data, tuple) and len(boundary_data) == 2:
        boundary_points, boundary_faces = boundary_data
    else:
        print("Warning: Unknown boundary data format, skipping boundaries")
        boundary_points, boundary_faces = np.array([]), np.array([])
    
    if USE_PYVISTA:
        import pyvista as pv
        
        # Создаем меш рельефа
        terrain_vertices = terrain_mesh_data['vertices']
        terrain_faces = terrain_mesh_data['faces']
        
        # Конвертируем грани в формат PyVista
        pv_terrain_faces = []
        for face in terrain_faces:
            pv_terrain_faces.extend([3] + face.tolist())
        
        terrain_mesh = pv.PolyData(terrain_vertices, pv_terrain_faces)
        
        # Создаем меш границ, если есть границы
        if len(boundary_points) > 0:
            pv_boundary_faces = []
            for face in boundary_faces:
                pv_boundary_faces.extend([3] + face.tolist())
            
            boundary_mesh = pv.PolyData(boundary_points, pv_boundary_faces)
            
            # Объединяем меши
            combined_mesh = terrain_mesh + boundary_mesh
            print(f"Combined mesh: {combined_mesh.n_points} points, {combined_mesh.n_faces} faces")
            return combined_mesh
        else:
            print("No boundaries to add, returning terrain mesh only")
            return terrain_mesh
    
    else:
        # Fallback для trimesh
        if len(boundary_points) > 0:
            # Объединяем точки и грани
            all_vertices = np.vstack([terrain_mesh_data['vertices'], boundary_points])
            
            # Сдвигаем индексы граней границ
            boundary_faces_shifted = boundary_faces + len(terrain_mesh_data['vertices'])
            all_faces = np.vstack([terrain_mesh_data['faces'], boundary_faces_shifted])
            
            return {
                'vertices': all_vertices,
                'faces': all_faces
            }
        else:
            return terrain_mesh_data


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


def _calculate_wall_direction(coords_mm, i):
    """
    Вычисляет направление стены для точки i
    
    Возвращает:
    - px, py: смещение для ширины стены
    """
    n_points = len(coords_mm)
    
    # Находим направления к соседним точкам
    prev_i = (i - 1) % n_points
    next_i = (i + 1) % n_points
    
    x, y = coords_mm[i]
    x_prev, y_prev = coords_mm[prev_i]
    x_next, y_next = coords_mm[next_i]
    
    # Вычисляем направления
    dx1 = x - x_prev
    dy1 = y - y_prev
    dx2 = x_next - x
    dy2 = y_next - y
    
    # Нормализуем
    len1 = np.sqrt(dx1*dx1 + dy1*dy1)
    len2 = np.sqrt(dx2*dx2 + dy2*dy2)
    
    if len1 > 0.01:
        dx1, dy1 = dx1/len1, dy1/len1
    if len2 > 0.01:
        dx2, dy2 = dx2/len2, dy2/len2
    
    # Средний перпендикуляр
    avg_dx = (dx1 + dx2) / 2
    avg_dy = (dy1 + dy2) / 2
    avg_len = np.sqrt(avg_dx*avg_dx + avg_dy*avg_dy)
    
    if avg_len > 0.01:
        avg_dx, avg_dy = avg_dx/avg_len, avg_dy/avg_len
    
    return avg_dx, avg_dy


def _create_wall_points(coords_mm, base_elevations, height, width):
    """
    Создает точки для стены
    
    Возвращает:
    - all_points: массив всех точек стены
    """
    n_points = len(coords_mm)
    all_points = []
    
    for i in range(n_points):
        x, y = coords_mm[i]
        base_z = base_elevations[i]
        
        # Вычисляем направление стены
        avg_dx, avg_dy = _calculate_wall_direction(coords_mm, i)
        
        # Перпендикуляр для ширины (направлен внутрь полигона)
        px = -avg_dy * width / 2
        py = avg_dx * width / 2
        
        # Добавляем 4 точки для этой позиции
        all_points.extend([
            [x + px, y + py, base_z],              # внутренняя нижняя
            [x + px, y + py, base_z + height],     # внутренняя верхняя
            [x - px, y - py, base_z],              # внешняя нижняя
            [x - px, y - py, base_z + height]      # внешняя верхняя
        ])
    
    return np.array(all_points)


def _create_wall_faces(n_points):
    """
    Создает грани для стены
    
    Возвращает:
    - faces: массив граней
    """
    faces = []
    
    for i in range(n_points):
        next_i = (i + 1) % n_points
        
        # Индексы текущих точек
        curr_inner_low = i * 4
        curr_inner_high = i * 4 + 1
        curr_outer_low = i * 4 + 2
        curr_outer_high = i * 4 + 3
        
        # Индексы следующих точек
        next_inner_low = next_i * 4
        next_inner_high = next_i * 4 + 1
        next_outer_low = next_i * 4 + 2
        next_outer_high = next_i * 4 + 3
        
        # Внутренняя вертикальная грань
        faces.extend([
            [curr_inner_low, next_inner_low, curr_inner_high],
            [curr_inner_high, next_inner_low, next_inner_high]
        ])
        
        # Внешняя вертикальная грань
        faces.extend([
            [curr_outer_low, curr_outer_high, next_outer_low],
            [curr_outer_high, next_outer_high, next_outer_low]
        ])
        
        # Верхняя горизонтальная грань
        faces.extend([
            [curr_inner_high, next_inner_high, curr_outer_high],
            [next_inner_high, next_outer_high, curr_outer_high]
        ])
        
        # Нижняя горизонтальная грань
        faces.extend([
            [curr_inner_low, curr_outer_low, next_inner_low],
            [next_inner_low, curr_outer_low, next_outer_low]
        ])
    
    return np.array(faces)


def create_polygon_wall(coords_mm, base_elevations, height, width):
    """
    Создает непрерывную стену из замкнутого полигона
    
    Параметры:
    - coords_mm: список координат в мм [(x, y), ...]
    - base_elevations: высоты рельефа для каждой точки
    - height: высота стены в мм
    - width: ширина стены в мм
    
    Возвращает:
    - points: массив точек
    - faces: массив граней
    """
    if len(coords_mm) < 3:
        return np.array([]), np.array([])
    
    # Убираем дублирующуюся последнюю точку если она есть
    if len(coords_mm) > 3 and coords_mm[0] == coords_mm[-1]:
        coords_mm = coords_mm[:-1]
        base_elevations = base_elevations[:-1]
    
    n_points = len(coords_mm)
    if n_points < 3:
        return np.array([]), np.array([])
    
    # Создаем точки и грани
    all_points = _create_wall_points(coords_mm, base_elevations, height, width)
    faces = _create_wall_faces(n_points)
    
    return all_points, faces


def create_3d_mesh_with_boundaries_and_waves(lon_grid, lat_grid, elevation, boundary_data, wave_lines):
    """
    Создает 3D модель с рельефом, границами и волновыми линиями
    
    Параметры:
    - lon_grid, lat_grid: координатные сетки
    - elevation: высоты рельефа
    - boundary_data: данные границ (точки и грани)
    - wave_lines: список волновых линий
    
    Возвращает:
    - объединенная 3D модель с рельефом, границами и волнами
    """
    print("Creating 3D mesh with boundaries and wave lines...")
    
    # Создаем базовый меш рельефа
    terrain_mesh_data = create_flat_bottom_mesh(lon_grid, lat_grid, elevation)
    
    # Создаем геометрию волновых линий
    wave_mesh_data = create_wave_lines_mesh(wave_lines)
    
    # Проверяем формат данных границ
    if isinstance(boundary_data, tuple) and len(boundary_data) == 2:
        boundary_points, boundary_faces = boundary_data
    else:
        print("Warning: Unknown boundary data format, skipping boundaries")
        boundary_points, boundary_faces = np.array([]), np.array([])
    
    if USE_PYVISTA:
        import pyvista as pv
        
        # Создаем меш рельефа
        terrain_vertices = terrain_mesh_data['vertices']
        terrain_faces = terrain_mesh_data['faces']
        
        # Конвертируем грани в формат PyVista
        pv_terrain_faces = []
        for face in terrain_faces:
            pv_terrain_faces.extend([3] + face.tolist())
        
        terrain_mesh = pv.PolyData(terrain_vertices, pv_terrain_faces)
        combined_mesh = terrain_mesh
        
        # Добавляем границы, если есть
        if len(boundary_points) > 0:
            pv_boundary_faces = []
            for face in boundary_faces:
                pv_boundary_faces.extend([3] + face.tolist())
            
            boundary_mesh = pv.PolyData(boundary_points, pv_boundary_faces)
            combined_mesh = combined_mesh + boundary_mesh
            print(f"Added boundaries: {len(boundary_points)} points, {len(boundary_faces)} faces")
        
        # Добавляем волновые линии, если есть
        if wave_mesh_data and len(wave_mesh_data['vertices']) > 0:
            wave_vertices = wave_mesh_data['vertices']
            wave_faces = wave_mesh_data['faces']
            
            pv_wave_faces = []
            for face in wave_faces:
                pv_wave_faces.extend([3] + face.tolist())
            
            wave_mesh = pv.PolyData(wave_vertices, pv_wave_faces)
            combined_mesh = combined_mesh + wave_mesh
            print(f"Added wave lines: {len(wave_vertices)} points, {len(wave_faces)} faces")
        
        print(f"Final combined mesh: {combined_mesh.n_points} points, {combined_mesh.n_faces} faces")
        return combined_mesh
    
    else:
        # Fallback для trimesh
        print("Using trimesh fallback (wave lines not fully supported)")
        return create_3d_mesh_with_boundaries(lon_grid, lat_grid, elevation, boundary_data)


def create_wave_lines_mesh(wave_lines):
    """
    Создает mesh для волновых линий
    
    Параметры:
    - wave_lines: список волновых линий с параметрами
    
    Возвращает:
    - словарь с vertices и faces для волновых линий
    """
    if not wave_lines:
        return {'vertices': np.array([]), 'faces': np.array([])}
    
    print(f"Creating mesh for {len(wave_lines)} wave lines...")
    
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    for wave_line in wave_lines:
        points = wave_line['points']
        height = wave_line['height']
        width = wave_line.get('width', 2.5)  # мм (используем новое значение по умолчанию)
        
        if len(points) < 2:
            continue
        
        # Создаем прямоугольные сегменты для каждой линии
        line_vertices = []
        line_faces = []
        
        # Конвертируем ширину из мм в координаты
        # Приблизительный масштаб: карта 400мм на ~70 градусов долготы
        map_width_mm = 400.0
        map_width_deg = 70.0  # приблизительно
        mm_to_deg = map_width_deg / map_width_mm
        width_coord = width * mm_to_deg
        
        print(f"Creating wave line: width={width}mm -> {width_coord:.6f} degrees")
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            
            # Направление линии
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = np.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Нормализованный вектор направления
                dx /= length
                dy /= length
                
                # Перпендикулярный вектор для ширины
                px = -dy * width_coord / 2
                py = dx * width_coord / 2
                
                # Четыре угла прямоугольника на уровне terrain + height
                v1 = [p1[0] + px, p1[1] + py, height]
                v2 = [p1[0] - px, p1[1] - py, height]
                v3 = [p2[0] - px, p2[1] - py, height]
                v4 = [p2[0] + px, p2[1] + py, height]
                
                # Четыре угла на уровне terrain (основание)
                v5 = [p1[0] + px, p1[1] + py, 0]
                v6 = [p1[0] - px, p1[1] - py, 0]
                v7 = [p2[0] - px, p2[1] - py, 0]
                v8 = [p2[0] + px, p2[1] + py, 0]
                
                # Добавляем вершины
                start_idx = len(line_vertices)
                line_vertices.extend([v1, v2, v3, v4, v5, v6, v7, v8])
                
                # Добавляем грани (по 2 треугольника на каждую сторону)
                # Верхняя грань
                line_faces.extend([
                    [start_idx, start_idx+1, start_idx+2],
                    [start_idx, start_idx+2, start_idx+3]
                ])
                # Нижняя грань
                line_faces.extend([
                    [start_idx+4, start_idx+6, start_idx+5],
                    [start_idx+4, start_idx+7, start_idx+6]
                ])
                # Боковые грани
                line_faces.extend([
                    [start_idx, start_idx+4, start_idx+5],
                    [start_idx, start_idx+5, start_idx+1],
                    [start_idx+1, start_idx+5, start_idx+6],
                    [start_idx+1, start_idx+6, start_idx+2],
                    [start_idx+2, start_idx+6, start_idx+7],
                    [start_idx+2, start_idx+7, start_idx+3],
                    [start_idx+3, start_idx+7, start_idx+4],
                    [start_idx+3, start_idx+4, start_idx]
                ])
        
        # Добавляем к общему списку с корректировкой индексов
        if line_vertices:
            all_vertices.extend(line_vertices)
            for face in line_faces:
                all_faces.append([face[0] + vertex_offset, face[1] + vertex_offset, face[2] + vertex_offset])
            vertex_offset += len(line_vertices)
    
    print(f"Created wave mesh: {len(all_vertices)} vertices, {len(all_faces)} faces")
    
    return {
        'vertices': np.array(all_vertices) if all_vertices else np.array([]),
        'faces': np.array(all_faces) if all_faces else np.array([])
    }
