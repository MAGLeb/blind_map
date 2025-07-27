import os
import numpy as np
import matplotlib.pyplot as plt
import requests
import xarray as xr
from scipy.interpolate import griddata
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# =============================================================================
# НАСТРОЙКИ ОБЛАСТИ
# =============================================================================

# Координаты области для отображения
# Формат: (min_lon, min_lat, max_lon, max_lat)
# Ваша область:
# - долгота: от 5 до 70 градусов восточной долготы
# - широта: от 12 до 55 градусов северной широты
TARGET_BBOX = (5.0, 12.0, 70.0, 55.0)

# Папка для сохранения файлов
DATA_FOLDER = "./data/"

# =============================================================================

def download_file(url, dest_folder):
    """
    Downloads a file from a given URL to a destination folder.
    
    Args:
        url (str): URL of the file to download
        dest_folder (str): Destination folder to save the downloaded file
        
    Returns:
        str: Path to the downloaded file
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # Create the folder if it doesn't exist
    
    filename = os.path.basename(url)
    file_path = os.path.join(dest_folder, filename)
    
    # Stream the download to handle large files
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # Check for HTTP errors
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    
    return file_path

def extract_zip(zip_path, extract_to):
    """
    Extracts a ZIP file to a specified directory.
    
    Args:
        zip_path (str): Path to the ZIP file
        extract_to (str): Directory to extract the contents to
    """
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def download_etopo1_data(data_folder=DATA_FOLDER):
    """
    Скачивает глобальную модель рельефа ETOPO1.
    
    Args:
        data_folder (str): Папка для сохранения файлов
        
    Returns:
        str: Путь к скачанному файлу
    """
    # URL для ETOPO1 в формате NetCDF (разрешение 1 arc-minute)
    etopo1_url = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/ETOPO1_Bed_g_gmt4.grd.gz"
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    etopo1_gz_path = os.path.join(data_folder, "ETOPO1_Bed_g_gmt4.grd.gz")
    etopo1_path = os.path.join(data_folder, "ETOPO1_Bed_g_gmt4.grd")
    
    # Проверяем, есть ли уже распакованный файл
    if os.path.exists(etopo1_path):
        print(f"Файл ETOPO1 уже существует: {etopo1_path}")
        return etopo1_path
    
    # Проверяем, есть ли архив
    if not os.path.exists(etopo1_gz_path):
        print("Скачиваем ETOPO1 (это может занять несколько минут)...")
        try:
            download_file(etopo1_url, data_folder)
            print("Скачивание завершено.")
        except Exception as e:
            print(f"Ошибка при скачивании ETOPO1: {e}")
            return None
    
    # Распаковываем архив
    print("Распаковываем архив ETOPO1...")
    try:
        import gzip
        with gzip.open(etopo1_gz_path, 'rb') as f_in:
            with open(etopo1_path, 'wb') as f_out:
                f_out.write(f_in.read())
        print("Распаковка завершена.")
    except Exception as e:
        print(f"Ошибка при распаковке ETOPO1: {e}")
        return None
    
    return etopo1_path

def load_and_crop_etopo1(etopo1_path, bbox):
    """
    Загружает ETOPO1 и обрезает по заданным границам.
    
    Args:
        etopo1_path (str): Путь к файлу ETOPO1
        bbox (tuple): Границы области (min_lon, min_lat, max_lon, max_lat)
        
    Returns:
        xarray.Dataset: Обрезанные данные высот
    """
    print(f"Загружаем ETOPO1 из {etopo1_path}...")
    
    try:
        # Загружаем данные с помощью xarray
        ds = xr.open_dataset(etopo1_path, decode_times=False)
        
        # Получаем координаты области
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Обрезаем данные по заданным границам
        print(f"Обрезаем данные по границам: {min_lon}°-{max_lon}°E, {min_lat}°-{max_lat}°N")
        
        # Определяем имена переменных в зависимости от формата файла
        if 'x' in ds.dims and 'y' in ds.dims:
            lon_var, lat_var = 'x', 'y'
        elif 'lon' in ds.dims and 'lat' in ds.dims:
            lon_var, lat_var = 'lon', 'lat'
        else:
            # Пробуем найти переменные координат
            coord_vars = list(ds.coords.keys())
            print(f"Доступные координаты: {coord_vars}")
            lon_var = coord_vars[0] if len(coord_vars) > 0 else 'x'
            lat_var = coord_vars[1] if len(coord_vars) > 1 else 'y'
        
        # Обрезаем данные
        ds_cropped = ds.sel(
            {lon_var: slice(min_lon, max_lon),
             lat_var: slice(min_lat, max_lat)}
        )
        
        print(f"Размер обрезанных данных: {ds_cropped.dims}")
        return ds_cropped
        
    except Exception as e:
        print(f"Ошибка при загрузке ETOPO1: {e}")
        return None

def create_elevation_map_from_etopo1(ds, bbox, output_image="elevation_map.png"):
    """
    Создаёт карту высот из данных ETOPO1.
    
    Args:
        ds (xarray.Dataset): Данные высот
        bbox (tuple): Границы области (min_lon, min_lat, max_lon, max_lat)
        output_image (str): Путь для сохранения изображения
    """
    print("Создаём карту высот...")
    
    try:
        # Определяем имена переменных
        data_vars = list(ds.data_vars.keys())
        print(f"Доступные переменные данных: {data_vars}")
        
        # Выбираем переменную высот (обычно z, elevation, или первая переменная)
        if 'z' in data_vars:
            elev_var = 'z'
        elif 'elevation' in data_vars:
            elev_var = 'elevation'
        else:
            elev_var = data_vars[0]
        
        elevation_data = ds[elev_var]
        
        # Получаем координаты
        if 'x' in ds.dims and 'y' in ds.dims:
            lon_coord, lat_coord = ds['x'], ds['y']
        elif 'lon' in ds.dims and 'lat' in ds.dims:
            lon_coord, lat_coord = ds['lon'], ds['lat']
        else:
            coord_names = list(ds.coords.keys())
            lon_coord = ds[coord_names[0]]
            lat_coord = ds[coord_names[1]]
        
        # Создаём фигуру
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Отображаем карту высот
        im = ax.imshow(elevation_data, 
                       extent=[lon_coord.min(), lon_coord.max(), 
                              lat_coord.min(), lat_coord.max()],
                       cmap='terrain',
                       origin='lower',
                       interpolation='bilinear',
                       aspect='auto')
        
        # Добавляем цветовую шкалу
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Высота (м)', rotation=270, labelpad=20)
        
        # Настраиваем оси
        ax.set_xlabel('Долгота (°)')
        ax.set_ylabel('Широта (°)')
        
        # Заголовок с координатными границами
        min_lon, min_lat, max_lon, max_lat = bbox
        title = f'Карта высот (ETOPO1)\nГраницы: {min_lon:.1f}° - {max_lon:.1f}° E, {min_lat:.1f}° - {max_lat:.1f}° N'
        ax.set_title(title, fontsize=14, pad=20)
        
        # Добавляем сетку
        ax.grid(True, alpha=0.3)
        
        # Статистика высот
        elevation_array = elevation_data.values
        valid_elevation = elevation_array[~np.isnan(elevation_array)]
        
        if len(valid_elevation) > 0:
            min_elev = np.min(valid_elevation)
            max_elev = np.max(valid_elevation)
            mean_elev = np.mean(valid_elevation)
            
            stats_text = f'Мин: {min_elev:.0f}м\nМакс: {max_elev:.0f}м\nСред: {mean_elev:.0f}м'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Устанавливаем разумные пределы осей
        ax.set_xlim(min_lon, max_lon)
        ax.set_ylim(min_lat, max_lat)
        
        plt.tight_layout()
        
        # Сохраняем изображение
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        print(f"Карта высот сохранена в файл: {output_image}")
        
        # Показываем карту
        plt.show()
        
    except Exception as e:
        print(f"Ошибка при создании карты высот: {e}")

def main():
    """
    Основная функция для создания карты высот.
    """
    try:
        print("=== Создание карты высот из ETOPO1 ===")
        print(f"Область: {TARGET_BBOX[1]:.1f}°-{TARGET_BBOX[3]:.1f}°N, {TARGET_BBOX[0]:.1f}°-{TARGET_BBOX[2]:.1f}°E")
        
        # Скачиваем ETOPO1
        etopo1_path = download_etopo1_data()
        
        if etopo1_path is None:
            print("Не удалось скачать ETOPO1")
            return
        
        # Загружаем и обрезаем данные
        ds = load_and_crop_etopo1(etopo1_path, TARGET_BBOX)
        
        if ds is None:
            print("Не удалось загрузить данные")
            return
        
        # Создаём карту высот
        create_elevation_map_from_etopo1(ds, TARGET_BBOX)
        
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")

if __name__ == "__main__":
    main()
