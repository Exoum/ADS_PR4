"""Модуль реализации k-d дерева для поиска ближайших точек на карте."""

import math
from typing import List, Optional, Tuple, Any


class KDNode:
    """Узел k-d дерева."""
    
    def __init__(self, point: Tuple[float, float], data: Any = None):
        """
        Инициализация узла k-d дерева.
        
        Args:
            point: Кортеж координат (x, y)
            data: Дополнительные данные, связанные с точкой
        """
        self.point = point
        self.data = data
        self.left: Optional['KDNode'] = None
        self.right: Optional['KDNode'] = None


class KDTree:
    """k-d дерево для поиска ближайших точек."""
    
    def __init__(self):
        """Инициализация k-d дерева."""
        self.root: Optional[KDNode] = None
    
    def insert(self, point: Tuple[float, float], data: Any = None) -> None:
        """
        Вставка точки в k-d дерево.
        
        Args:
            point: Кортеж координат (x, y)
            data: Дополнительные данные, связанные с точкой
        """
        self.root = self._insert_recursive(self.root, point, data, 0)
    
    def _insert_recursive(self, node: Optional[KDNode], point: Tuple[float, float], 
                          data: Any, depth: int) -> KDNode:
        """
        Рекурсивная вставка точки в k-d дерево.
        
        Args:
            node: Текущий узел
            point: Кортеж координат (x, y)
            data: Дополнительные данные
            depth: Глубина узла (для определения оси разделения)
            
        Returns:
            Обновленный узел
        """
        if node is None:
            return KDNode(point, data)
        
        # Определяем ось разделения (0 - x, 1 - y)
        axis = depth % 2
        
        # Сравниваем по соответствующей оси
        if point[axis] < node.point[axis]:
            node.left = self._insert_recursive(node.left, point, data, depth + 1)
        else:
            node.right = self._insert_recursive(node.right, point, data, depth + 1)
        
        return node
    
    def delete(self, point: Tuple[float, float]) -> bool:
        """
        Удаление точки из k-d дерева.
        
        Args:
            point: Кортеж координат (x, y) для удаления
            
        Returns:
            True, если точка была удалена, False если не найдена
        """
        self.root, deleted = self._delete_recursive(self.root, point, 0)
        return deleted
    
    def _delete_recursive(self, node: Optional[KDNode], point: Tuple[float, float], 
                         depth: int) -> Tuple[Optional[KDNode], bool]:
        """
        Рекурсивное удаление точки из k-d дерева.
        
        Args:
            node: Текущий узел
            point: Кортеж координат для удаления
            depth: Глубина узла
            
        Returns:
            Кортеж (обновленный узел, флаг удаления)
        """
        if node is None:
            return None, False
        
        axis = depth % 2
        
        # Нашли узел для удаления
        if node.point == point:
            # Случай 1: листовой узел
            if node.left is None and node.right is None:
                return None, True
            
            # Случай 2: есть правый потомок
            if node.right is not None:
                # Находим минимальный элемент в правом поддереве
                min_node = self._find_min(node.right, axis)
                node.point = min_node.point
                node.data = min_node.data
                node.right, _ = self._delete_recursive(node.right, min_node.point, depth + 1)
            else:
                # Случай 3: есть только левый потомок
                min_node = self._find_min(node.left, axis)
                node.point = min_node.point
                node.data = min_node.data
                node.left, _ = self._delete_recursive(node.left, min_node.point, depth + 1)
            
            return node, True
        
        # Рекурсивный поиск
        if point[axis] < node.point[axis]:
            node.left, deleted = self._delete_recursive(node.left, point, depth + 1)
        else:
            node.right, deleted = self._delete_recursive(node.right, point, depth + 1)
        
        return node, deleted
    
    def _find_min(self, node: KDNode, axis: int) -> KDNode:
        """
        Поиск минимального элемента по заданной оси.
        
        Args:
            node: Начальный узел
            axis: Ось для поиска минимума (0 - x, 1 - y)
            
        Returns:
            Узел с минимальным значением по заданной оси
        """
        if node is None:
            raise ValueError("Node cannot be None")
        
        # Если это лист или ось совпадает с осью узла
        if axis == 0 and node.left is None:
            return node
        if axis == 1 and node.left is None and node.right is None:
            return node
        
        # Рекурсивный поиск
        if axis == 0:
            # Поиск минимума по x
            if node.left is None:
                return node
            return self._find_min(node.left, axis)
        else:
            # Поиск минимума по y
            left_min = self._find_min(node.left, axis) if node.left else None
            right_min = self._find_min(node.right, axis) if node.right else None
            
            min_node = node
            if left_min and left_min.point[axis] < min_node.point[axis]:
                min_node = left_min
            if right_min and right_min.point[axis] < min_node.point[axis]:
                min_node = right_min
            
            return min_node
    
    def range_search(self, min_point: Tuple[float, float], 
                    max_point: Tuple[float, float]) -> List[Tuple[Tuple[float, float], Any]]:
        """
        Поиск точек в заданном прямоугольном диапазоне.
        
        Args:
            min_point: Кортеж минимальных координат (min_x, min_y)
            max_point: Кортеж максимальных координат (max_x, max_y)
            
        Returns:
            Список кортежей (точка, данные) найденных точек
        """
        result = []
        self._range_search_recursive(self.root, min_point, max_point, 0, result)
        return result
    
    def _range_search_recursive(self, node: Optional[KDNode], 
                              min_point: Tuple[float, float], max_point: Tuple[float, float],
                              depth: int, result: List[Tuple[Tuple[float, float], Any]]) -> None:
        """
        Рекурсивный поиск точек в диапазоне.
        
        Args:
            node: Текущий узел
            min_point: Кортеж минимальных координат
            max_point: Кортеж максимальных координат
            depth: Глубина узла
            result: Список для накопления результатов
        """
        if node is None:
            return
        
        # Проверяем, попадает ли точка в диапазон
        if (min_point[0] <= node.point[0] <= max_point[0] and 
            min_point[1] <= node.point[1] <= max_point[1]):
            result.append((node.point, node.data))
        
        # Определяем ось разделения
        axis = depth % 2
        
        # Рекурсивно проверяем поддеревья
        # Всегда проверяем левое поддерево, если min_point[axis] <= node.point[axis]
        if min_point[axis] <= node.point[axis]:
            self._range_search_recursive(node.left, min_point, max_point, depth + 1, result)
        # Всегда проверяем правое поддерево, если node.point[axis] <= max_point[axis]
        if node.point[axis] <= max_point[axis]:
            self._range_search_recursive(node.right, min_point, max_point, depth + 1, result)
    
    def nearest_neighbor(self, target: Tuple[float, float]) -> Optional[Tuple[Tuple[float, float], Any, float]]:
        """
        Поиск ближайшего соседа к заданной точке.
        
        Args:
            target: Кортеж координат целевой точки (x, y)
            
        Returns:
            Кортеж (точка, данные, расстояние) ближайшей точки или None, если дерево пусто
        """
        if self.root is None:
            return None
        
        best = [None, None, float('inf')]  # [точка, данные, расстояние]
        self._nearest_neighbor_recursive(self.root, target, 0, best)
        return tuple(best) if best[0] is not None else None
    
    def _nearest_neighbor_recursive(self, node: KDNode, target: Tuple[float, float], 
                                  depth: int, best: List) -> None:
        """
        Рекурсивный поиск ближайшего соседа.
        
        Args:
            node: Текущий узел
            target: Целевая точка
            depth: Глубина узла
            best: Список [лучшая точка, лучшие данные, лучшее расстояние]
        """
        if node is None:
            return
        
        # Вычисляем расстояние до текущей точки
        distance = math.sqrt((node.point[0] - target[0])**2 + (node.point[1] - target[1])**2)
        
        # Обновляем лучший результат, если текущая точка ближе
        if distance < best[2]:
            best[0] = node.point
            best[1] = node.data
            best[2] = distance
        
        # Определяем ось разделения
        axis = depth % 2
        
        # Определяем, в какое поддерево идти первым
        if target[axis] < node.point[axis]:
            self._nearest_neighbor_recursive(node.left, target, depth + 1, best)
            # Проверяем, нужно ли проверять другое поддерево
            if abs(target[axis] - node.point[axis]) < best[2]:
                self._nearest_neighbor_recursive(node.right, target, depth + 1, best)
        else:
            self._nearest_neighbor_recursive(node.right, target, depth + 1, best)
            # Проверяем, нужно ли проверять другое поддерево
            if abs(target[axis] - node.point[axis]) < best[2]:
                self._nearest_neighbor_recursive(node.left, target, depth + 1, best)