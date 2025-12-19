"""Визуализация реальной карты Красноярска с объектами."""

import folium
import requests
from typing import List
from map_search import MapObject, MapSearchApp


def get_krasnoyarsk_center():
    """
    Получить координаты центра Красноярска.
    
    Returns:
        tuple: Координаты центра Красноярска (широта, долгота)
    """
    headers = {'User-Agent': 'MapSearchApp/1.0'}
    url = "https://nominatim.openstreetmap.org/search?q=Красноярск&format=json"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon
    
    # Если не удалось получить координаты, используем приблизительные
    return 56.0091173, 92.8725860


def create_real_map(objects: List[MapObject], center_lat: float = None, center_lon: float = None):
    """
    Создать интерактивную карту Красноярска с объектами.
    
    Args:
        objects: Список объектов для отображения
        center_lat: Широта центра карты (опционально)
        center_lon: Долгота центра карты (опционально)
    """
    # Если координаты центра не заданы, получаем их
    if center_lat is None or center_lon is None:
        center_lat, center_lon = get_krasnoyarsk_center()
    
    # Создаем карту с центром в Красноярске
    map_obj = folium.Map(
        location=[center_lat, center_lon],
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
    
    # Добавляем объекты на карту
    for obj in objects:
        color = type_colors.get(obj.type, 'gray')
        
        # Создаем popup с информацией об объекте
        popup_text = f"""
        <b>{obj.name}</b><br>
        Тип: {obj.type}<br>
        Адрес: {obj.address}<br>
        """
        
        # Добавляем маркер на карту
        folium.Marker(
            location=[obj.y, obj.x],  # folium использует [широта, долгота]
            popup=popup_text,
            tooltip=obj.name,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(map_obj)
    
    # Сохраняем карту в HTML файл
    map_obj.save("krasnoyarsk_map.html")
    print("Карта сохранена в файл 'krasnoyarsk_map.html'")
    print("Откройте этот файл в браузере для просмотра интерактивной карты.")


def demo_real_map():
    """Демонстрация визуализации реальной карты Красноярска."""
    # Создаем приложение и загружаем данные
    app = MapSearchApp()
    
    # Загрузка реальных данных
    print("Загрузка данных о магазинах в Красноярске...")
    app.load_real_data("Красноярск", "магазин", 15)
    
    print("Загрузка данных о кафе в Красноярске...")
    app.load_real_data("Красноярск", "кафе", 10)
    
    print("Загрузка данных о больницах в Красноярске...")
    app.load_real_data("Красноярск", "больница", 5)
    
    # Создаем и сохраняем реальную карту
    print("Создание интерактивной карты Красноярска...")
    create_real_map(app.objects)
    
    print("Демонстрация завершена.")


if __name__ == "__main__":
    demo_real_map()