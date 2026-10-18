import math
import time
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tkinter import (
    Canvas,
    Tk,
    N,
    W,
    E,
    S,
    Event,
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
        self.bind("<Control-Button-1>", self._start_add_after)
        self.bind("<Control-ButtonRelease-1>", self._end_add_after)
        self._coords: dict[int, Coord] = {}  # ident to position
        self._order: dict[int, float] = {}  # ident to order
        self._text: dict[int, int] = {}  # circle id to text id
        self._move_position: float | None = None
        self._after_position: float | None = None
        self.radius = 15

    def _add(self, event: Event, position: float | None = None) -> None:
        c = Coord(event.x, event.y)
        x0 = c.x - self.radius
        x1 = c.x + self.radius
        y0 = c.y - self.radius
        y1 = c.y + self.radius
        ident = self.create_oval(x0, y0, x1, y1)
        if position is None:
            position = max(self._order.values(), default=0.0) + 1.0
        self._order[ident] = position
        text_id = self.create_text(c.x, c.y, text=f"{position:.2f}")
        self._coords[ident] = c
        self._text[ident] = text_id

    def _next_after(self, position: float) -> float:
        order = sorted(self._order.values())
        for p in order:
            if p > position:
                return (p + position) / 2.0
        if len(order) == 0:
            return 1.0
        return order[-1] + 1.0

    def _start_add_after(self, event: Event) -> None:
        clicked = Coord(event.x, event.y)
        ident = self._find(clicked)
        if ident is None:
            return
        orig_position = self._order[ident]
        self._after_position = self._next_after(orig_position)

    def _end_add_after(self, event: Event) -> None:
        if self._after_position is None:
            return
        self._add(event, self._after_position)
        self._after_position = None

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

    def _del(self, event: Event) -> None | float:
        clicked = Coord(event.x, event.y)
        ident = self._find(clicked)
        if ident is None:
            return None
        self.delete(ident)
        self.delete(self._text[ident])
        del self._coords[ident]
        del self._text[ident]
        position = self._order[ident]
        del self._order[ident]
        return position

    def _start_move(self, event: Event) -> None:
        self._move_position = self._del(event)

    def _end_move(self, event: Event) -> None:
        if self._move_position is None:
            return
        self._add(event, position=self._move_position)
        self._move_position = None

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
            direction: float = (-harmonic_idx * point_idx * 2 * math.pi) / n
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
    for h in result:
        if h.freq >= len(result) / 2:
            h.freq -= len(result)
    return result


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
    header = Path(".") / "src" / "c" / "digits.h"
    with header.open("w") as f:
        f.write('#pragma once\n\n')
        f.write('#include "harmonic.h"\n\n')
        f.write(as_c(harmonics))
    subprocess.check_call(["pebble", "build"])
    subprocess.check_call(["pebble", "install", "--emulator", "emery"])




if __name__ == "__main__":
    main()
