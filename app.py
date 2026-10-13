import tkinter as tk
from tkinter import simpledialog, messagebox

from polygon import Point, Polygon         
import transforms as tr                    
import geometry_ops as gops                


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Полигоны — 6 пунктов")
        root.geometry("1150x720")

        self.poly = Polygon()
        self.mode = "create"
        self.buf: list[Point] = []          
        self.edge1_a = self.edge1_b = None  
        self._pending = None                

        self._build_ui()
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Motion>", self._motion)

    def _build_ui(self):
        left = tk.Frame(self.root, width=310, bg="#f4f4f4")
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        def section(title):
            tk.Label(left, text=title, font=("Arial", 11, "bold"),
                     bg="#f4f4f4").pack(pady=(12, 2))

        def btn(text, cmd):
            tk.Button(left, text=text, command=cmd,
                      width=32).pack(padx=8, pady=2)

        section("Пункты 1-2")
        btn("Режим: создание полигона (п.1)", lambda: self._set_mode("create"))
        btn("Очистить сцену (п.2)", self._clear)

        section("Пункт 3 — Преобразования")
        btn("Смещение (dx, dy)", self._tr_translate)
        btn("Поворот вокруг точки (клик)", self._tr_rot_user)
        btn("Поворот вокруг центра", self._tr_rot_center)
        btn("Масштаб отн. точки (клик)", self._tr_scale_user)
        btn("Масштаб отн. центра", self._tr_scale_center)

        section("Пункт 4 — Пересечение")
        btn("Пересечение двух рёбер (п.4)", lambda: self._set_mode("intersect"))

        section("Пункты 5-6")
        btn("Точка ∈ полигон (п.5)", lambda: self._set_mode("contains"))
        btn("Точка vs ребро (п.6)", lambda: self._set_mode("classify"))

        section("Журнал")
        self.log_box = tk.Text(left, height=14, state="disabled",
                               wrap="word", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=8, pady=4)

        self.canvas = tk.Canvas(self.root, bg="white",
                                highlightthickness=1, highlightbackground="#aaa")
        self.canvas.pack(side=tk.RIGHT, fill="both", expand=True)

        self.status = tk.StringVar(value="Режим: создание. Кликайте по холсту.")
        tk.Label(self.root, textvariable=self.status, anchor="w",
                 bg="#e0e0e0", font=("Arial", 10)).pack(side=tk.BOTTOM, fill="x")


    def log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")


    def _redraw_poly(self):
        self.canvas.delete("poly")
        v = self.poly.vertices
        if not v:
            return
        if len(v) == 1:
            p = v[0]
            self.canvas.create_oval(p.x-5, p.y-5, p.x+5, p.y+5,
                                    fill="black", tags="poly")
        elif len(v) == 2:
            self.canvas.create_line(v[0].x, v[0].y, v[1].x, v[1].y,
                                    width=2, tags="poly")
            for p in v:
                self.canvas.create_oval(p.x-4, p.y-4, p.x+4, p.y+4,
                                        fill="black", tags="poly")
        else:
            coords = [c for p in v for c in (p.x, p.y)]
            self.canvas.create_polygon(coords, fill="#c8e6ff",
                                       outline="black", width=2, tags="poly")
            for p in v:
                self.canvas.create_oval(p.x-4, p.y-4, p.x+4, p.y+4,
                                        fill="red", tags="poly")

    def _set_mode(self, mode: str):
        self.mode = mode
        self.buf.clear()
        self.edge1_a = self.edge1_b = None
        gops.clear_temp(self.canvas)
        msgs = {
            "create":    "п.1: кликайте — добавляются вершины полигона.",
            "intersect": "п.4: клик 1,2 — первое ребро; движение — динамическое 2-е ребро; клик 3 — зафиксировать.",
            "contains":  "п.5: кликайте — проверяется принадлежность точки полигону.",
            "classify":  "п.6: клик 1,2 — ребро; клик 3 — точка для классификации.",
        }
        self.status.set(msgs.get(mode, ""))

    def _clear(self):
        self.poly.clear()
        self.canvas.delete("all")
        self.buf.clear()
        self.edge1_a = self.edge1_b = None
        self._set_mode("create")
        self.log("Сцена очищена.")

    def _need(self, n=1):
        if len(self.poly.vertices) < n:
            messagebox.showinfo("Инфо", f"Нужно минимум {n} вершин(а).")
            return False
        return True

    def _tr_translate(self):
        if not self._need(): return
        dx = simpledialog.askfloat("Смещение", "dx:", parent=self.root)
        if dx is None: return
        dy = simpledialog.askfloat("Смещение", "dy:", parent=self.root)
        if dy is None: return
        tr.translate(self.poly, dx, dy)
        self._redraw_poly()
        self.log(f"п.3: смещение ({dx}, {dy})")

    def _tr_rot_user(self):
        if not self._need(): return
        self.status.set("п.3: кликните центр поворота на холсте…")
        self._pending = "rot_user"

    def _tr_rot_center(self):
        if not self._need(): return
        a = simpledialog.askfloat("Поворот", "Угол (°):", parent=self.root)
        if a is None: return
        tr.rotate_around_center(self.poly, a)
        self._redraw_poly()
        self.log(f"п.3: поворот вокруг центра на {a}°")

    def _tr_scale_user(self):
        if not self._need(): return
        self.status.set("п.3: кликните центр масштабирования…")
        self._pending = "scale_user"

    def _tr_scale_center(self):
        if not self._need(): return
        sx = simpledialog.askfloat("Масштаб", "sx:", parent=self.root, initialvalue=1.5)
        if sx is None: return
        sy = simpledialog.askfloat("Масштаб", "sy:", parent=self.root, initialvalue=1.5)
        if sy is None: return
        tr.scale_around_center(self.poly, sx, sy)
        self._redraw_poly()
        self.log(f"п.3: масштаб отн. центра ({sx}, {sy})")

    def _click(self, ev):
        p = Point(ev.x, ev.y)
        if self._pending:
            act = self._pending
            self._pending = None
            if act == "rot_user":
                a = simpledialog.askfloat("Поворот", "Угол (°):", parent=self.root)
                if a is None: return
                tr.rotate_around_point(self.poly, a, p)
                self._redraw_poly()
                self.log(f"п.3: поворот вокруг ({p.x:.0f},{p.y:.0f}) на {a}°")
            elif act == "scale_user":
                sx = simpledialog.askfloat("Масштаб", "sx:", parent=self.root, initialvalue=1.5)
                if sx is None: return
                sy = simpledialog.askfloat("Масштаб", "sy:", parent=self.root, initialvalue=1.5)
                if sy is None: return
                tr.scale_around_point(self.poly, sx, sy, p)
                self._redraw_poly()
                self.log(f"п.3: масштаб отн. ({p.x:.0f},{p.y:.0f}) → ({sx},{sy})")
            return
        
        if self.mode == "create":
            self.poly.add_vertex(p)
            self._redraw_poly()
            self.log(f"п.1: вершина ({p.x:.0f},{p.y:.0f}) → {self.poly.kind()}")

        elif self.mode == "intersect":
            self.buf.append(p)
            if len(self.buf) == 2:
                self.edge1_a, self.edge1_b = self.buf
                self.status.set("п.4: 2-е ребро следует за курсором. Клик — зафиксировать.")
            elif len(self.buf) == 3:
                e2a, e2b = self.edge1_b, p
                inter = tr.segment_intersection(self.edge1_a, self.edge1_b, e2a, e2b)
                gops.clear_temp(self.canvas)
                gops.draw_temp_line(self.canvas, self.edge1_a, self.edge1_b, "green", 3)
                gops.draw_temp_line(self.canvas, e2a, e2b, "orange", 3)
                if inter:
                    gops.draw_temp_point(self.canvas, inter, "magenta", 8)
                    self.log(f"п.4: пересечение ({inter.x:.1f},{inter.y:.1f})")
                else:
                    self.log("п.4: рёбра не пересекаются")
                self.buf.clear()
                self.edge1_a = self.edge1_b = None
                self.status.set("п.4: клик 1,2 — первое ребро…")

        elif self.mode == "contains":
            if self.poly.is_empty():
                self.log("п.5: полигон пуст — создайте полигон сначала.")
                return
            gops.do_point_in_polygon(self.canvas, self.poly, p, self.log)

        elif self.mode == "classify":
            self.buf.append(p)
            if len(self.buf) == 2:
                gops.draw_temp_line(self.canvas, self.buf[0], self.buf[1], "green", 3)
                self.status.set("п.6: кликните точку для классификации.")
            elif len(self.buf) == 3:
                gops.do_classify(self.canvas, self.buf[0], self.buf[1], self.buf[2], self.log)
                self.buf.clear()
                self.status.set("п.6: клик 1,2 — новое ребро…")

    def _motion(self, ev):
        if self.mode == "intersect" and self.edge1_a is not None:
            cursor = Point(ev.x, ev.y)
            gops.clear_temp(self.canvas)
            gops.draw_temp_line(self.canvas, self.edge1_a, self.edge1_b, "green", 3)
            gops.draw_temp_line(self.canvas, self.edge1_b, cursor, "orange", 2)
            inter = tr.segment_intersection(self.edge1_a, self.edge1_b,
                                            self.edge1_b, cursor)
            if inter:
                gops.draw_temp_point(self.canvas, inter, "magenta", 7)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()