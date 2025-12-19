"""Тесты для k-d дерева."""

import unittest
from tree import KDTree


class TestKDTree(unittest.TestCase):
    """Тесты для k-d дерева."""
    
    def setUp(self):
        """Инициализация тестового k-d дерева."""
        self.tree = KDTree()
        # Добавляем тестовые точки
        self.points = [
            ((2, 3), "point1"),
            ((5, 4), "point2"),
            ((9, 6), "point3"),
            ((4, 7), "point4"),
            ((8, 1), "point5"),
            ((7, 2), "point6")
        ]
        
        for point, data in self.points:
            self.tree.insert(point, data)
    
    def test_insert_and_nearest_neighbor(self):
        """Тест вставки точек и поиска ближайшего соседа."""
        # Поиск ближайшего к точке (5, 5)
        nearest = self.tree.nearest_neighbor((5, 5))
        self.assertIsNotNone(nearest)
        
        # Ближайшая точка должна быть (5, 4) или (4, 7)
        self.assertIn(nearest[0], [(5, 4), (4, 7)])
    
    def test_range_search(self):
        """Тест поиска в диапазоне."""
        # Поиск точек в прямоугольнике от (2, 3) до (6, 5)
        results = self.tree.range_search((2, 3), (6, 5))
        
        # Должны найти точки (2, 3) и (5, 4)
        points = [point for point, _ in results]
        self.assertIn((2, 3), points)
        self.assertIn((5, 4), points)
    
    def test_delete(self):
        """Тест удаления точек."""
        # Удаляем точку (5, 4)
        deleted = self.tree.delete((5, 4))
        self.assertTrue(deleted)
        
        # Проверяем, что точка удалена
        nearest = self.tree.nearest_neighbor((5, 4))
        self.assertNotEqual(nearest[0], (5, 4))
        
        # Пытаемся удалить несуществующую точку
        deleted = self.tree.delete((100, 100))
        self.assertFalse(deleted)


if __name__ == "__main__":
    unittest.main()