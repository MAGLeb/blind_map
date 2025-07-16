"""
Constants for tactile map generation
"""

# Параметры карты для 3D-печати
CARD_WIDTH_MM = 148  # A5 ширина
CARD_HEIGHT_MM = 210  # A5 высота
GRID_COLS = 3
GRID_ROWS = 2
FULL_WIDTH_MM = CARD_WIDTH_MM * GRID_COLS  # 444 мм
FULL_HEIGHT_MM = CARD_HEIGHT_MM * GRID_ROWS  # 420 мм
BASE_THICKNESS_MM = 3.0  # Толщина основания (увеличена для стабильности)

# Тактильные параметры для слепых пользователей (основаны на исследованиях осязания)
MAX_ELEVATION_MM = 6.0  # Максимальная высота рельефа (оптимально для осязания)
MIN_TACTILE_DIFFERENCE_MM = 0.8  # Минимальная разница высот для различения пальцем
BOUNDARY_HEIGHT_MM = 0.6  # Высота границ стран ПОВЕРХ рельефа (тонкие, но различимые)
BOUNDARY_WIDTH_MM = 1.5  # Ширина границ стран (оптимально для осязания)
WAVE_HEIGHT_MM = 0.4  # Высота волн на воде (тонкая текстура)
WAVE_SPACING_MM = 5.0  # Расстояние между волнами (комфортно для пальца)

# Тактильные рекомендации:
# - Минимальная различимая высота: 0.8-1.0 мм
# - Оптимальная высота для рельефа: 3-6 мм
# - Максимальная комфортная высота: 8-10 мм
# - Минимальная ширина линий: 1-2 мм
# - Оптимальное расстояние между элементами: 3-5 мм

# Try to import pyvista, fallback to trimesh if not available
try:
    import pyvista as pv
    USE_PYVISTA = True
except ImportError:
    try:
        import trimesh
        USE_PYVISTA = False
    except ImportError:
        print("Warning: Neither pyvista nor trimesh is available. STL export will be limited.")
        USE_PYVISTA = None
