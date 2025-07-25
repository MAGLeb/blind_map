
# Blind Map - Тактильная карта для незрячих

Проект создания 3D тактильной карты для незрячих пользователей с использованием данных OpenStreetMap и ETOPO1.

## Последовательность запуска скриптов

### 1. download_geojson.py
**Описание**: Скачивает границы стран из OpenStreetMap  
**Входные данные**: -  
**Выходные данные**: 
- `data/countries/*.geojson` - файлы границ стран
- `data/downloaded_files.json` - список скачанных файлов

```bash
python core/download_geojson.py
```

### 2. merge_countries_geojson.py
**Описание**: Объединяет все файлы стран в один GeoJSON  
**Входные данные**: 
- `data/countries/*.geojson` - файлы границ стран
- `data/downloaded_files.json` - список файлов  
**Выходные данные**: 
- `data/output/merged_countries.geojson` - объединенный файл всех стран

```bash
python core/merge_countries_geojson.py
```

### 3. load_height.py
**Описание**: Скачивает данные высот ETOPO1  
**Входные данные**: -  
**Выходные данные**: 
- `data/ETOPO1_Bed_g_gmt4.grd` - данные рельефа
- `data/previews/elevation_map.png` - превью карты высот

```bash
python core/load_height.py
```

### 4. water_processor.py (опционально)
**Описание**: Создает водные области для визуализации  
**Входные данные**: 
- `data/output/merged_countries.geojson` - объединенные страны  
**Выходные данные**: 
- `data/output/water_areas.geojson` - водные области

```bash
python core/water_processor.py
```

### 5. create_final_map.py (опционально)
**Описание**: Создает 2D превью карты  
**Входные данные**: 
- `data/output/merged_countries.geojson` - объединенные страны
- `data/output/water_areas.geojson` - водные области (опционально)  
**Выходные данные**: 
- `data/previews/tactile_map.png` - 2D превью карты

```bash
python core/create_final_map.py
```

### 6. create_3d_map.py
**Описание**: Создает 3D STL файл для печати  
**Входные данные**: 
- `data/output/merged_countries.geojson` - объединенные страны
- `data/ETOPO1_Bed_g_gmt4.grd` - данные рельефа  
**Выходные данные**: 
- `data/output/terrain_model.stl` - 3D модель для печати

```bash
python core/create_3d_map.py
```

## Минимальная последовательность

Для создания 3D карты **обязательны** только шаги:
1. **download_geojson.py** - скачать границы стран
2. **merge_countries_geojson.py** - объединить страны  
3. **load_height.py** - скачать данные высот
4. **create_3d_map.py** - создать 3D модель

Шаги 4-5 (water_processor.py и create_final_map.py) **опциональны** и нужны только для визуализации и отладки.

## Структура файлов

```
blind_map/
├── core/
│   ├── tactile_map/          # Декомпозированные модули
│   ├── download_geojson.py   # 1. Скачивание границ стран
│   ├── merge_countries_geojson.py  # 2. Объединение стран
│   ├── load_height.py        # 3. Скачивание данных высот
│   ├── water_processor.py    # 4. Создание водных областей
│   ├── create_final_map.py   # 5. 2D превью карты
│   └── create_3d_map.py      # 6. 3D модель для печати
├── data/
│   ├── countries/            # Скачанные границы стран
│   ├── output/              # Обработанные данные
│   └── previews/            # Превью изображения
└── README.md
```

## Тактильные параметры

Проект оптимизирован для тактильного восприятия:
- Минимальная различимая высота: 0.8 мм
- Максимальная высота рельефа: 6.0 мм
- Высота границ стран: 0.6 мм НАД рельефом
- Ширина границ стран: 1.5 мм
- Размер карты: 444x420 мм (6 карточек A5)

## Настройки

Для изменения области карты отредактируйте `MAP_BOUNDS` в `core/config.py`:

```python
MAP_BOUNDS = (min_lon, min_lat, max_lon, max_lat)
```

## Требования

- Python 3.8+
- geopandas
- xarray
- matplotlib
- numpy
- scipy
- shapely
- pyvista или trimesh (для 3D экспорта)
- rasterio

5. **Создание тактильной легенды** 📋
   - Генерация таблицы соответствия (номер → страна/объект)
   - Образцы тактильных символов и текстур
   - Версия на языке Брайля

5. **Генерация SVG для печати** 📋
   - Экспорт каждой карточки в отдельный SVG
   - Различные стили линий: границы (толстые), реки (тонкие), побережье (пунктир)
   - Тактильные символы: столицы (точки), горы (треугольники), цифры
   - Оптимизация для рельефной печати

7. **Подготовка к 3D-печати** 📋
   - Конвертация SVG в 3D-модели (STL)
   - Добавление высоты для различных элементов
   - Оптимизация для термоформовки

---



## Текущий статус

### Выполнено ✅
1. **Получение и объединение данных**
   - [X] Автоматическая загрузка GeoJSON для стран
   - [X] Объединение границ стран в единый файл
   - [X] Базовая обработка водных объектов (береговая линия из границ стран)
   - [X] Создание предварительных карт для визуализации

### В процессе 🔄
2. **Настройка области карты**
   - [X] Фиксированные границы региона (Балканы + Кавказ + Ближний Восток)
   - [X] Базовые параметры отображения

### Планируется 📋
3. **Обогащение данных**
   - [ ] Размещение столиц городов
   - [ ] Интеграция данных о высотах и рельефе
   - [ ] Создание системы нумерации для объектов

4. **Разделение на карточки**
   - [ ] Вычисление bbox для каждой A5-карточки
   - [ ] Алгоритм разбиения карты на 6 частей (3×2)
   - [ ] Обеспечение совместимости границ между карточками

5. **Генерация SVG**
   - [ ] Экспорт границ стран в SVG
   - [ ] Различные стили линий (границы, реки, побережье)
   - [ ] Добавление символов (столицы, горы, цифры)
   - [ ] Оптимизация для тактильного восприятия

6. **Тактильная легенда**
   - [ ] Генерация таблицы соответствия (цифра → объект)
   - [ ] Образцы тактильных символов
   - [ ] Интеграция с Брайлем

7. **Подготовка файла к 3D печати** ✅
   - [X] Создание 3D-модели с оптимизированными тактильными параметрами
   - [X] Экспорт в STL-формат для 3D-печати
   - [X] Плоское дно для стабильной печати
   - [X] Сглаженный рельеф для комфортного тактильного восприятия

## Следующие шаги

1. Реализовать размещение столиц и нумерацию
2. Создать алгоритм разбиения на карточки
3. Генерация SVG и тактильной легенды

## Технические детали

### Охватываемый регион
- **Границы**: 5°-70° в.д., 12°-55° с.ш.
- **Включает**: Балканы, Малую Азию, Кавказ, Ближний Восток, часть Северной Африки
- **Страны**: ~80 стран (включая частично признанные территории)

### Параметры карты
- **Целевой масштаб**: 1:30 000 000
- **Формат карточек**: A5 (148×210 мм)
- **Количество карточек**: 6 (сетка 3×2)
- **Разрешение**: 150 DPI для предварительных изображений

### Размеры и масштаб
- **Размеры полной карты**: 444×420 мм
- **Размеры одной карточки**: 148×210 мм
- **Реальная территория**: 6034×4787 км
- **Масштаб**: 1:13,589,710 (ширина), 1:11,397,048 (высота)
- **1 мм на карте** = ~13.6 км в реальности

### Тактильные параметры для слепых пользователей
Основано на исследованиях тактильного восприятия:

**Высоты:**
- **Минимальная различимая высота**: 0.8 мм
- **Максимальная высота рельефа**: 6.0 мм (комфортно для исследования)
- **Высота границ стран**: 0.6 мм НАД рельефом (тонкие, но различимые)
- **Высота волн на воде**: 0.4 мм (тонкая текстура)
- **Толщина основания**: 3.0 мм (стабильная для печати)

**Расстояния:**
- **Расстояние между волнами**: 5.0 мм (комфортно для пальца)
- **Ширина границ**: 1.5 мм (оптимально для осязания)
- **Расстояние между элементами**: 3-5 мм

**Особенности:**
- **Количество различимых уровней высот**: 6-8
- **Квантизация высот**: для создания четких тактильных ступеней
- **Плавное сглаживание**: устраняет острые пики, сохраняет общие очертания
- **Плоское дно**: обеспечивает стабильность при печати и использовании

**Общие размеры модели:**
- **Полная модель**: 444×420×9 мм (включая основание)
- **Готова для 3D-печати**: STL-файл с закрытой геометрией
