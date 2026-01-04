"""
Constants for tactile map generation.

Спецификация тактильной карты для незрячих.
"""

# === РАЗМЕРЫ КАРТЫ ===
CARD_WIDTH_MM = 200    # Ширина одной карточки
CARD_HEIGHT_MM = 160   # Высота одной карточки
GRID_COLS = 2          # Колонок в сетке
GRID_ROWS = 2          # Рядов в сетке
FULL_WIDTH_MM = CARD_WIDTH_MM * GRID_COLS   # 400 мм
FULL_HEIGHT_MM = CARD_HEIGHT_MM * GRID_ROWS  # 320 мм
BASE_THICKNESS_MM = 6.0  # Толщина основания (увеличена для пазов)

# === ПАЗЛОВЫЕ СОЕДИНЕНИЯ ===
TAB_HEIGHT_MM = 3.0      # Высота выступа (по Z)
TAB_DEPTH_MM = 4.0       # Глубина выступа (насколько торчит)
TAB_WIDTH_MM = 8.0       # Ширина выступа
SLOT_CLEARANCE_MM = 0.5  # Зазор для вхождения tab в slot

# === ТАКТИЛЬНЫЕ ПАРАМЕТРЫ ===

# Границы стран — ГЛАВНЫЙ элемент, самый высокий
BOUNDARY_HEIGHT_MM = 5.0   # Высота границ (фиксированная, выше всего)
BOUNDARY_WIDTH_MM = 2.5    # Ширина границ

# Рельеф — фоновый элемент
MAX_ELEVATION_MM = 10.0    # Максимальная высота рельефа (горы)
MIN_ELEVATION_MM = 0.0     # Минимальная высота (низменности, уровень моря)

# Вода — волновой паттерн
WAVE_HEIGHT_MM = 2.0       # Высота волны
WAVE_INTERVAL_MM = 4.0     # Расстояние между волнами
WAVE_DIRECTION = "horizontal"  # Направление волн (восток-запад)

# Столицы — бугорки
CAPITAL_HEIGHT_MM = 2.0    # Высота бугорка столицы
CAPITAL_DIAMETER_MM = 3.0  # Диаметр бугорка

# Номера стран
NUMBER_HEIGHT_MM = 1.5     # Высота выпуклых цифр

# === ИЕРАРХИЯ ВЫСОТ ===
# 0 мм   — уровень моря, низменности
# 0.8 мм — волны воды
# 3 мм   — максимальный рельеф
# 5 мм   — границы стран (всегда выше)

# === ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ ===
MIN_TACTILE_DIFFERENCE_MM = 0.5  # Минимальная различимая разница высот
PROGRESS_REPORT_INTERVAL = 10
MIN_BOUNDARY_POINTS = 50

# === БИБЛИОТЕКИ ===
try:
    import pyvista as pv
    USE_PYVISTA = True
except ImportError:
    try:
        import trimesh
        USE_PYVISTA = False
    except ImportError:
        print("Warning: Neither pyvista nor trimesh available.")
        USE_PYVISTA = None
