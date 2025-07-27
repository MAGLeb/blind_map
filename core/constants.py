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
BOUNDARY_HEIGHT_MM = 1.0  # Высота границ стран ПОВЕРХ рельефа (увеличена для четкого различения)
BOUNDARY_WIDTH_MM = 0.2  # Ширина границ стран (очень узкие для четкого различения от рельефа)
WAVE_HEIGHT_MM = 0.4  # Высота волн на воде (тонкая текстура)
WAVE_SPACING_MM = 5.0  # Расстояние между волнами (комфортно для пальца)

# Параметры производительности
PROGRESS_REPORT_INTERVAL = 10  # Показывать прогресс каждые N стран
MIN_BOUNDARY_POINTS = 50  # Минимальное количество точек на сегмент границы (увеличено для детализации)

# Тактильные рекомендации:
# - Минимальная различимая высота: 0.8-1.0 мм
# - Оптимальная высота для рельефа: 3-6 мм
# - Максимальная комфортная высота: 8-10 мм
# - Границы: очень узкие (0.2 мм) но высокие (3.0 мм) для четкого различения от рельефа
# - Минимальная ширина для 3D печати: 0.2 мм
# - Оптимальное расстояние между элементами: 3-5 мм
# - Границы должны быть прямоугольными, а не квадратными областями

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
