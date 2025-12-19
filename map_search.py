"""Приложение для поиска ближайших объектов на карте с использованием k-d деревьев."""

import math
import random
import requests
import folium
import webbrowser
import os
from typing import List, Tuple, Optional
from tree import KDTree


class MapObject:
    """Класс, представляющий объект на карте."""
    
    def __init__(self, name: str, obj_type: str, x: float, y: float, address: str = ""):
        """
        Инициализация объекта на карте.
        
        Args:
            name: Название объекта
            obj_type: Тип объекта (магазин, кафе, больница и т.д.)
            x: Координата X (долгота)
            y: Координата Y (широта)
            address: Адрес объекта (опционально)
        """
        self.name = name
        self.type = obj_type
        self.x = x  # Долгота
        self.y = y  # Широта
        self.address = address
    
    def __repr__(self):
        """Строковое представление объекта."""
        return f"MapObject(name='{self.name}', type='{self.type}', x={self.x}, y={self.y}, address='{self.address}')"
    
    def get_coordinates(self) -> Tuple[float, float]:
        """Получить координаты объекта."""
        return (self.x, self.y)


class MapSearchApp:
    """Приложение для поиска ближайших объектов на карте."""
    
    def __init__(self):
        """Инициализация приложения."""
        self.objects: List[MapObject] = []
        self.kd_tree = KDTree()
        self.object_types = set()
        self.center_lat = 56.0091173
        self.center_lon = 92.8725860
        self.get_krasnoyarsk_center()
    
    def get_krasnoyarsk_center(self):
        """
        Получить координаты центра Красноярска.
        """
        try:
            headers = {'User-Agent': 'MapSearchApp/1.0'}
            url = "https://nominatim.openstreetmap.org/search?q=Красноярск&format=json"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data:
                self.center_lat = float(data[0]['lat'])
                self.center_lon = float(data[0]['lon'])
        except Exception as e:
            print(f"Не удалось получить координаты центра Красноярска: {e}")
    
    def add_object(self, obj: MapObject) -> None:
        """
        Добавить объект на карту.
        
        Args:
            obj: Объект для добавления
        """
        self.objects.append(obj)
        self.object_types.add(obj.type)
        # Добавляем объект в k-d дерево
        self.kd_tree.insert(obj.get_coordinates(), obj)
    
    def load_sample_data(self) -> None:
        """Загрузить тестовые данные."""
        sample_objects = [
            MapObject("Магазин продуктов", "магазин", 92.85, 56.01, "ул. Ленина, 10"),
            MapObject("Кафе 'Уютное'", "кафе", 92.88, 56.02, "ул. Советская, 15"),
            MapObject("Больница №1", "больница", 92.90, 56.03, "пр. Мира, 25"),
            MapObject("Кафе 'Романтика'", "кафе", 92.87, 56.04, "ул. Пушкина, 5"),
            MapObject("Супермаркет", "магазин", 92.89, 56.00, "ул. Кирова, 30"),
            MapObject("Аптека", "аптека", 92.88, 56.01, "ул. Гагарина, 12"),
            MapObject("Ресторан 'Любимый'", "ресторан", 92.86, 56.02, "ул. Лермонтова, 8"),
            MapObject("Парикмахерская", "салон красоты", 92.87, 56.03, "ул. Маяковского, 20")
        ]
        
        for obj in sample_objects:
            self.add_object(obj)
    
    def load_real_data(self, query: str = "Красноярск", obj_type: str = "магазин", limit: int = 20) -> None:
        """
        Загрузить реальные данные из OpenStreetMap.
        
        Args:
            query: Запрос для поиска города
            obj_type: Тип объектов для поиска
            limit: Максимальное количество объектов
        """
        # Получаем координаты центра Красноярска
        headers = {'User-Agent': 'MapSearchApp/1.0'}
        center_url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
        center_response = requests.get(center_url, headers=headers)
        center_data = center_response.json()
        
        if not center_data:
            print("Не удалось получить координаты города")
            return
        
        center_lat = float(center_data[0]['lat'])
        center_lon = float(center_data[0]['lon'])
        
        # Определяем границы области поиска (около 0.2 градуса от центра)
        bbox = f"{center_lon-0.2},{center_lat-0.2},{center_lon+0.2},{center_lat+0.2}"
        
        # Ищем объекты в заданной области
        search_url = f"https://nominatim.openstreetmap.org/search?format=json&q={obj_type}&bounded=1&viewbox={bbox}&addressdetails=1&limit={limit}"
        search_response = requests.get(search_url, headers=headers)
        search_data = search_response.json()
        
        print(f"Найдено объектов типа '{obj_type}': {len(search_data)}")
        
        # Добавляем найденные объекты
        for item in search_data:
            name = item.get('display_name', '').split(',')[0]
            address = item.get('display_name', '')
            lat = float(item['lat'])
            lon = float(item['lon'])
            
            # Используем реальные координаты (долгота, широта)
            obj = MapObject(name, obj_type, lon, lat, address)
            self.add_object(obj)
        
        print(f"Загружено {len(search_data)} объектов")
    
    def filter_by_type(self, obj_type: str) -> List[MapObject]:
        """
        Отфильтровать объекты по типу.
        
        Args:
            obj_type: Тип объектов для фильтрации
            
        Returns:
            Список объектов заданного типа
        """
        return [obj for obj in self.objects if obj.type == obj_type]
    
    def search_in_area(self, center_x: float, center_y: float, radius: float, 
                      obj_type: Optional[str] = None) -> List[Tuple[MapObject, float]]:
        """
        Поиск объектов в заданной области.
        
        Args:
            center_x: Координата X центра области (долгота)
            center_y: Координата Y центра области (широта)
            radius: Радиус области поиска (в градусах)
            obj_type: Тип объектов для поиска (опционально)
            
        Returns:
            Список кортежей (объект, расстояние) отсортированный по расстоянию
        """
        # Определяем прямоугольную область для поиска в k-d дереве
        min_x, max_x = center_x - radius, center_x + radius
        min_y, max_y = center_y - radius, center_y + radius
        
        # Ищем объекты в прямоугольной области
        candidates = self.kd_tree.range_search((min_x, min_y), (max_x, max_y))
        
        # Фильтруем по типу, если задан
        if obj_type:
            candidates = [(point, data) for point, data in candidates if data.type == obj_type]
        
        # Вычисляем расстояния и фильтруем по радиусу
        results = []
        for point, obj in candidates:
            # Вычисляем расстояние в километрах
            distance = self.calculate_distance(center_x, center_y, point[0], point[1])
            if distance <= radius * 111:  # Преобразуем градусы в км (примерно 111 км на градус)
                results.append((obj, distance))
        
        # Сортируем по расстоянию
        results.sort(key=lambda x: x[1])
        return results
    
    def calculate_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """
        Вычислить расстояние между двумя точками в километрах.
        
        Args:
            lon1: Долгота первой точки
            lat1: Широта первой точки
            lon2: Долгота второй точки
            lat2: Широта второй точки
            
        Returns:
            Расстояние в километрах
        """
        # Преобразуем градусы в радианы
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Формула гаверсинусов
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Радиус Земли в километрах
        radius = 6371
        
        return radius * c
    
    def find_nearest(self, x: float, y: float, obj_type: Optional[str] = None) -> Optional[Tuple[MapObject, float]]:
        """
        Найти ближайший объект к заданной точке.
        
        Args:
            x: Координата X точки (долгота)
            y: Координата Y точки (широта)
            obj_type: Тип объектов для поиска (опционально)
            
        Returns:
            Кортеж (объект, расстояние) или None, если объекты не найдены
        """
        if obj_type:
            # Если задан тип, фильтруем объекты
            filtered_objects = self.filter_by_type(obj_type)
            if not filtered_objects:
                return None
            
            # Создаем временное k-d дерево только с объектами нужного типа
            temp_tree = KDTree()
            for obj in filtered_objects:
                temp_tree.insert(obj.get_coordinates(), obj)
            
            result = temp_tree.nearest_neighbor((x, y))
        else:
            # Ищем ближайший объект любого типа
            result = self.kd_tree.nearest_neighbor((x, y))
        
        if result:
            point, obj, distance = result
            # Преобразуем расстояние в километры
            real_distance = self.calculate_distance(x, y, point[0], point[1])
            return (obj, real_distance)
        
        return None
    
    def get_object_types(self) -> List[str]:
        """
        Получить список доступных типов объектов.
        
        Returns:
            Список типов объектов
        """
        return sorted(list(self.object_types))
    
    def create_interactive_map(self, search_point: Tuple[float, float] = None, 
                              search_radius: float = None, nearest_object: MapObject = None,
                              found_objects: List[Tuple[MapObject, float]] = None):
        """
        Создать интерактивную карту с результатами поиска.
        
        Args:
            search_point: Точка поиска (долгота, широта)
            search_radius: Радиус поиска в км
            nearest_object: Ближайший объект
            found_objects: Список найденных объектов с расстояниями
        """
        # Создаем карту с центром в Красноярске
        map_obj = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Цвета для разных типов объектов
        type_colors = {
            'магазин': 'red',
            'кафе': 'blue',
            'больница': 'green',
            'аптека': 'orange',
            'ресторан': 'purple',
            'салон красоты': 'pink'
        }
        
        # Добавляем все объекты на карту
        for obj in self.objects:
            color = type_colors.get(obj.type, 'gray')
            
            # Создаем popup с информацией об объекте
            popup_text = f"""
            <b>{obj.name}</b><br>
            Тип: {obj.type}<br>
            Адрес: {obj.address}<br>
            Координаты: ({obj.x:.6f}, {obj.y:.6f})
            """
            
            # Добавляем маркер на карту
            folium.Marker(
                location=[obj.y, obj.x],  # folium использует [широта, долгота]
                popup=popup_text,
                tooltip=obj.name,
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(map_obj)
        
        # Добавляем точку поиска, если задана
        if search_point:
            folium.Marker(
                location=[search_point[1], search_point[0]],  # [широта, долгота]
                popup=f"Точка поиска<br>Координаты: ({search_point[0]:.6f}, {search_point[1]:.6f})",
                tooltip="Точка поиска",
                icon=folium.Icon(color='black', icon='search')
            ).add_to(map_obj)
            
            # Добавляем круг радиуса поиска, если задан
            if search_radius:
                folium.Circle(
                    location=[search_point[1], search_point[0]],
                    radius=search_radius * 1000,  # Преобразуем км в метры
                    color='black',
                    fill=False,
                    dash_array='5,5',
                    tooltip=f"Радиус поиска: {search_radius} км"
                ).add_to(map_obj)
        
        # Выделяем ближайший объект, если задан
        if nearest_object:
            folium.Marker(
                location=[nearest_object.y, nearest_object.x],
                popup=f"<b>Ближайший объект</b><br>{nearest_object.name}<br>Тип: {nearest_object.type}",
                tooltip="Ближайший объект",
                icon=folium.Icon(color='gold', icon='star')
            ).add_to(map_obj)
        
        # Выделяем найденные объекты, если заданы
        if found_objects:
            for obj, distance in found_objects:
                folium.Marker(
                    location=[obj.y, obj.x],
                    popup=f"<b>Найденный объект</b><br>{obj.name}<br>Тип: {obj.type}<br>Расстояние: {distance:.2f} км",
                    tooltip="Найденный объект",
                    icon=folium.Icon(color='cadetblue', icon='map-marker')
                ).add_to(map_obj)
        
        # Сохраняем карту в HTML файл
        map_obj.save("krasnoyarsk_map.html")
        print("Интерактивная карта сохранена в файл 'krasnoyarsk_map.html'")
        
        # Открываем карту в браузере
        try:
            webbrowser.open("krasnoyarsk_map.html")
        except Exception as e:
            print(f"Не удалось открыть карту в браузере: {e}")


def main():
    """Главная функция приложения."""
    app = MapSearchApp()
    
    # Загрузка реальных данных
    print("Загрузка данных о магазинах в Красноярске...")
    app.load_real_data("Красноярск", "магазин", 15)
    
    print("Загрузка данных о кафе в Красноярске...")
    app.load_real_data("Красноярск", "кафе", 10)
    
    print("Загрузка данных о больницах в Красноярске...")
    app.load_real_data("Красноярск", "больница", 5)
    
    
    print("Приложение для поиска ближайших объектов на карте")
    print("=" * 50)
    
    while True:
        print("\nДоступные действия:")
        print("1. Поиск ближайшего объекта (от центра города)")
        print("2. Поиск объектов в области (от центра города)")
        print("3. Поиск ближайшего объекта (ввести координаты)")
        print("4. Поиск объектов в области (ввести координаты)")
        print("5. Показать доступные типы объектов")
        print("6. Показать все объекты на карте")
        print("7. Выход")
        
        choice = input("\nВыберите действие (1-7): ").strip()
        
        if choice == "1":
            try:
                # Используем центр города как точку поиска
                lon = app.center_lon
                lat = app.center_lat
                
                print("Доступные типы объектов:")
                types = app.get_object_types()
                for i, obj_type in enumerate(types, 1):
                    print(f"{i}. {obj_type}")
                
                type_choice = input("Выберите тип объекта (оставьте пустым для любого типа): ").strip()
                obj_type = None
                if type_choice:
                    try:
                        type_index = int(type_choice) - 1
                        if 0 <= type_index < len(types):
                            obj_type = types[type_index]
                        else:
                            print("Неверный выбор типа.")
                            continue
                    except ValueError:
                        print("Неверный формат выбора.")
                        continue
                
                result = app.find_nearest(lon, lat, obj_type)
                if result:
                    obj, distance = result
                    print(f"\nБлижайший объект:")
                    print(f"  Название: {obj.name}")
                    print(f"  Тип: {obj.type}")
                    print(f"  Адрес: {obj.address}")
                    print(f"  Координаты: ({obj.x:.6f}, {obj.y:.6f})")
                    print(f"  Расстояние: {distance:.2f} км")
                    
                    # Создаем карту с результатами
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        nearest_object=obj
                    )
                else:
                    print("Объекты не найдены.")
                    # Создаем карту с точкой поиска
                    app.create_interactive_map(
                        search_point=(lon, lat)
                    )
                    
            except ValueError:
                print("Неверный формат координат.")
        
        elif choice == "2":
            try:
                # Используем центр города как точку поиска
                lon = app.center_lon
                lat = app.center_lat
                radius = float(input("Введите радиус поиска (км): "))
                
                print("Доступные типы объектов:")
                types = app.get_object_types()
                for i, obj_type in enumerate(types, 1):
                    print(f"{i}. {obj_type}")
                
                type_choice = input("Выберите тип объекта (оставьте пустым для любого типа): ").strip()
                obj_type = None
                if type_choice:
                    try:
                        type_index = int(type_choice) - 1
                        if 0 <= type_index < len(types):
                            obj_type = types[type_index]
                        else:
                            print("Неверный выбор типа.")
                            continue
                    except ValueError:
                        print("Неверный формат выбора.")
                        continue
                
                results = app.search_in_area(lon, lat, radius/111, obj_type)  # Преобразуем км в градусы
                if results:
                    print(f"\nНайдено объектов: {len(results)}")
                    for i, (obj, distance) in enumerate(results, 1):
                        print(f"{i}. {obj.name} ({obj.type})")
                        print(f"   Адрес: {obj.address}")
                        print(f"   Координаты: ({obj.x:.6f}, {obj.y:.6f})")
                        print(f"   Расстояние: {distance:.2f} км")
                    
                    # Создаем карту с результатами
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        search_radius=radius,
                        found_objects=results
                    )
                else:
                    print("Объекты не найдены.")
                    # Создаем карту с точкой поиска
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        search_radius=radius
                    )
                    
            except ValueError:
                print("Неверный формат данных.")
        
        elif choice == "3":
            try:
                lon = float(input("Введите долготу точки поиска: "))
                lat = float(input("Введите широту точки поиска: "))
                
                print("Доступные типы объектов:")
                types = app.get_object_types()
                for i, obj_type in enumerate(types, 1):
                    print(f"{i}. {obj_type}")
                
                type_choice = input("Выберите тип объекта (оставьте пустым для любого типа): ").strip()
                obj_type = None
                if type_choice:
                    try:
                        type_index = int(type_choice) - 1
                        if 0 <= type_index < len(types):
                            obj_type = types[type_index]
                        else:
                            print("Неверный выбор типа.")
                            continue
                    except ValueError:
                        print("Неверный формат выбора.")
                        continue
                
                result = app.find_nearest(lon, lat, obj_type)
                if result:
                    obj, distance = result
                    print(f"\nБлижайший объект:")
                    print(f"  Название: {obj.name}")
                    print(f"  Тип: {obj.type}")
                    print(f"  Адрес: {obj.address}")
                    print(f"  Координаты: ({obj.x:.6f}, {obj.y:.6f})")
                    print(f"  Расстояние: {distance:.2f} км")
                    
                    # Создаем карту с результатами
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        nearest_object=obj
                    )
                else:
                    print("Объекты не найдены.")
                    # Создаем карту с точкой поиска
                    app.create_interactive_map(
                        search_point=(lon, lat)
                    )
                    
            except ValueError:
                print("Неверный формат координат.")
        
        elif choice == "4":
            try:
                lon = float(input("Введите долготу центра области: "))
                lat = float(input("Введите широту центра области: "))
                radius = float(input("Введите радиус поиска (км): "))
                
                print("Доступные типы объектов:")
                types = app.get_object_types()
                for i, obj_type in enumerate(types, 1):
                    print(f"{i}. {obj_type}")
                
                type_choice = input("Выберите тип объекта (оставьте пустым для любого типа): ").strip()
                obj_type = None
                if type_choice:
                    try:
                        type_index = int(type_choice) - 1
                        if 0 <= type_index < len(types):
                            obj_type = types[type_index]
                        else:
                            print("Неверный выбор типа.")
                            continue
                    except ValueError:
                        print("Неверный формат выбора.")
                        continue
                
                results = app.search_in_area(lon, lat, radius/111, obj_type)  # Преобразуем км в градусы
                if results:
                    print(f"\nНайдено объектов: {len(results)}")
                    for i, (obj, distance) in enumerate(results, 1):
                        print(f"{i}. {obj.name} ({obj.type})")
                        print(f"   Адрес: {obj.address}")
                        print(f"   Координаты: ({obj.x:.6f}, {obj.y:.6f})")
                        print(f"   Расстояние: {distance:.2f} км")
                    
                    # Создаем карту с результатами
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        search_radius=radius,
                        found_objects=results
                    )
                else:
                    print("Объекты не найдены.")
                    # Создаем карту с точкой поиска
                    app.create_interactive_map(
                        search_point=(lon, lat),
                        search_radius=radius
                    )
                    
            except ValueError:
                print("Неверный формат данных.")
        
        elif choice == "5":
            print("Доступные типы объектов:")
            types = app.get_object_types()
            for i, obj_type in enumerate(types, 1):
                print(f"{i}. {obj_type}")
        
        elif choice == "6":
            # Показать все объекты на карте
            app.create_interactive_map()
            print("Все объекты отображены на интерактивной карте.")
        
        elif choice == "7":
            print("Спасибо за использование приложения!")
            break
        
        else:
            print("Неверный выбор. Пожалуйста, выберите действие от 1 до 7.")


if __name__ == "__main__":
    main()