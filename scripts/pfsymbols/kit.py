"""Drawing kit for Porto Faifo Symbols: the Porto Faifo Sans geometry at icon scale.

Recipes draw on a 24-unit grid with y up (live area 2..22), in centre-line
coordinates.  A ``Pen`` turns centre lines into filled regions at its stroke
width, with the rules of the font:

* line ends are cut on the grid, horizontally or vertically, never round
  (``"g"`` picks the cut closer to perpendicular, horizontal at 45° like
  the arms of v and x);
* open joins of ``apexFlatBelow`` degrees or more stay sharp like E L <;
  sharper ones end in a narrow flat cut on the grid, ``apexFlat`` strokes
  wide, like the apex of A and the foot of V;
* closed shapes round their corners with the font's tensions (outer 0.59,
  inner 0.58), so a corner is a touch fuller than a circular arc;
* rings are Porto Faifo Sans ovals (superellipses at the outer/inner tension) and
  dots are true circles ``dotDiameter`` strokes wide, like the i dot.

Regions are ``pathops.Path`` objects and every boolean is explicit, so the
direction of a contour never matters.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path

import pathops

from pfsans.geometry import Contour, _contours_from, add, cross, line_intersection, mul, sub, superellipse
from pfsans.system import ROOT, load

SYMBOL_PATH = ROOT / "symbols" / "symbol-system.json"
BIG = 100.0


def symbol_system(path: Path = SYMBOL_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ regions
def region(*contours: Contour) -> pathops.Path:
    """Union of closed contours, whatever their direction."""
    acc = pathops.Path()
    for c in contours:
        p = pathops.Path()
        c.draw(p.getPen(), round_to=0)
        acc = pathops.op(acc, p, pathops.PathOp.UNION)
    return acc


def union(*regions: pathops.Path) -> pathops.Path:
    acc = pathops.Path()
    for r in regions:
        acc = pathops.op(acc, r, pathops.PathOp.UNION)
    return acc


def minus(a: pathops.Path, *bs: pathops.Path) -> pathops.Path:
    for b in bs:
        a = pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    return a


def clip(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.INTERSECTION)


def box(x0: float = -BIG, y0: float = -BIG, x1: float = BIG, y1: float = BIG) -> pathops.Path:
    """A rectangle region; the defaults make half-planes (``box(y0=12)``)."""
    return region(Contour((x0, y0)).line((x1, y0)).line((x1, y1)).line((x0, y1)).close())


def contours(r: pathops.Path) -> list[Contour]:
    return _contours_from(r)


def _rebuilt(cs) -> pathops.Path:
    """Contours back into a region, counters kept (winding fill)."""
    out = pathops.Path()
    for c in cs:
        c.draw(out.getPen(), round_to=0)
    return pathops.simplify(out)


def mirrored(r: pathops.Path, axis: float = 12.0) -> pathops.Path:
    """``r`` mirrored across the vertical line x = ``axis`` (undo -> redo)."""
    return _rebuilt(c.mirrored_x(axis) for c in contours(r))


def turned(r: pathops.Path, angle: float, cx: float = 12.0, cy: float = 12.0) -> pathops.Path:
    """``r`` rotated by ``angle`` degrees about (cx, cy)."""
    return _rebuilt(c.rotated(angle, cx, cy) for c in contours(r))


def _without_crumbs(r: pathops.Path, min_area: float) -> pathops.Path:
    """``r`` without contours (ink or holes) smaller than ``min_area``."""
    cs = contours(r)
    if not cs:
        return r
    keep = [c for c in cs if abs(c.signed_area()) >= min_area]
    out = pathops.Path()
    for c in keep:
        c.draw(out.getPen(), round_to=0)
    return pathops.simplify(out)


# --------------------------------------------------------------- polylines
def _unit(v):
    ln = math.hypot(*v)
    return (v[0] / ln, v[1] / ln)


def _angle(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _meet(p, d, q, e):
    hit = line_intersection(p, d, q, e)
    return p if hit is None else add(p, mul(d, hit[0]))


@dataclass
class _Node:
    """One corner of an offset side: ``entry`` and ``exit`` points joined by
    ``kind`` ("pt" = same point, "arc" = tension curve, "flat" = line)."""

    kind: str
    entry: tuple
    exit: tuple
    a0: float = 0.0
    a1: float = 0.0
    k: float = 0.0

    def draw(self, c: Contour) -> None:
        c.line(self.entry)
        if self.kind == "arc":
            c.curve(self.exit, self.a0, self.a1, self.k)
        elif self.kind == "flat":
            c.line(self.exit)

    def draw_reversed(self, c: Contour) -> None:
        c.line(self.exit)
        if self.kind == "arc":
            c.curve(self.entry, self.a1 + 180, self.a0 + 180, self.k)
        elif self.kind == "flat":
            c.line(self.entry)


# --------------------------------------------------------------------- pen
@dataclass
class Pen:
    size: int
    weight: str
    w: float  # stroke, design units
    wr: float  # Regular stroke at this size, design units
    k: object  # Porto Faifo Sans curves: outer, inner, circle
    dot_d: float
    dot_big: float
    dot_gap: float  # i-dot gap, fraction of the stem below it
    flat: float
    flat_below: float
    radius: float
    radius_small: float
    hinted: bool = False  # strokes rounded to whole pixels (Linux pixel editions)

    @property
    def h(self) -> float:
        return self.w / 2

    def stroked(self, w: float) -> "Pen":
        """The same pen at another stroke (a beam, a knock-out gap)."""
        return replace(self, w=w)

    # ------------------------------------------------------------- strokes
    def bar(self, p, q, cut="g") -> pathops.Path:
        return self.line([p, q], cut=cut)

    def line(self, pts, cut="g", corners=None) -> pathops.Path:
        """Open stroke through ``pts``.  ``cut`` is one end kind or a pair:
        "g" grid (auto), "h", "v", or "p" perpendicular (for ends hidden
        inside another stroke).  ``corners`` maps a vertex index to a
        centre-line radius; unlisted joins are sharp or flat by angle."""
        cuts = (cut, cut) if isinstance(cut, str) else cut
        left = self._side(pts, +1, corners or {})
        right = self._side(pts, -1, corners or {})
        u0, un = _unit(sub(pts[1], pts[0])), _unit(sub(pts[-1], pts[-2]))
        sl, sr = (self._end(pts[0], u0, s, cuts[0]) for s in (+1, -1))
        el, er = (self._end(pts[-1], un, s, cuts[1]) for s in (+1, -1))
        c = Contour(sl)
        for node in left:
            node.draw(c)
        c.line(el).line(er)
        for node in reversed(right):
            node.draw_reversed(c)
        c.line(sr)
        return region(c.close())

    def frame(self, pts, r=None, corners=None) -> pathops.Path:
        """Closed stroke along the polygon ``pts``; every corner rounds at
        centre-line radius ``r`` (default ``radius``) unless ``corners``
        overrides it (0 = sharp)."""
        r = self.radius if r is None else r
        spec = {i: r for i in range(len(pts))}
        spec.update(corners or {})
        a = self._loop(pts, +1, spec)
        b = self._loop(pts, -1, spec)
        return pathops.op(region(a), region(b), pathops.PathOp.XOR)

    def solid(self, pts, r=None, corners=None) -> pathops.Path:
        """The filled silhouette of ``frame(pts, r)``: its outer edge."""
        r = self.radius if r is None else r
        spec = {i: r for i in range(len(pts))}
        spec.update(corners or {})
        a, b = self._loop(pts, +1, spec), self._loop(pts, -1, spec)
        return union(region(a), region(b))

    def rect(self, x0, y0, x1, y1, r=None) -> pathops.Path:
        return self.frame([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)

    def rect_solid(self, x0, y0, x1, y1, r=None) -> pathops.Path:
        return self.solid([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)

    # --------------------------------------------------------------- round
    def ring(self, cx, cy, rx, ry=None) -> pathops.Path:
        ry = rx if ry is None else ry
        h = self.h
        outer = superellipse(cx, cy, rx + h, ry + h, self.k.outer)
        inner = superellipse(cx, cy, rx - h, ry - h, self.k.inner)
        return minus(region(outer), region(inner))

    def disc(self, cx, cy, rx, ry=None) -> pathops.Path:
        """The filled silhouette of ``ring``."""
        ry = rx if ry is None else ry
        return region(superellipse(cx, cy, rx + self.h, ry + self.h, self.k.outer))

    def arc(self, cx, cy, rx, ry=None, keep=None) -> pathops.Path:
        """Part of a ring: the ring inside ``keep`` (half-planes from
        ``box``), so its ends are cut on the grid."""
        return clip(self.ring(cx, cy, rx, ry), keep)

    def dot(self, cx, cy, big=False) -> pathops.Path:
        d = self.dot_big if big else self.dot_d
        return region(superellipse(cx, cy, d / 2, d / 2, self.k.circle))

    def root_dot(self, cx, cy) -> pathops.Path:
        """A standalone dot: the one a level family grows from (Wi-Fi, hotspot), or the three of ``more``.
        At a 1 px pixel edition the round dot is under 2 px and lights no
        pixel fully, so it becomes a 2 x 2 px square on the pixel grid, every pixel full."""
        unit = 24 / self.size
        if not (self.hinted and abs(self.w - unit) < 1e-6):
            return self.dot(cx, cy, big=True)
        x0, y0 = round(cx / unit - 1) * unit, round(cy / unit - 1) * unit
        return box(x0, y0, x0 + 2 * unit, y0 + 2 * unit)

    def pixel_centred(self, r: pathops.Path, x, y) -> pathops.Path:
        """At a 1 px pixel edition, ``r`` moved (by under half a pixel) so the
        design point (x, y) sits on a pixel centre.  A 1 px 45-degree stroke
        whose centre line runs through pixel centres fills them; through
        pixel corners it splits into two grey halves (a 22 px
        chevron then reads at about 60 % ink)."""
        unit = 24 / self.size
        if not (self.hinted and abs(self.w - unit) < 1e-6):
            return r
        dx = (math.floor(x / unit) + 0.5) * unit - x
        dy = (math.floor(y / unit) + 0.5) * unit - y
        return _rebuilt(c.translated(dx, dy) for c in contours(r))

    def outline(self, contour: Contour) -> pathops.Path:
        """Stroke a smooth closed centre line (bell, shield ...).  A tight
        curve can make the inner offset cross itself; the crumb it leaves
        (a speck of ink in the counter or a pinhole in the stroke) is
        dropped."""
        c = contour.oriented(True)
        ink = minus(region(c.offset(self.h)), region(c.offset(-self.h)))
        return _without_crumbs(ink, (0.5 * self.w) ** 2)

    def silhouette(self, contour: Contour) -> pathops.Path:
        return region(contour.oriented(True).offset(self.h))

    # ------------------------------------------------------------ internal
    def _end(self, p, u, s, kind):
        """Side ``s`` (+1 left, -1 right) of an end at ``p``, direction ``u``."""
        n = (-u[1], u[0])
        q = add(p, mul(n, s * self.h))
        if kind == "g":
            kind = "h" if abs(u[1]) >= abs(u[0]) - 1e-9 else "v"
        if kind == "h" and abs(u[1]) > 1e-9:
            return _meet(q, u, p, (1.0, 0.0))
        if kind == "v" and abs(u[0]) > 1e-9:
            return _meet(q, u, p, (0.0, 1.0))
        return q

    def _corner(self, prev, v, nxt, s, r):
        """The node of side ``s`` at vertex ``v`` between ``prev`` and ``nxt``.
        ``r`` None: an open join, sharp or flat by angle; 0: sharp; "flat":
        a point cut flat on the grid (star tips); else the centre-line
        radius."""
        ua, ub = _unit(sub(v, prev)), _unit(sub(nxt, v))
        na, nb = (-ua[1], ua[0]), (-ub[1], ub[0])
        pa, pb = add(v, mul(na, s * self.h)), add(v, mul(nb, s * self.h))
        turn = cross(ua, ub)
        if abs(turn) < 1e-9 and ua[0] * ub[0] + ua[1] * ub[1] > 0:
            return _Node("pt", pa, pa)
        m = _meet(pa, ua, pb, ub)
        outside = (turn > 0 and s < 0) or (turn < 0 and s > 0)
        theta = math.acos(max(-1.0, min(1.0, ua[0] * ub[0] + ua[1] * ub[1])))
        interior = 180 - math.degrees(theta)
        if r is None or r == "flat":  # sharp, or a flat apex when acute
            if outside and (r == "flat" or interior < self.flat_below):
                return self._flat(m, ua, ub)
            return _Node("pt", m, m)
        rs = r + self.h if outside else r - self.h
        if r <= 0 or rs <= 1e-6:
            return _Node("pt", m, m)
        t = rs * math.tan(theta / 2)
        p1, p2 = sub(m, mul(ua, t)), add(m, mul(ub, t))
        return _Node("arc", p1, p2, _angle(ua), _angle(ub), self.k.outer if outside else self.k.inner)

    def _flat(self, m, ua, ub):
        """Cut the miter tip ``m`` on the grid so the cut is ``flat`` strokes
        wide (the apex of A, the foot of V)."""
        b = sub(ua, ub)  # outward bisector
        axis = 0 if abs(b[0]) >= abs(b[1]) else 1  # 0: vertical cut (x = c)
        sgn = 1 if b[axis] > 0 else -1

        def at(delta):
            c = m[axis] - sgn * delta
            ta = (m[axis] - c) / ua[axis]
            tb = (c - m[axis]) / ub[axis]
            return sub(m, mul(ua, ta)), add(m, mul(ub, tb))

        a1, b1 = at(1.0)
        span = math.hypot(*sub(a1, b1))
        pa, pb = at(self.flat * self.w / span)
        return _Node("flat", pa, pb)

    def _side(self, pts, s, corners):
        return [self._corner(pts[i - 1], pts[i], pts[i + 1], s, corners.get(i)) for i in range(1, len(pts) - 1)]

    def _loop(self, pts, s, spec) -> Contour:
        n = len(pts)
        nodes = [self._corner(pts[i - 1], pts[i], pts[(i + 1) % n], s, spec[i]) for i in range(n)]
        c = Contour(nodes[0].exit)
        for node in nodes[1:] + nodes[:1]:
            node.draw(c)
        return c.close()


# ---------------------------------------------------------------- factory
def stroke_px(raw_font: dict, sym: dict, weight: str, size: int) -> float:
    st = load(weight).st
    upm = raw_font["metrics"]["unitsPerEm"]
    text = sym["sizes"][str(size)]["text"]
    return st.stemLower / upm * text * sym["stroke"]["opticalGain"]


def pen(weight: str, size: int, sym: dict | None = None, hint: bool | None = None) -> Pen:
    """The pen for ``weight`` at canvas ``size``; hinted sizes round the
    stroke to whole pixels (``hint`` overrides the size's setting)."""
    sym = sym or symbol_system()
    fs = load(weight)
    reg = load("Regular")
    sz = sym["sizes"][str(size)]
    w_px = stroke_px(fs.raw, sym, weight, size)
    hinted = bool(sz["hint"] if hint is None else hint)
    if hinted:
        w_px = max(1.0, math.floor(w_px + 0.5))
    unit = sym["grid"]["design"] / size  # design units per px
    w = w_px * unit
    wr = stroke_px(reg.raw, sym, "Regular", size) * unit
    shp = sym["shapes"]
    dot = fs.sh.dotDiameter * w
    return Pen(
        size=size,
        weight=weight,
        w=w,
        wr=wr,
        k=fs.k,
        dot_d=dot,
        dot_big=dot * shp["dotStandalone"],
        dot_gap=fs.sh.dotGap,
        flat=204 / reg.st.diagonalUpper,
        flat_below=shp["apexFlatBelow"],
        radius=shp["radius"],
        radius_small=shp["radiusSmall"],
        hinted=hinted,
    )
