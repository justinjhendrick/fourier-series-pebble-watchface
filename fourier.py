import math
from dataclasses import dataclass
import time
import turtle

from tkinter import (
    Canvas,
    Tk,
    N,
    W,
    E,
    S,
)

@dataclass
class Coord:  # in pixel space
    x: int    # positive is right
    y: int    # positive is down

def dist(c1: Coord, c2: Coord) -> float:
    x = c1.x - c2.x
    y = c1.y - c2.y
    return math.sqrt(x**2 + y**2)

@dataclass
class Point:  # in arbitrary size float 0.0-1.0 space
    x: float  # positive is right
    y: float  # positive is down

class Sketchpad(Canvas):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.bind("<Button-1>", self._add)
        self.bind("<Button-2>", self._del)
        self.bind("<Button-3>", self._start_move)
        self.bind("<ButtonRelease-3>", self._end_move)
        self._coords: dict[int, Coord] = {}  # ident to position
        self._order: dict[int, float] = {}  # ident to order
        self._text: dict[int, int] = {}  # circle id to text id
        self._move_started: Coord | None = None
        self.radius = 10

    def _add(self, event) -> None:
        print(f"_add({event.x}, {event.y})")
        c = Coord(event.x, event.y)
        x0 = c.x - self.radius
        x1 = c.x + self.radius
        y0 = c.y - self.radius
        y1 = c.y + self.radius
        ident = self.create_oval(x0, y0, x1, y1)
        position = max(self._order.values(), default=0.0) + 1.0  # TODO: find two nearest points and average them. Or append to the end. this only appends to the end right now.
        self._order[ident] = position
        text_id = self.create_text(c.x, c.y, text=str(position))
        self._coords[ident] = c
        self._text[ident] = text_id

    def _find(self, query: Coord) -> int | None:
        mind = math.inf
        mini = None
        for ident, c in self._coords.items():
            d = dist(c, query)
            if d < mind:
                mind = d
                mini = ident
        if mind > self.radius * 1.2:
            return None
        return mini

    def _del(self, event) -> bool:
        print(f"_del({event.x}, {event.y})")
        clicked = Coord(event.x, event.y)
        ident = self._find(clicked)
        if ident is None:
            return False
        self.delete(ident)
        self.delete(self._text[ident])
        del self._coords[ident]
        del self._text[ident]
        del self._order[ident]
        return True

    def _start_move(self, event) -> None:
        if self._del(event):
            self._move_started = Coord(event.x, event.y)

    def _end_move(self, event) -> None:
        if self._move_started is None:
            return
        self._add(event)
        self._move_started = None

    def to_points(self) -> list[Point]:
        items = list(self._coords.items())
        items.sort(key=lambda k: self._order[k[0]])
        coords = [i[1] for i in items]
        xs = [c.x for c in coords]
        ys = [c.y for c in coords]
        minx = min(xs)
        maxx = max(xs)
        miny = min(ys)
        maxy = max(ys)
        rx = maxx - minx
        ry = maxy - miny
        r = max(rx, ry)
        return [
            Point(
                (c.x - minx) / r,
                (c.y - miny) / r,
            )
            for c in coords
        ]



@dataclass
class Harmonic:
    freq: float
    amp: float
    phase: float


FULL_TURN = 2 * math.pi


def compress(harmonics: list[Harmonic]) -> list[Harmonic]:
    result: list[Harmonic] = []
    for h in harmonics:
        if h.amp < 0.0001:
            continue
        result.append(h)
    print(f"dropped {len(harmonics) - len(result)}")
    return result


def to_harmonics(points: list[Point]) -> list[Harmonic]:
    # https://www.youtube.com/watch?v=Qr3VsZYQy4s
    n = len(points)
    result: list[Harmonic] = []
    for harmonic_idx in range(n):
        complex_for_average: complex = 0 + 0j

        for point_idx in range(n):
            direction: float = -harmonic_idx * point_idx / n * FULL_TURN
            complex_for_probe = complex(
                math.cos(direction),
                math.sin(direction),
            )
            complex_for_point = complex(
                points[point_idx].x,
                points[point_idx].y,
            )
            complex_for_average += complex_for_probe * complex_for_point
        complex_for_average /= n

        result.append(
            Harmonic(
                freq=harmonic_idx,
                amp=abs(complex_for_average),
                phase=math.atan2(complex_for_average.imag, complex_for_average.real),
            )
        )
    return result


def draw(harmonics: list[Harmonic], num_step: int) -> None:
    turtle.clear()
    for step in range(num_step):
        s = Point(0, 0)
        for h in harmonics:
            f = h.freq
            if f >= len(harmonics) / 2:
                f -= len(harmonics)
            phase = step / num_step * FULL_TURN * f + h.phase
            s.x += h.amp * math.cos(phase)
            s.y += h.amp * math.sin(phase)

        PX = 200
        if step == 0:
            turtle.teleport(PX * s.x, PX * s.y)
        else:
            turtle.goto(PX * s.x, PX * s.y)
    time.sleep(1)

TRIG_MAX_ANGLE = 0x10000

def as_c(harmonics: list[Harmonic]) -> str:
    result = []
    result.append("static Harmonic harmonics[%d] = {" % len(harmonics))
    for h in harmonics:
        freq = int(h.freq)
        amp = int(h.amp * 1000)
        phase = int(h.phase * TRIG_MAX_ANGLE / (2 * math.pi))
        result.append("    (Harmonic){.freq=%d, .amp=%d, .phase=%d}," % (freq, amp, phase))
    result.append("};")
    return "\n".join(result)



def main() -> None:
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    sketch = Sketchpad(root)
    sketch.grid(column=0, row=0, sticky=(N, W, E, S))
    root.mainloop()

    points = sketch.to_points()
    harmonics = compress(to_harmonics(points))
    print(as_c(harmonics))
    draw(harmonics, 100)




if __name__ == "__main__":
    main()
