import math
from dataclasses import dataclass
from pprint import pprint
import turtle


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Harmonic:
    freq: float
    amp: float
    phase: float


FULL_TURN = 2 * math.pi


def polygon(args: list[float]) -> list[Point]:
    # https://schervenkov.github.io/polygon-editor/
    assert len(args) % 2 == 0
    xs = []
    ys = []
    i = 0
    while i < len(args):
        xs.append(args[i])
        ys.append(args[i + 1])
        i += 2
    maxx = max(xs)
    maxy = max(ys)
    result = []
    for x, y in zip(xs, ys, strict=True):
        result.append(Point(x / maxx, -y / maxy))
    return result


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
    for step in range(num_step):
        s = Point(0, 0)
        for h in harmonics:
            f = h.freq
            if f >= len(harmonics) / 2:
                f -= len(harmonics)
            phase = step / num_step * FULL_TURN * f + h.phase
            s.x += h.amp * math.cos(phase)
            s.y += h.amp * math.sin(phase)

        PX = 100
        if step == 0:
            turtle.teleport(PX * s.x, PX * s.y)
        else:
            turtle.goto(PX * s.x, PX * s.y)


def main() -> None:
    # fmt: off
    one = polygon([33,29,76,0,155,21,179,58,171,95,155,141,150,170,155,247,161,290,189,296,232,304,247,332,215,358,155,361,77,363,40,352,26,320,59,307,103,294,126,241,113,183,111,142,115,96,97,56,77,53,32,55,0,48])
    two = polygon([220,49,180,11,110,0,57,7,22,32,20,72,39,75,88,54,111,51,145,63,163,96,159,122,148,173,127,197,76,208,36,248,11,284,0,314,31,331,115,334,165,334,263,330,294,303,239,279,180,276,116,290,98,276,139,240,194,213,240,196,280,140,282,77])
    four = polygon([207.25,1.6974291206017824,0,260.8948582412037,195,260.8948582412037,194,498.8948582412037,278,499.8948582412037,272,257.8948582412037,368,258.8948582412037,366,203.89485824120368,121.25,206.69742912060178,288.25,0])
    eight = polygon([179,26,0,164,185,283,23,429,204,532,219,503,102,424,224,306,318,387,179,528,220,543,380,377,92,161,218,60,286,110,209,246,237,269,384,106,206,0])
    # fmt: on
    harmonics = compress(to_harmonics(four))
    draw(harmonics, 1000)


if __name__ == "__main__":
    main()
