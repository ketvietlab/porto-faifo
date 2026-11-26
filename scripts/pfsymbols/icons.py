"""Porto Faifo Symbols recipes.

Each recipe draws one icon with a ``Pen`` on the 24-unit grid (y up, live
area 2..22) in centre-line coordinates; ``fill=True`` draws the filled
variant where one exists.  Centre lines sit ``inset`` (0.9) inside the
keylines, so the outer edge of a Regular stroke lands on them: circle 20
(r 9.1), square 17.2, portrait 16 x 20 (x 4.9..19.1), landscape 20 x 16
(y 4.9..19.1).

The registry pairs every icon with the Lucide name of the same meaning (a
cross-reference only; no Lucide geometry is used) and, where one exists, its
freedesktop name.  ``spec`` names come from the freedesktop Icon Naming
Specification; ``gnome`` names are Adwaita extensions with no spec
equivalent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
import pathops

from pfsans.geometry import Contour, superellipse, untangled
from pfsans.system import ROOT

from .kit import BIG, Pen, box, clip, minus, mirrored, region, union

LO, HI = 2.9, 21.1  # centre lines on the 2 / 22 keylines
R = 9.1  # centre line of the 20-unit keyline circle


def _u(a):
    return (math.cos(math.radians(a)), math.sin(math.radians(a)))


def _at(p, d, t):
    return (p[0] + d[0] * t, p[1] + d[1] * t)


# ------------------------------------------------------------- navigation
def search(p: Pen, fill=False):
    c, r = (10.2, 13.8), 7.0
    s = _at(c, _u(-45), r)
    return union(p.ring(*c, r), p.bar(s, (20.4, 3.6), cut=("p", "h")))


def plus(p: Pen, fill=False):
    return union(p.bar((12, 5), (12, 19)), p.bar((5, 12), (19, 12)))


def minus_(p: Pen, fill=False):
    return p.bar((5, 12), (19, 12))


def close(p: Pen, fill=False):
    return union(p.bar((6, 6), (18, 18)), p.bar((6, 18), (18, 6)))


def check(p: Pen, fill=False):
    return p.line([(4, 12.2), (9.4, 6.8), (20, 17.4)])


def _chevron(p: Pen, pts):
    return p.pixel_centred(p.line(pts), *pts[1])


def chevron_right(p: Pen, fill=False):
    return _chevron(p, [(8.8, 18), (14.8, 12), (8.8, 6)])


def chevron_left(p: Pen, fill=False):
    return _chevron(p, [(15.2, 18), (9.2, 12), (15.2, 6)])


def chevron_down(p: Pen, fill=False):
    return _chevron(p, [(6, 15.2), (12, 9.2), (18, 15.2)])


def chevron_up(p: Pen, fill=False):
    return _chevron(p, [(6, 8.8), (12, 14.8), (18, 8.8)])


def arrow_right(p: Pen, fill=False):
    return union(p.bar((3.8, 12), (19.6, 12), cut=("v", "p")), p.line([(13, 18.6), (19.6, 12), (13, 5.4)]))


def menu(p: Pen, fill=False):
    return union(*(p.bar((4, y), (20, y)) for y in (6.4, 12, 17.6)))


def more(p: Pen, fill=False):
    return union(*(p.root_dot(x, 12) for x in (5.4, 12, 18.6)))


def home(p: Pen, fill=False):
    pts = [(4.4, LO), (19.6, LO), (19.6, 12.6), (12, 20.2), (4.4, 12.6)]
    corners = {2: p.radius_small, 3: 1.5, 4: p.radius_small}
    door = [(9.8, LO), (9.8, 9.4), (14.2, 9.4), (14.2, LO)]
    if fill:
        knock = p.solid([(9.8, LO - 2), (14.2, LO - 2), (14.2, 9.4), (9.8, 9.4)], r=p.radius_small)
        return minus(p.solid(pts, corners=corners), knock)
    return union(p.frame(pts, corners=corners), p.line(door, cut="h", corners={1: p.radius_small, 2: p.radius_small}))


def user(p: Pen, fill=False):
    head, rh = (12, 15.9), 4.2
    base, rx, ry = 2.6, 7.6, 5.6
    if fill:
        return union(p.disc(*head, rh), clip(p.disc(12, base, rx, ry), box(y0=base)))
    return union(p.ring(*head, rh), p.arc(12, base, rx, ry, keep=box(y0=base)))


def settings(p: Pen, fill=False):
    """Six teeth on a Porto Faifo oval, stroked like every other outline: the outer
    edge grows the silhouette by half a stroke, the inner edge shrinks it.
    When the stroke leaves a tooth less than a unit of counter (Bold) the
    tooth turns solid, as heavy weights of a font drop a counter."""
    c, body, tip, tw, hub = (12, 12), 7.0, R, 3.4, 2.6

    def teeth(grow):
        return union(*(region(Contour((c[0] - tw / 2 - grow, c[1])).line((c[0] + tw / 2 + grow, c[1])).line((c[0] + tw / 2 + grow, c[1] + tip + grow)).line((c[0] - tw / 2 - grow, c[1] + tip + grow)).close().rotated(a, *c)) for a in range(0, 360, 60)))

    outer = union(region(superellipse(*c, body + p.h, body + p.h, p.k.outer)), teeth(p.h))
    if fill:
        return minus(outer, region(superellipse(*c, hub + p.h, hub + p.h, p.k.inner)))
    inner = region(superellipse(*c, body - p.h, body - p.h, p.k.inner))
    if tw - p.w >= 1.0:  # the tooth keeps its counter until it would be a slit
        inner = union(inner, teeth(-p.h))
    return union(minus(outer, inner), p.ring(*c, hub))


def apps(p: Pen, fill=False):
    s, out = 6.6, []
    for x0 in (3.4, 14.0):
        for y0 in (3.4, 14.0):
            out.append((p.rect_solid if fill else p.rect)(x0, y0, x0 + s, y0 + s, r=1.5))
    return union(*out)


# ------------------------------------------------------------------ status
def _bell():
    c = Contour((4.4, 7.4)).line((19.6, 7.4))
    c.curve((18.0, 10.6), 112, 90, 0.62)
    c.line((18.0, 12.8))
    c.curve((12, 18.8), 90, 180, 0.59)
    c.curve((6.0, 12.8), 180, 270, 0.59)
    c.line((6.0, 10.6))
    c.curve((4.4, 7.4), 270, 248, 0.62)
    return c.close()


def bell(p: Pen, fill=False):
    knob = p.bar((12, 18.4), (12, 20.8), cut=("p", "h"))
    if fill:
        clapper = clip(p.disc(12, 5.6, 2.2), box(y1=5.6))
        return union(p.silhouette(_bell()), knob, clapper)
    return union(p.outline(_bell()), knob, p.arc(12, 5.6, 2.2, keep=box(y1=5.6)))


def info(p: Pen, fill=False):
    stem = 5.6
    gap = p.dot_gap * stem
    y0 = 12 - (stem + gap + p.dot_d) / 2
    i = union(p.bar((12, y0), (12, y0 + stem), cut="h"), p.dot(12, y0 + stem + gap + p.dot_d / 2))
    if fill:
        return minus(p.disc(12, 12, R), i)
    return union(p.ring(12, 12, R), i)


def warning(p: Pen, fill=False):
    tri = [(12, 20.4), (2.6, 3.9), (21.4, 3.9)]
    stem = 5.0
    gap = p.dot_gap * stem
    y0 = 9.6 - (stem + gap + p.dot_d) / 2 + 0.4
    mark = union(p.bar((12, y0 + p.dot_d + gap), (12, y0 + p.dot_d + gap + stem), cut="h"), p.dot(12, y0 + p.dot_d / 2))
    if fill:
        return minus(p.solid(tri, r=1.6), mark)
    return union(p.frame(tri, r=1.6), mark)


def lock(p: Pen, fill=False):
    body = (4.6, LO, 19.4, 12.4)
    shackle = union(p.arc(12, 15.6, 4.2, 4.4, keep=box(y0=15.6)), p.bar((7.8, 12.4), (7.8, 15.6), cut="p"), p.bar((16.2, 12.4), (16.2, 15.6), cut="p"))
    key = p.bar((12, 5.8), (12, 9.4), cut="h")
    if fill:
        return union(minus(p.rect_solid(*body), key), shackle)
    return union(p.rect(*body), shackle, key)


def clock(p: Pen, fill=False):
    hands = p.line([(12, 17.2), (12, 12), (15.8, 9.4)], cut=("h", "g"))
    if fill:
        return minus(p.disc(12, 12, R), hands)
    return union(p.ring(12, 12, R), hands)


def star(p: Pen, fill=False):
    """The five points end flat on the grid like the apex of A."""
    c, ro, ri = (12, 11.6), 9.4, 0.48
    pts = []
    for i in range(10):
        a = math.radians(90 + 36 * i)
        rr = ro if i % 2 == 0 else ro * ri
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    corners = {i: ("flat" if i % 2 == 0 else 0) for i in range(10)}
    return (p.solid if fill else p.frame)(pts, corners=corners)


def power(p: Pen, fill=False):
    c, r = (12, 11.0), 8.0
    keep = minus(box(), box(8.2, c[1], 15.8, BIG))
    return union(p.arc(*c, r, keep=keep), p.bar((12, 21.0), (12, 11.4), cut="h"))


def wifi(p: Pen, fill=False):
    c = (12, 6.2)
    arcs = [p.arc(*c, r, keep=box(y0=c[1] + r * math.sin(math.radians(45)))) for r in (3.9, 7.7, 11.5)]
    return union(*arcs, p.root_dot(*c))


def battery(p: Pen, fill=False):
    x0, y0, x1, y1 = LO, 6.6, 19.4, 17.4
    nub = box(x1 + p.h - 0.2, 10.2, 21.8, 13.8)
    g = p.h + 1.1
    level = box(x0 + g, y0 + g, 11.6, y1 - g)
    return union(p.rect(x0, y0, x1, y1), nub, level)


def volume(p: Pen, fill=False):
    cone = [(3.4, 9.0), (7.6, 9.0), (12.4, 4.6), (12.4, 19.4), (7.6, 15.0), (3.4, 15.0)]
    corners = {0: 1.0, 1: 0, 2: 1.0, 3: 1.0, 4: 0, 5: 1.0}
    cx = 12.4
    waves = [p.arc(cx, 12, r, keep=clip(box(x0=cx), box(y0=12 - r * 0.72, y1=12 + r * 0.72))) for r in (4.4, 8.2)]
    return union((p.solid if fill else p.frame)(cone, corners=corners), *waves)


def refresh(p: Pen, fill=False):
    c, r = (12, 11.2), 7.2
    top = c[1] + r
    keep = union(box(x1=c[0]), box(y1=c[1]))
    return union(p.arc(*c, r, keep=keep), p.bar((c[0], top), (15.6, top), cut="p"), p.line([(12.4, top + 3.2), (15.6, top), (12.4, top - 3.2)]))


# --------------------------------------------------------------- documents
FILE = [(4.9, LO), (19.1, LO), (19.1, 15.6), (13.6, HI), (4.9, HI)]
FOLD = [(13.6, HI), (13.6, 15.6), (19.1, 15.6)]


def file(p: Pen, fill=False):
    corners = {2: 0, 3: 0}
    if fill:
        return minus(p.solid(FILE, corners=corners), p.line(FOLD, cut="p"))
    return union(p.frame(FILE, corners=corners), p.line(FOLD, cut="p"))


def file_text(p: Pen, fill=False):
    lines = union(p.bar((8.6, 14.8), (11.4, 14.8)), p.bar((8.6, 10.8), (15.4, 10.8)), p.bar((8.6, 6.8), (15.4, 6.8)))
    if fill:
        return minus(file(p, True), lines)
    return union(file(p), lines)


def folder(p: Pen, fill=False):
    pts = [(LO, 4.4), (HI, 4.4), (HI, 16.2), (12.4, 16.2), (10.4, 18.8), (LO, 18.8)]
    corners = {3: p.radius_small, 4: p.radius_small}
    return (p.solid if fill else p.frame)(pts, corners=corners)


def calendar(p: Pen, fill=False):
    x0, y0, x1, y1, yh = 3.4, 3.4, 20.6, 19.0, 14.2
    tabs = union(p.bar((8, 16.4), (8, 21.2), cut="h"), p.bar((16, 16.4), (16, 21.2), cut="h"))
    if fill:
        head = clip(p.rect_solid(x0, y0, x1, y1), box(y0=yh - p.h))
        return union(p.rect(x0, y0, x1, y1), head, tabs)
    return union(p.rect(x0, y0, x1, y1), p.bar((x0, yh), (x1, yh), cut="p"), tabs)


def mail(p: Pen, fill=False):
    flap = p.line([(3.8, 18.2), (12, 11.6), (20.2, 18.2)], cut="p")
    if fill:
        return minus(p.rect_solid(LO, 4.9, HI, 19.1), flap)
    return union(p.rect(LO, 4.9, HI, 19.1), flap)


def image(p: Pen, fill=False):
    hills = p.line([(LO, 6.4), (8.6, 15.2), (13.2, 8.6), (15.8, 11.2), (HI, 6.4)], cut="v")
    sun = region(superellipse(16.0, 15.4, 1.2 + p.h, 1.2 + p.h, p.k.circle))
    return union(p.rect(LO, 3.9, HI, 20.1), hills, sun)


def trash(p: Pen, fill=False):
    lid = p.bar((3.4, 17.6), (20.6, 17.6))
    handle = p.line([(9, 17.6), (9, 20.6), (15, 20.6), (15, 17.6)], cut="p", corners={1: p.radius_small, 2: p.radius_small})
    body = [(5.8, 17.6), (5.8, LO), (18.2, LO), (18.2, 17.6)]
    lines = union(p.bar((10, 6.6), (10, 13.6), cut="h"), p.bar((14, 6.6), (14, 13.6), cut="h"))
    if fill:
        solid = clip(p.rect_solid(5.8, LO, 18.2, 17.6 + 4), box(y1=17.6 - p.h - 0.9 * p.h))
        return union(lid, handle, minus(solid, lines))
    return union(lid, handle, p.line(body, cut="p", corners={1: p.radius, 2: p.radius}), lines)


def edit(p: Pen, fill=False):
    u, n = _u(45), _u(135)
    tip, hw = (3.8, 3.8), 2.4
    b, e = _at(tip, u, 4.2), _at(tip, u, 21.4)
    pts = [tip, _at(b, n, -hw), _at(e, n, -hw), _at(e, n, hw), _at(b, n, hw)]
    corners = {0: 0.5, 1: 0, 2: p.radius_small, 3: p.radius_small, 4: 0}
    f = _at(e, u, -4.2)
    band = p.bar(_at(f, n, hw), _at(f, n, -hw), cut="p")
    if fill:
        return minus(p.solid(pts, corners=corners), band)
    return union(p.frame(pts, corners=corners), band)


def download(p: Pen, fill=False):
    tray = p.line([(3.4, 10.2), (3.4, 3.4), (20.6, 3.4), (20.6, 10.2)], corners={1: p.radius, 2: p.radius})
    return union(p.bar((12, 20.8), (12, 7.6), cut=("h", "p")), p.line([(7, 12.6), (12, 7.6), (17, 12.6)]), tray)


def upload(p: Pen, fill=False):
    tray = p.line([(3.4, 10.2), (3.4, 3.4), (20.6, 3.4), (20.6, 10.2)], corners={1: p.radius, 2: p.radius})
    return union(p.bar((12, 7.4), (12, 20.4), cut=("h", "p")), p.line([(7, 15.4), (12, 20.4), (17, 15.4)]), tray)


def filter_(p: Pen, fill=False):
    pts = [(3.2, 19.6), (20.8, 19.6), (14.0, 11.2), (14.0, 3.6), (10.0, 5.8), (10.0, 11.2)]
    corners = {0: 1.5, 1: 1.5, 2: p.radius_small, 3: p.radius_small, 4: p.radius_small, 5: p.radius_small}
    return (p.solid if fill else p.frame)(pts, corners=corners)


def terminal(p: Pen, fill=False):
    prompt = union(p.line([(6.8, 15.2), (10.2, 11.8), (6.8, 8.4)]), p.bar((12.4, 8.4), (17.4, 8.4)))
    if fill:
        return minus(p.rect_solid(LO, 3.9, HI, 20.1), prompt)
    return union(p.rect(LO, 3.9, HI, 20.1), prompt)


# ------------------------------------------------------------- business
def chart_bar(p: Pen, fill=False):
    axis = p.line([(3.4, 21), (3.4, 3.4), (21, 3.4)])
    bars = [p.bar((x, 7.4), (x, top), cut="h") for x, top in ((8.4, 13.0), (13.0, 18.4), (17.6, 15.4))]
    return union(axis, *bars)


def activity(p: Pen, fill=False):
    return p.line([(2.6, 12), (7, 12), (9.6, 19), (14.4, 5), (17, 12), (21.4, 12)], cut="v")


def archive(p: Pen, fill=False):
    body = [(4.6, 15.2), (4.6, LO), (19.4, LO), (19.4, 15.2)]
    slot = p.bar((9.6, 10.8), (14.4, 10.8))
    if fill:
        lid = p.rect_solid(LO, 15.2, HI, 20.1, r=1.4)
        box_ = clip(p.rect_solid(4.6, LO, 19.4, 19), box(y1=15.2 - p.h - 0.9 * p.h))
        return union(lid, minus(box_, slot))
    return union(p.rect(LO, 15.2, HI, 20.1, r=1.4), p.line(body, cut="p", corners={1: p.radius, 2: p.radius}), slot)


def receipt(p: Pen, fill=False):
    xs = [4.9 + i * (19.1 - 4.9) / 6 for i in range(7)]
    teeth = [(x, 5.6 if i % 2 == 0 else 3.6) for i, x in enumerate(xs)]
    pts = [(19.1, HI), (4.9, HI)] + teeth
    corners = {i: 0 for i in range(len(pts))}
    corners.update({0: p.radius, 1: p.radius})
    lines = union(p.bar((8.6, 16.6), (15.4, 16.6)), p.bar((8.6, 12.4), (15.4, 12.4)), p.bar((8.6, 8.2), (12.2, 8.2)))
    if fill:
        return minus(p.solid(pts, corners=corners), lines)
    return union(p.frame(pts, corners=corners), lines)


@lru_cache(maxsize=None)
def _dong(master: str):
    """The ₫ of Porto Faifo Sans ``master`` as contours, and its stem width (font units)."""
    font = TTFont(ROOT / "fonts" / "otf" / f"PFSans-{master}.otf")
    rec = RecordingPen()
    font.getGlyphSet()["dong"].draw(rec)
    out, c = [], None
    for op, args in rec.value:
        if op == "moveTo":
            c = Contour(args[0])
        elif op == "lineTo":
            c.line(args[0])
        elif op == "curveTo":
            c.cubic(*args)
        elif op == "closePath":
            out.append(c.close())
    path = region(*out)
    x0, y0, x1, y1 = path.bounds
    # The stem alone, between the bowl and the crossbar of đ.
    y = y0 + 0.79 * (y1 - y0)
    strip = pathops.op(path, region(Contour((x0 - 10, y)).line((x1 + 10, y)).line((x1 + 10, y + 1)).line((x0 - 10, y + 1)).close()), pathops.PathOp.INTERSECTION)
    sx0, _, sx1, _ = strip.bounds
    return out, (x0, y0, x1, y1), sx1 - sx0


def coin_dong(p: Pen, fill=False):
    """The ₫ is the Porto Faifo Sans glyph, from the master whose stem comes closest
    to the icon stroke, emboldened by the remainder within limits that keep
    its counters open."""
    height, target = 11.2, p.w
    best = None
    for master in ("Light", "Regular", "Medium", "Bold"):
        cs, (x0, y0, x1, y1), stem = _dong(master)
        s = height / (y1 - y0)
        d = (target - stem * s) / 2
        if best is None or abs(d) < abs(best[0]):
            best = (d, cs, (x0, y0, x1, y1), s)
    d, cs, (x0, y0, x1, y1), s = best
    d = max(-0.3, min(0.22, d))
    placed = []
    for c in cs:
        c = c.translated(-(x0 + x1) / 2, -(y0 + y1) / 2).scaled(s, s).translated(12, 12)
        placed += untangled(c.offset(d)) if abs(d) > 1e-3 else [c]
    glyph = _even_odd(placed)
    if fill:
        return minus(p.disc(12, 12, R), glyph)
    return union(p.ring(12, 12, R), glyph)


def _even_odd(cs):
    """Glyph contours with counters: fill by direction, as the font does."""
    path = pathops.Path()
    for c in cs:
        c.draw(path.getPen(), round_to=0)
    return pathops.simplify(path)


def safe(p: Pen, fill=False):
    body = (LO, 4.6, HI, 20.2)
    feet = union(p.bar((6.4, 4.6), (6.4, 2.4), cut=("p", "h")), p.bar((17.6, 4.6), (17.6, 2.4), cut=("p", "h")))
    dial, rd = (10.4, 12.4), 3.9
    handle = p.bar((16.8, 9.6), (16.8, 15.2), cut="h")
    if fill:
        return union(minus(p.rect_solid(*body), p.ring(*dial, rd), handle), feet)
    pin = region(superellipse(*dial, p.dot_d * p.wr / p.w / 2, p.dot_d * p.wr / p.w / 2, p.k.circle))
    return union(p.rect(*body), feet, p.ring(*dial, rd), pin, handle)


# ------------------------------------------------------- files
def arrow_left(p: Pen, fill=False):
    return union(p.bar((20.2, 12), (4.4, 12), cut=("v", "p")), p.line([(11, 18.6), (4.4, 12), (11, 5.4)]))


def arrow_up(p: Pen, fill=False):
    return union(p.bar((12, 3.8), (12, 19.6), cut=("h", "p")), p.line([(5.4, 13), (12, 19.6), (18.6, 13)]))


def arrow_up_right(p: Pen, fill=False):
    return union(p.bar((5.6, 5.6), (18.2, 18.2), cut=("h", "p")), p.line([(9.4, 18.2), (18.2, 18.2), (18.2, 9.4)]))


def folder_add(p: Pen, fill=False):
    plus_ = union(p.bar((12, 7.6), (12, 13.6)), p.bar((9, 10.6), (15, 10.6)))
    if fill:
        return minus(folder(p, True), plus_)
    return union(folder(p), plus_)


def rename(p: Pen, fill=False):
    """A text field broken by an I-beam cursor; the field ends where the
    cursor cuts it, vertically, on the grid."""
    x = 15.6
    field = minus(p.rect(LO, 7.0, HI, 17.0), box(x - p.h - 1.0, -BIG, x + p.h + 1.0, BIG))
    cursor = union(p.bar((x, 3.4), (x, 20.6), cut="h"), p.bar((13.4, 20.6), (17.8, 20.6)), p.bar((13.4, 3.4), (17.8, 3.4)))
    return union(field, cursor, p.bar((6.6, 12), (10.8, 12)))


def cut(p: Pen, fill=False):
    rings = [(7.6, 6.4), (16.4, 6.4)]
    r = 2.8
    a = (rings[0][0] + r * math.cos(math.radians(60)), rings[0][1] + r * math.sin(math.radians(60)))
    b = (rings[1][0] - r * math.cos(math.radians(60)), a[1])
    blades = union(p.bar(a, (16.4, 20.6), cut=("p", "h")), p.bar(b, (7.6, 20.6), cut=("p", "h")))
    return union(*(p.ring(*c, r) for c in rings), blades)


def _front_knock(p: Pen, x0, y0, x1, y1, r, gap=1.2):
    """The silhouette of a front frame grown by a gap, to cut what lies behind."""
    return p.rect_solid(x0 - gap, y0 - gap, x1 + gap, y1 + gap, r + gap)


def copy(p: Pen, fill=False):
    front = (8.4, 3.4, 20.6, 15.6)
    back = minus(p.rect(3.4, 8.4, 15.6, 20.6), _front_knock(p, *front, p.radius))
    return union(back, (p.rect_solid if fill else p.rect)(*front))


def paste(p: Pen, fill=False):
    clip_ = (8.6, 17.4, 15.4, 21.0)
    board = minus((p.rect_solid if fill else p.rect)(4.6, LO, 19.4, 19.2), _front_knock(p, *clip_, p.radius_small, gap=1.0))
    return union(board, (p.rect_solid if fill else p.rect)(*clip_, r=p.radius_small))


def restore(p: Pen, fill=False):
    return mirrored(refresh(p))


def undo(p: Pen, fill=False):
    dx = 0.8
    top, bottom, cx, r = 14.6, 5.8, 14.0 + dx, 4.4
    return union(
        p.bar((4.4 + dx, top), (cx, top), cut="p"),
        p.arc(cx, (top + bottom) / 2, r, keep=box(x0=cx)),
        p.bar((cx, bottom), (8.6 + dx, bottom), cut=("p", "v")),
        p.line([(8.6 + dx, top + 4.2), (4.4 + dx, top), (8.6 + dx, top - 4.2)]),
    )


def redo(p: Pen, fill=False):
    return mirrored(undo(p))


def open_(p: Pen, fill=False):
    box_ = p.line([(11.0, 18.0), (4.4, 18.0), (4.4, 4.4), (18.0, 4.4), (18.0, 11.0)], corners={1: p.radius, 2: p.radius, 3: p.radius})
    arrow = union(p.bar((11.0, 11.0), (19.4, 19.4), cut=("h", "p")), p.line([(13.6, 19.4), (19.4, 19.4), (19.4, 13.6)]))
    return union(box_, arrow)


def panel_right(p: Pen, fill=False):
    frame = p.rect(LO, 3.9, HI, 20.1)
    divider = p.bar((15.2, 3.9), (15.2, 20.1), cut="p")
    if fill:
        side = clip(p.rect_solid(LO, 3.9, HI, 20.1), box(x0=15.2))
        return union(frame, divider, side)
    return union(frame, divider)


def view_list(p: Pen, fill=False):
    return union(*(union(p.dot(5.2, y, big=True), p.bar((9.4, y), (20.4, y))) for y in (6.4, 12, 17.6)))


def _sort(p: Pen, up: bool):
    tip, tail = (19.4, 4.4) if up else (4.6, 19.6)
    s = 1 if up else -1
    arrow = union(p.bar((7.2, tail), (7.2, tip), cut=("h", "p")), p.line([(4.0, tip - s * 3.2), (7.2, tip), (10.4, tip - s * 3.2)]))
    lengths = (16.0, 18.4, 20.8) if up else (20.8, 18.4, 16.0)
    bars = [p.bar((12.0, y), (x1, y)) for y, x1 in zip((17.6, 12, 6.4), lengths)]
    return union(arrow, *bars)


def sort_ascending(p: Pen, fill=False):
    return _sort(p, True)


def sort_descending(p: Pen, fill=False):
    return _sort(p, False)


def music(p: Pen, fill=False):
    """Two beamed notes; the heads are Porto Faifo ovals and grow with the stroke."""
    rx, ry = 2.0 + p.h, 1.5 + p.h
    heads = [(6.6, 5.8), (16.4, 7.4)]
    xs = [cx + rx - p.h for cx, _ in heads]
    thick = p.stroked(1.4 * p.w).bar((xs[0] - p.h, 18.8), (xs[1] + p.h, 20.4), cut="v")
    stems = union(*(p.bar((x, cy), (x, 19.4 if i == 0 else 21.0), cut="h") for i, (x, (_, cy)) in enumerate(zip(xs, heads))))
    ovals = union(*(region(superellipse(cx, cy, rx, ry, p.k.outer)) for cx, cy in heads))
    return union(ovals, stems, thick)


def video(p: Pen, fill=False):
    play = p.solid([(10.2, 8.8), (15.8, 12.0), (10.2, 15.2)], r=0.5)
    if fill:
        return minus(p.rect_solid(LO, 5.4, HI, 18.6), p.stroked(1.6 * p.w).solid([(10.2, 8.8), (15.8, 12.0), (10.2, 15.2)], r=0.5))
    return union(p.rect(LO, 5.4, HI, 18.6), play)


def code(p: Pen, fill=False):
    left = p.line([(8.2, 17.0), (3.6, 12.0), (8.2, 7.0)])
    right = p.line([(15.8, 17.0), (20.4, 12.0), (15.8, 7.0)])
    return union(left, right, p.bar((13.8, 19.6), (10.2, 4.4), cut="h"))


def computer(p: Pen, fill=False):
    """A laptop: screen and base.  The monitor on a stand is ``display``, so
    computer, display, drive and memory never share one drawing."""
    return union((p.rect_solid if fill else p.rect)(4.6, 8.6, 19.4, 19.6), p.bar((LO, 4.6), (HI, 4.6)))


def drive(p: Pen, fill=False):
    body = (LO, 5.4, HI, 18.6)
    band = union(p.bar((LO, 11.0), (HI, 11.0), cut="p"))
    slot = p.bar((6.6, 8.2), (11.6, 8.2))
    led = p.dot(17.2, 8.2, big=True)
    if fill:
        return minus(p.rect_solid(*body), band, slot, p.stroked(1.6 * p.w).dot(17.2, 8.2, big=True))
    return union(p.rect(*body), band, slot, led)


def usb(p: Pen, fill=False):
    body = (6.4, LO, 17.6, 14.6)
    plug = p.line([(9.0, 14.6), (9.0, HI), (15.0, HI), (15.0, 14.6)], cut="p")
    return union((p.rect_solid if fill else p.rect)(*body), plug)


def eject(p: Pen, fill=False):
    tri = [(12, 20.2), (3.8, 10.6), (20.2, 10.6)]
    return union((p.solid if fill else p.frame)(tri, r=1.0), p.bar((4.2, 5.2), (19.8, 5.2)))


def table(p: Pen, fill=False):
    frame = (LO, 3.9, HI, 20.1)
    rows = union(p.bar((LO, 14.6), (HI, 14.6), cut="p"), p.bar((LO, 9.2), (HI, 9.2), cut="p"))
    col = p.bar((9.4, 3.9), (9.4, 20.1), cut="p")
    if fill:
        head = clip(p.rect_solid(*frame), box(y0=14.6))
        return union(p.rect(*frame), head, rows, col)
    return union(p.rect(*frame), rows, col)


def presentation(p: Pen, fill=False):
    board = (LO, 7.8, HI, 20.4)
    leg = union(p.bar((12, 7.8), (12, 3.0), cut=("p", "h")), p.bar((8.4, 3.0), (15.6, 3.0)))
    bars = union(*(p.bar((x, 11.0), (x, top), cut="h") for x, top in ((8.0, 14.0), (12.0, 17.0), (16.0, 15.4))))
    if fill:
        return union(minus(p.rect_solid(*board), bars), leg)
    return union(p.rect(*board), leg, bars)


def window_minimize(p: Pen, fill=False):
    return p.bar((5.4, 7.4), (18.6, 7.4))


def window_maximize(p: Pen, fill=False):
    return p.rect(5.0, 5.0, 19.0, 19.0, r=p.radius_small)


def window_restore(p: Pen, fill=False):
    front = (5.0, 5.0, 16.0, 16.0)
    back = minus(p.rect(8.0, 8.0, 19.0, 19.0, r=p.radius_small), _front_knock(p, *front, p.radius_small))
    return union(back, p.rect(*front, r=p.radius_small))


# ---------------------------------------------------------------- registry
@dataclass
class Icon:
    name: str
    draw: Callable
    group: str
    lucide: str
    fdo: str = ""
    fdo_source: str = ""  # "spec" | "gnome" (Adwaita) | "kde" (Breeze) | "xdg" | "mime"
    context: str = "actions"
    fill: bool = False
    note: str = ""
    aliases: list = field(default_factory=list)  # other codes for the same glyph
    fdo_more: list = field(default_factory=list)  # extra freedesktop names (same context)
    ghost: Callable | None = None  # second layer at GHOST_OPACITY (levels above the current one)
    meaning: str = ""  # what the code means in the UI, in Vietnamese
    since: str = "0.1.0"


ICONS = [
    Icon("search", search, "Navigation", "search", "system-search", "spec", "actions", note="The ring is the Porto Faifo oval (0.59); the handle is cut horizontally on the grid."),
    Icon("plus", plus, "Navigation", "plus", "list-add", "spec", note="Same math axis as the + of Porto Faifo Sans."),
    Icon("minus", minus_, "Navigation", "minus", "list-remove", "spec"),
    Icon("close", close, "Navigation", "x", "window-close", "spec", note="Stroke ends cut horizontally, as on the letter x.", aliases=["window-close"]),
    Icon("check", check, "Navigation", "check", "object-select", "gnome"),
    Icon("chevron-right", chevron_right, "Navigation", "chevron-right", "pan-end", "gnome", note="Sharp apex and horizontal cuts, like the font's > sign."),
    Icon("chevron-left", chevron_left, "Navigation", "chevron-left", "pan-start", "gnome"),
    Icon("chevron-down", chevron_down, "Navigation", "chevron-down", "pan-down", "gnome"),
    Icon("chevron-up", chevron_up, "Navigation", "chevron-up", "pan-up", "gnome"),
    Icon("arrow-right", arrow_right, "Navigation", "arrow-right", "go-next", "spec"),
    Icon("menu", menu, "Navigation", "menu", "open-menu", "gnome"),
    Icon("more", more, "Navigation", "ellipsis", "view-more-horizontal", "gnome", note="Standalone dot = dot of i × 1.3.", aliases=["more-horizontal"]),
    Icon("home", home, "Navigation", "house", "go-home", "spec", "actions", fill=True),
    Icon("user", user, "Navigation", "user", "avatar-default", "gnome", "status", fill=True),
    Icon("settings", settings, "Navigation", "settings", "preferences-system", "spec", "categories", fill=True),
    Icon("apps", apps, "Navigation", "layout-grid", "view-app-grid", "gnome", fill=True, aliases=["view-grid"], fdo_more=["view-grid"]),
    Icon("bell", bell, "Status", "bell", "preferences-system-notifications", "gnome", "status", fill=True),
    Icon("info", info, "Status", "info", "dialog-information", "spec", "status", fill=True, note="The letter i with the exact 1.32-stroke dot and 0.2 gap of Porto Faifo Sans."),
    Icon("warning", warning, "Status", "triangle-alert", "dialog-warning", "spec", "status", fill=True),
    Icon("lock", lock, "Status", "lock", "system-lock-screen", "spec", fill=True),
    Icon("clock", clock, "Status", "clock", "preferences-system-time", "gnome", "categories", fill=True),
    Icon("star", star, "Status", "star", "starred", "gnome", "status", fill=True),
    Icon("power", power, "System", "power", "system-shutdown", "spec"),
    Icon("wifi", wifi, "System", "wifi", "network-wireless", "spec", "devices", note="Arcs cut horizontally on the grid, like the aperture of c. Also the strongest signal level (81–100%).", aliases=["wifi-high"],
         fdo_more=["network-wireless-signal-excellent"]),
    Icon("battery", battery, "System", "battery-medium", "battery", "spec", "devices", note="Also the medium level (31–79%) of the battery-* family.", aliases=["battery-medium"],
         fdo_more=["battery-good"]),
    Icon("volume", volume, "System", "volume-2", "audio-volume-high", "spec", "status", note="Also the high volume level (50–100%). audio-volume-medium uses the volume-low drawing (0.5.1).", aliases=["volume-high"]),
    Icon("refresh", refresh, "System", "rotate-cw", "view-refresh", "spec", note="retry shares this drawing: to retry is to reload the action.", aliases=["retry"]),
    Icon("terminal", terminal, "System", "square-terminal", "utilities-terminal", "spec", "apps", fill=True),
    Icon("file", file, "Documents", "file", "text-x-generic", "spec", "mimetypes", fill=True),
    Icon("file-text", file_text, "Documents", "file-text", "x-office-document", "spec", "mimetypes", fill=True, aliases=["document"]),
    Icon("folder", folder, "Documents", "folder", "folder", "spec", "places", fill=True),
    Icon("calendar", calendar, "Documents", "calendar", "x-office-calendar", "spec", "mimetypes", fill=True),
    Icon("mail", mail, "Documents", "mail", "mail-unread", "spec", "status", fill=True),
    Icon("image", image, "Documents", "image", "image-x-generic", "spec", "mimetypes", note="A peak sharper than 70°, so it ends flat like the apex of A."),
    Icon("trash", trash, "Documents", "trash-2", "user-trash", "spec", "places", fill=True, aliases=["delete"], fdo_more=["edit-delete"]),
    Icon("edit", edit, "Documents", "pencil", "document-edit", "gnome", fill=True),
    Icon("download", download, "Documents", "download", "folder-download", "xdg", "places",
         note="Since 0.2.0 document-save belongs to save; the freedesktop name here is the Downloads folder."),
    Icon("upload", upload, "Documents", "upload", "document-send", "spec"),
    Icon("filter", filter_, "Documents", "funnel", "", "", fill=True),
    Icon("chart-bar", chart_bar, "Business", "chart-column", "", "", note="The axis is a sharp right angle, like the letter L."),
    Icon("activity", activity, "Business", "activity", "utilities-system-monitor", "spec", "apps", note="Two 39° apexes end flat like the apex of A and the foot of V."),
    Icon("archive", archive, "Business", "archive", "application-x-archive", "mime", "mimetypes", fill=True, note="An archive box with a lid; an application package is package."),
    Icon("receipt", receipt, "Business", "receipt", "", "", fill=True),
    Icon("coin-dong", coin_dong, "Business", "", "", "", fill=True, note="₫ is the glyph from Porto Faifo Sans, taken from the master that matches the icon weight."),
    Icon("safe", safe, "Business", "vault", "", "", fill=True, note="A safe: the signature icon of Két Việt (két means safe)."),
    # File manager
    Icon("arrow-left", arrow_left, "Files · actions", "arrow-left", "go-previous", "spec", note="Go back."),
    Icon("arrow-up", arrow_up, "Files · actions", "arrow-up", "go-up", "spec", note="Parent folder."),
    Icon("arrow-up-right", arrow_up_right, "Files · actions", "arrow-up-right", "", "", note="Shortcut; also the mark of badge-shortcut."),
    Icon("folder-add", folder_add, "Files · actions", "folder-plus", "folder-new", "spec", fill=True),
    Icon("rename", rename, "Files · actions", "text-cursor-input", "edit-rename", "kde", note="A text field cut by the cursor along the grid."),
    Icon("cut", cut, "Files · actions", "scissors", "edit-cut", "spec"),
    Icon("copy", copy, "Files · actions", "copy", "edit-copy", "spec", fill=True),
    Icon("paste", paste, "Files · actions", "clipboard", "edit-paste", "spec", fill=True),
    Icon("restore", restore, "Files · actions", "rotate-ccw", "", "", note="Restore from the trash: refresh mirrored."),
    Icon("undo", undo, "Files · actions", "undo-2", "edit-undo", "spec"),
    Icon("redo", redo, "Files · actions", "redo-2", "edit-redo", "spec"),
    Icon("open", open_, "Files · actions", "square-arrow-out-up-right", "document-open", "spec", note="external-link shares this drawing: the same meaning of opening outside the app.", aliases=["external-link"]),
    Icon("panel-right", panel_right, "Files · actions", "panel-right", "", "", fill=True, note="Toggle the details pane; filled = open."),
    Icon("view-list", view_list, "Files · actions", "list", "view-list", "gnome"),
    Icon("sort-ascending", sort_ascending, "Files · actions", "arrow-up-narrow-wide", "view-sort-ascending", "spec"),
    Icon("sort-descending", sort_descending, "Files · actions", "arrow-down-wide-narrow", "view-sort-descending", "spec"),
    Icon("eject", eject, "Files · actions", "", "media-eject", "spec", fill=True, note="Eject safely."),
    Icon("music", music, "Files · locations", "music", "folder-music", "gnome", "places", note="The note head is the Porto Faifo oval, scaled with the stroke."),
    Icon("video", video, "Files · locations", "square-play", "folder-videos", "gnome", "places", fill=True),
    Icon("code", code, "Files · locations", "code-xml", "", "", note="Project / source code."),
    Icon("computer", computer, "Files · locations", "laptop", "computer", "spec", "devices", fill=True, note="A laptop since 0.2.0; a screen on a stand is display."),
    Icon("drive", drive, "Files · locations", "hard-drive", "drive-harddisk", "spec", "devices", fill=True),
    Icon("usb", usb, "Files · locations", "usb", "drive-removable-media", "spec", "devices", fill=True, note="A USB stick, not the trident symbol."),
    Icon("table", table, "Files · locations", "sheet", "x-office-spreadsheet", "spec", "mimetypes", fill=True),
    Icon("presentation", presentation, "Files · locations", "presentation", "x-office-presentation", "spec", "mimetypes", fill=True),
    Icon("window-minimize", window_minimize, "Windows", "", "window-minimize", "gnome", note="Window glyphs shown at 11–12 px: use Medium or Bold."),
    Icon("window-maximize", window_maximize, "Windows", "", "window-maximize", "gnome"),
    Icon("window-restore", window_restore, "Windows", "", "window-restore", "gnome"),
]

ALIASES = {alias: icon.name for icon in ICONS for alias in icon.aliases}
