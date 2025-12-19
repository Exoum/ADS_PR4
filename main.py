#!/usr/bin/env python3
"""Основной файл для запуска всего приложения с визуализацией."""

import subprocess
import sys
import os

def run_map_search():
    """Запустить основное приложение для поиска объектов."""
    print("Запуск основного приложения для поиска объектов...")
    try:
        subprocess.run([sys.executable, "map_search.py"], check=True)
        print("Основное приложение завершено.")
    except subprocess.CalledProcessError:
        print("Ошибка при запуске основного приложения.")
        return False
    return True

def run_visualization():
    """Запустить визуализацию реальной карты."""
    print("Создание визуализации реальной карты Красноярска...")
    try:
        subprocess.run([sys.executable, "real_map_visual.py"], check=True)
        print("Визуализация завершена.")
        
        # Открыть сгенерированную карту в браузере
        if os.path.exists("krasnoyarsk_map.html"):
            print("Открытие интерактивной карты в браузере...")
            os.startfile("krasnoyarsk_map.html")
        else:
            print("Файл карты не найден.")
    except subprocess.CalledProcessError:
        print("Ошибка при создании визуализации.")
        return False
    return True

def run_tests():
    """Запустить тесты для проверки работы k-d дерева."""
    print("Запуск тестов...")
    try:
        result = subprocess.run([sys.executable, "test_kd_tree.py"], 
                              capture_output=True, text=True, check=True)
        print("Тесты пройдены успешно.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Ошибка при запуске тестов.")
        print(e.stdout)
        print(e.stderr)
        return False
    return True

def main():
    """Главная функция для запуска всего приложения."""
    print("=" * 50)
    print("Приложение для поиска ближайших объектов на карте")
    print("с использованием k-d деревьев и реальных данных Красноярска")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Запустить основное приложение")
        print("2. Создать визуализацию реальной карты")
        print("3. Запустить тесты")
        print("4. Запустить все (приложение + визуализация)")
        print("5. Выход")
        
        choice = input("\nВведите номер действия (1-5): ").strip()
        
        if choice == "1":
            run_map_search()
        elif choice == "2":
            run_visualization()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            print("Запуск всего приложения...")
            # Сначала запускаем основное приложение
            if run_map_search():
                # Затем создаем визуализацию
                run_visualization()
        elif choice == "5":
            print("Спасибо за использование приложения!")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 5.")

if __name__ == "__main__":
    main()