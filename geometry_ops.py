import math

from polygon import Point, Polygon

TOL = 5.0  # допуск в пикселях для кликов мышью


def _cross(ox: float, oy: float,
           ax: float, ay: float,
           bx: float, by: float) -> float:
    return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)


def _dist_point_segment(p: Point, a: Point, b: Point) -> float:
    dx, dy = b.x - a.x, b.y - a.y
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(p.x - a.x, p.y - a.y)
    t = max(0.0, min(1.0, ((p.x - a.x) * dx + (p.y - a.y) * dy) / l2))
    return math.hypot(p.x - (a.x + t * dx), p.y - (a.y + t * dy))


def point_in_polygon(point: Point, poly: Polygon) -> bool:
    verts = poly.vertices
    n = len(verts)

    if n == 0:
        return False

    if n == 1:
        v = verts[0]
        return math.hypot(v.x - point.x, v.y - point.y) <= TOL

    if n == 2:
        return _dist_point_segment(point, verts[0], verts[1]) <= TOL
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = verts[i].x, verts[i].y
        xj, yj = verts[j].x, verts[j].y
        if (yi > point.y) != (yj > point.y):
            x_int = (xj - xi) * (point.y - yi) / (yj - yi + 1e-12) + xi
            if point.x < x_int:
                inside = not inside
        j = i
    return inside

def classify_point_vs_edge(point: Point, e1: Point, e2: Point) -> str:
    cp = _cross(e1.x, e1.y, e2.x, e2.y, point.x, point.y)
    length = math.hypot(e2.x - e1.x, e2.y - e1.y)
    if length == 0 or abs(cp) / length < TOL:
        return "on"
    return "left" if cp > 0 else "right"


TAG = "temp_op"


def clear_temp(canvas) -> None:
    canvas.delete(TAG)


def draw_temp_point(canvas, p: Point, color: str = "red", r: int = 6) -> None:
    canvas.create_oval(p.x - r, p.y - r, p.x + r, p.y + r,
                       fill=color, outline="black", tags=TAG)


def draw_temp_line(canvas, a: Point, b: Point,
                   color: str = "green", width: int = 2) -> None:
    canvas.create_line(a.x, a.y, b.x, b.y,
                       fill=color, width=width, tags=TAG)


def draw_temp_text(canvas, p: Point, text: str, color: str = "black") -> None:
    canvas.create_text(p.x + 10, p.y - 10, text=text,
                       fill=color, anchor="w", tags=TAG, font=("Arial", 10))

def do_point_in_polygon(canvas, poly: Polygon, point: Point, log) -> None:
    inside = point_in_polygon(point, poly)
    kind = poly.kind()
    res = "ПРИНАДЛЕЖИТ " if inside else "НЕ принадлежит "
    color = "blue" if inside else "red"
    log(f"[п.5] {kind}  |  точка ({point.x:.0f},{point.y:.0f}) → {res}")
    draw_temp_point(canvas, point, color=color, r=7)


def do_classify(canvas, e1: Point, e2: Point, point: Point, log) -> None:
    pos = classify_point_vs_edge(point, e1, e2)
    names = {"left": "СЛЕВА", "right": "СПРАВА", "on": "НА РЕБРЕ"}
    colors = {"left": "green", "right": "orange", "on": "black"}
    log(f"[п.6] точка ({point.x:.0f},{point.y:.0f}) → {names[pos]} от ребра")
    draw_temp_point(canvas, point, color=colors[pos], r=7)
    draw_temp_text(canvas, point, names[pos], color=colors[pos])