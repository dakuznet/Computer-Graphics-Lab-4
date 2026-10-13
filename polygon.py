from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Point:
    x: float
    y: float


class Polygon:

    def __init__(self):
        self.vertices: List[Point] = []

    def add_vertex(self, p: Point) -> None:
        self.vertices.append(p)

    def is_empty(self) -> bool:
        return len(self.vertices) == 0

    def is_point(self) -> bool:
        return len(self.vertices) == 1

    def is_edge(self) -> bool:
        return len(self.vertices) == 2

    def is_polygon(self) -> bool:
        return len(self.vertices) >= 3

    def kind(self) -> str:
        if self.is_point():
            return "точка"
        if self.is_edge():
            return "ребро"
        return "выпуклый полигон" if self.is_convex() else "невыпуклый полигон"

    def get_edges(self) -> List[Tuple[Point, Point]]:
        edges: List[Tuple[Point, Point]] = []
        n = len(self.vertices)
        if n < 2:
            return edges
        for i in range(n - 1):
            edges.append((self.vertices[i], self.vertices[i + 1]))
        if n >= 3:
            edges.append((self.vertices[-1], self.vertices[0]))
        return edges

    def centroid(self) -> Point:
        if not self.vertices:
            return Point(0.0, 0.0)
        n = len(self.vertices)
        return Point(
            sum(v.x for v in self.vertices) / n,
            sum(v.y for v in self.vertices) / n,
        )

    def is_convex(self) -> bool:
        n = len(self.vertices)
        if n < 3:
            return True
        sign = 0
        for i in range(n):
            a = self.vertices[i]
            b = self.vertices[(i + 1) % n]
            c = self.vertices[(i + 2) % n]
            cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x)
            if cross > 0:
                if sign < 0:
                    return False
                sign = 1
            elif cross < 0:
                if sign > 0:
                    return False
                sign = -1
        return True

    def clear(self) -> None:
        self.vertices.clear()