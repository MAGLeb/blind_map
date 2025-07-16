#!/usr/bin/env python3
"""
Правильная последовательность запуска скриптов для создания тактильной карты
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Проверяет существование файла"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - НЕ НАЙДЕН")
        return False

def run_pipeline():
    """Запускает полный пайплайн создания карты"""
    
    print("🗺️  ПАЙПЛАЙН СОЗДАНИЯ ТАКТИЛЬНОЙ КАРТЫ")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    
    # Последовательность выполнения
    steps = [
        {
            "step": 1,
            "name": "Скачивание GeoJSON файлов стран",
            "script": "download_geojson.py",
            "description": "Скачивает границы стран из OpenStreetMap",
            "input_files": [],
            "output_files": ["data/countries/*.geojson", "data/downloaded_files.json"],
            "optional": False
        },
        {
            "step": 2,
            "name": "Объединение GeoJSON файлов",
            "script": "merge_countries_geojson.py", 
            "description": "Объединяет все страны в один файл",
            "input_files": ["data/countries/*.geojson"],
            "output_files": ["data/output/merged_countries.geojson"],
            "optional": False
        },
        {
            "step": 3,
            "name": "Скачивание данных высот",
            "script": "load_height.py",
            "description": "Скачивает данные рельефа ETOPO1",
            "input_files": [],
            "output_files": ["data/ETOPO1_Bed_g_gmt4.grd"],
            "optional": False
        },
        {
            "step": 4,
            "name": "Создание водных областей",
            "script": "water_processor.py",
            "description": "Создает водные области для визуализации",
            "input_files": ["data/output/merged_countries.geojson"],
            "output_files": ["data/output/water_areas.geojson"],
            "optional": True
        },
        {
            "step": 5,
            "name": "Создание 2D превью карты",
            "script": "create_final_map.py",
            "description": "Создает 2D изображение карты для предварительного просмотра",
            "input_files": ["data/output/merged_countries.geojson"],
            "output_files": ["data/previews/tactile_map.png"],
            "optional": True
        },
        {
            "step": 6,
            "name": "Создание 3D тактильной карты",
            "script": "create_3d_map.py",
            "description": "Создает 3D STL файл для печати",
            "input_files": ["data/output/merged_countries.geojson", "data/ETOPO1_Bed_g_gmt4.grd"],
            "output_files": ["data/output/terrain_model.stl"],
            "optional": False
        }
    ]
    
    print("\n📋 ПОСЛЕДОВАТЕЛЬНОСТЬ ВЫПОЛНЕНИЯ:")
    print("-" * 60)
    
    for step in steps:
        status = "⭐ ОБЯЗАТЕЛЬНО" if not step["optional"] else "🔹 ОПЦИОНАЛЬНО"
        print(f"\n{step['step']}. {step['name']} {status}")
        print(f"   Скрипт: python core/{step['script']}")
        print(f"   Описание: {step['description']}")
        
        if step["input_files"]:
            print(f"   Входные файлы: {', '.join(step['input_files'])}")
        if step["output_files"]:
            print(f"   Выходные файлы: {', '.join(step['output_files'])}")
    
    print("\n" + "=" * 60)
    print("📁 ПРОВЕРКА СУЩЕСТВУЮЩИХ ФАЙЛОВ:")
    print("-" * 60)
    
    # Проверяем ключевые файлы
    key_files = [
        ("data/countries/", "Папка со странами"),
        ("data/output/merged_countries.geojson", "Объединенные страны"),
        ("data/ETOPO1_Bed_g_gmt4.grd", "Данные высот"),
        ("data/output/water_areas.geojson", "Водные области (опционально)"),
        ("data/previews/tactile_map.png", "2D превью (опционально)"),
        ("data/output/terrain_model.stl", "3D модель")
    ]
    
    for file_path, description in key_files:
        full_path = base_path / file_path
        check_file_exists(full_path, description)
    
    print("\n" + "=" * 60)
    print("🚀 КОМАНДЫ ДЛЯ ЗАПУСКА:")
    print("-" * 60)
    
    commands = [
        "# 1. Скачать границы стран",
        "python core/download_geojson.py",
        "",
        "# 2. Объединить страны в один файл", 
        "python core/merge_countries_geojson.py",
        "",
        "# 3. Скачать данные высот",
        "python core/load_height.py",
        "",
        "# 4. (Опционально) Создать водные области",
        "python core/water_processor.py",
        "",
        "# 5. (Опционально) Создать 2D превью",
        "python core/create_final_map.py",
        "",
        "# 6. Создать 3D тактильную карту",
        "python core/create_3d_map.py"
    ]
    
    for cmd in commands:
        print(cmd)
    
    print("\n" + "=" * 60)
    print("💡 СОВЕТЫ:")
    print("-" * 60)
    print("• Шаги 1-3 и 6 - обязательны для создания 3D карты")
    print("• Шаги 4-5 - опциональны, нужны для визуализации и отладки")
    print("• Если файлы уже существуют, соответствующие шаги можно пропустить")
    print("• Для изменения области карты - отредактируйте MAP_BOUNDS в core/config.py")
    print("• 3D карта будет сохранена в data/output/terrain_model.stl")

if __name__ == "__main__":
    run_pipeline()
