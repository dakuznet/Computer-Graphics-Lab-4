import math
from typing import Optional

import numpy as np

from polygon import Point, Polygon

class AffineMatrix:
    """Генератор матриц 3×3 в однородных координатах."""

    @staticmethod
    def translation(dx: float, dy: float) -> np.ndarray:
        """Матрица смещения."""
        return np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0,  1],
        ], dtype=float)

    @staticmethod
    def rotation(angle_rad: float) -> np.ndarray:
        """Матрица поворота вокруг начала координат."""
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return np.array([
            [c, -s, 0],
            [s,  c, 0],
            [0,  0, 1],
        ], dtype=float)

    @staticmethod
    def scaling(sx: float, sy: float) -> np.ndarray:
        """Матрица масштабирования."""
        return np.array([
            [sx,  0, 0],
            [ 0, sy, 0],
            [ 0,  0, 1],
        ], dtype=float)

    @staticmethod
    def rotation_around(angle_rad: float, cx: float, cy: float) -> np.ndarray:
        """Поворот вокруг произвольной точки: T(c) · R · T(−c)."""
        return (AffineMatrix.translation(cx, cy)
                @ AffineMatrix.rotation(angle_rad)
                @ AffineMatrix.translation(-cx, -cy))

    @staticmethod
    def scaling_around(sx: float, sy: float, cx: float, cy: float) -> np.ndarray:
        """Масштабирование относительно произвольной точки: T(c) · S · T(−c)."""
        return (AffineMatrix.translation(cx, cy)
                @ AffineMatrix.scaling(sx, sy)
                @ AffineMatrix.translation(-cx, -cy))


def apply_matrix(poly: Polygon, M: np.ndarray) -> None:
    """Применить матрицу M ко всем вершинам полигона (in-place)."""
    new_verts = []
    for v in poly.vertices:
        h = np.array([v.x, v.y, 1.0])
        r = M @ h
        new_verts.append(Point(float(r[0]), float(r[1])))
    poly.vertices = new_verts







def translate(poly: Polygon, dx: float, dy: float) -> None:
    """Смещение на (dx, dy)."""
    apply_matrix(poly, AffineMatrix.translation(dx, dy))


def rotate_around_point(poly: Polygon, angle_deg: float, center: Point) -> None:
    """Поворот вокруг заданной пользователем точки."""
    apply_matrix(poly, AffineMatrix.rotation_around(
        math.radians(angle_deg), center.x, center.y))


def rotate_around_center(poly: Polygon, angle_deg: float) -> None:
    """Поворот вокруг центра масс полигона."""
    c = poly.centroid()
    apply_matrix(poly, AffineMatrix.rotation_around(
        math.radians(angle_deg), c.x, c.y))


def scale_around_point(poly: Polygon, sx: float, sy: float, center: Point) -> None:
    """Масштабирование относительно заданной пользователем точки."""
    apply_matrix(poly, AffineMatrix.scaling_around(sx, sy, center.x, center.y))


def scale_around_center(poly: Polygon, sx: float, sy: float) -> None:
    """Масштабирование относительно центра масс полигона."""
    c = poly.centroid()
    apply_matrix(poly, AffineMatrix.scaling_around(sx, sy, c.x, c.y))







def segment_intersection(a1: Point, a2: Point,
                         b1: Point, b2: Point) -> Optional[Point]:
    """
    Точка пересечения отрезков a1-a2 и b1-b2.
    Возвращает None, если отрезки не пересекаются.
    """
    d1x, d1y = a2.x - a1.x, a2.y - a1.y
    d2x, d2y = b2.x - b1.x, b2.y - b1.y
    denom = d1x * d2y - d1y * d2x
    if abs(denom) < 1e-12:
        return None

    dx, dy = b1.x - a1.x, b1.y - a1.y
    t = (dx * d2y - dy * d2x) / denom
    u = (dx * d1y - dy * d1x) / denom

    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return Point(a1.x + t * d1x, a1.y + t * d1y)
    return None