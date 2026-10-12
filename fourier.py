import math
from dataclasses import dataclass
import time
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
    # fmt: off
    zero = polygon([136,0,0,126,118,263,279,138,169,32,136,62,214,139,126,205,59,130,170,31])
    one = polygon([47,32,0,62,3,85,13,101,59,73,59,225,58,358,120,356,116,232,115,75,114,0,81,15])
    two = polygon([62.25,25.4765625,101,5.2265625,205.1875,0,235.1875,52.36328125,210,129.2265625,138,190.2265625,73.1875,271.36328125,58.1875,319.36328125,154.1875,313.36328125,242.1875,330.4765625,245.875,366.4765625,162,379.2265625,54,374.2265625,2,355.2265625,4,290.2265625,56,205.2265625,110,140.2265625,176,84.2265625,172.1875,51.4765625,104,61.2265625,55,91.2265625,25,110.2265625,4,104.2265625,0,68.2265625,28,45.2265625])
    three = polygon([0,103,101,0,202,104,121,190,206,274,109,384,2,285,28,257,102,328,152,277,73,192,156,105,102,51,22,130])
    four = polygon([207.25,1.6974291206017824,0,260.8948582412037,195,260.8948582412037,194,498.8948582412037,278,499.8948582412037,272,257.8948582412037,368,258.8948582412037,366,203.89485824120368,121.25,206.69742912060178,288.25,0])
    eight = polygon([179,26,0,164,185,283,23,429,204,532,219,503,102,424,224,306,318,387,179,528,220,543,380,377,92,161,218,60,286,110,209,246,237,269,384,106,206,0])
    # fmt: on
    digits = [three]
    for digit in digits:
        harmonics = compress(to_harmonics(digit))
        print(as_c(harmonics))
        #draw(harmonics, 100)


if __name__ == "__main__":
    main()
