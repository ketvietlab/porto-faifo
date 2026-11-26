"""Regions to SVG path data at a canvas size, with optional pixel hinting."""

from __future__ import annotations

import math

import pathops

from pfsans.geometry import Contour

from .kit import contours

EPS = 1e-3


def _scaled(cs: list[Contour], k: float) -> list[Contour]:
    return [c.scaled(k, k) for c in cs]


def _snap_values(cs: list[Contour]):
    """Coordinates that carry a straight vertical/horizontal edge or a
    vertical/horizontal tangent (an oval's extreme): x stems and y bars."""
    xs, ys = set(), set()
    for c in cs:
        for seg in c.beziers():
            if len(seg) == 2:
                (x0, y0), (x1, y1) = seg
                if abs(x1 - x0) < EPS:
                    xs.add(x0)
                if abs(y1 - y0) < EPS:
                    ys.add(y0)
            else:
                p0, p1, p2, p3 = seg
                for a, b in ((p0, p1), (p3, p2)):
                    if abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) > EPS:
                        xs.add(a[0])
                    if abs(a[1] - b[1]) < EPS and abs(a[0] - b[0]) > EPS:
                        ys.add(a[1])
    return sorted(xs), sorted(ys)


def hinted(cs: list[Contour]) -> list[Contour]:
    """Move every stem and bar edge to the nearest whole pixel.  Strokes are
    whole pixels wide at hinted sizes, so both edges of a stroke share their
    fraction and move together; points that share an edge's coordinate
    (handles on an oval's extreme) move with it, so curves stay smooth."""
    xs, ys = _snap_values(cs)

    def snap(v, table):
        for t in table:
            if abs(v - t) < EPS:
                return math.floor(t + 0.5)
        return v

    return [c.transformed(lambda p: (snap(p[0], xs), snap(p[1], ys))) for c in cs]


def _num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def d_of(cs: list[Contour]) -> str:
    """SVG ``d`` for contours already in SVG coordinates (y down)."""
    out = []
    for c in cs:
        def pt(p):
            return f"{_num(p[0])} {_num(p[1])}"

        out.append("M" + pt(c.start))
        for seg in c.segments:
            out.append(("L" + pt(seg[1])) if seg[0] == "line" else ("C" + " ".join(pt(q) for q in seg[1:])))
        out.append("Z")
    return "".join(out)


def path_data(region: pathops.Path, size: int, design: int, hint: bool) -> str:
    """SVG ``d`` for a design-grid region at ``size`` px, y flipped."""
    cs = _scaled(contours(region), size / design)
    if hint:
        cs = hinted(cs)
    out = []
    for c in cs:
        def pt(p):
            return f"{_num(p[0])} {_num(size - p[1])}"

        out.append("M" + pt(c.start))
        for seg in c.segments:
            if seg[0] == "line":
                out.append("L" + pt(seg[1]))
            else:
                out.append("C" + " ".join(pt(q) for q in seg[1:]))
        out.append("Z")
    return "".join(out)


def bounds(region: pathops.Path, size: int, design: int):
    if region.area == 0:
        return None
    x0, y0, x1, y1 = region.bounds
    k = size / design
    return x0 * k, size - y1 * k, x1 * k, size - y0 * k


def _ghost(d: str, extra: str = "", opacity: float | None = None) -> str:
    """The second layer of a level icon (levels above the current one)."""
    return f'<path{extra} opacity="{GHOST if opacity is None else opacity}" d="{d}"/>' if d else ""


GHOST = 0.35


def svg(d: str, size: int, ghost: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" fill="currentColor"><path d="{d}"/>{_ghost(ghost)}</svg>\n'
    )
