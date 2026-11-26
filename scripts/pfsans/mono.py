"""Porto Faifo Mono: the proportional recipes on one fixed advance.

Two steps, both driven by ``design-system.json`` ``mono``:

1. ``MonoMixin`` redraws the letters that are too narrow for a cell.  They
   keep the Porto Faifo pen and gain what every monospace needs to fill the cell and
   to tell 1 l I i apart:

       i ı   stem with a spur to the left at the x-height, a slab foot
       j ȷ   the same spur over the descender hook
       l     spur at the ascender, the t tail as its foot
       f t   bars reaching both ways, longer hooks
       r     the wide arm of a wider arch, no slab
       I     slabs top and foot
       1     the flag over a slab foot
       0     the slash across the counter, by default
       W w M the middle apex lowered (W, w) or raised (M), inner strokes
             lighter, so four diagonals in one cell do not meet in a blot
       A V N K k v y 4 * # @  lighter diagonals and spokes (``LIGHTER``)

   A cell is narrower than the proportional letter, so its diagonals stand
   steeper at the same pen and their joins pile up into dark spots at text
   sizes.  build/clot_audit.py measures that: the blurred peak of each glyph
   against a plain stem, next to JetBrains Mono and SF Mono.

2. ``monospace`` puts every spacing glyph on the advance.  Glyphs keep the
   balance of their own sidebearings (n stays a touch left of centre, as its
   stems are); glyphs drawn here are centred on their outline.  A glyph wider
   than the cell less ``minSidebearing`` either side is condensed about its
   centre and reported.
"""

from __future__ import annotations

import math

from .geometry import intersect_lines, offset_line, polygon, rect, shared_foot, stroke
from .glyphs import Glyph
from .system import Namespace
from .upper import hcut_centre


class MonoMixin:
    @property
    def adv(self) -> int:
        return self.sys.raw["mono"]["advance"]

    @property
    def slab(self):
        return self.sys.raw["mono"]["slab"]

    def _cell(self, name, unis, cs, anchors, note) -> Glyph:
        """A glyph drawn here, centred on its outline in the cell."""
        g = Glyph(name, unis, self.adv, cs, note=note)
        g.anchors = anchors
        x0 = min(c.bounds()[0] for c in cs)
        x1 = max(c.bounds()[2] for c in cs)
        g.lib_centred = True
        return g.shifted(self.adv / 2 - (x0 + x1) / 2)

    # ------------------------------------------------------------------ i ı j ȷ
    def _spur(self, x_stem, top):
        b = self.st.barLower
        return rect(x_stem - self.slab["spur"], top - b, x_stem + 10, top)

    def _foot(self, cx, width=None, thick=None):
        w = width or self.slab["slab"]
        return rect(cx - w / 2, 0, cx + w / 2, thick or self.st.barLower)

    def _i(self, name, unis, dot):
        S, X = self.st.stemLower, self.xh
        sx = 40  # stem a touch right of the foot's centre: the spur weighs on the left
        cs = [rect(sx, 0, sx + S, X), self._spur(sx, X), self._foot(S / 2)]
        if dot:
            cs.append(self.dot(sx + S / 2, X + self.sh.dotGap * X))
        anchors = {"top": (sx + S / 2, X), "bottom": (S / 2, 0), "ogonek": (S / 2 + self.slab["slab"] / 2 - 80, 0)}
        return self._cell(name, unis, cs, anchors, "mono: n stem + spur + slab foot" + (" + round dot" if dot else ""))

    def i(self):
        return self._i("i", [0x69], True)

    def dotlessi(self):
        return self._i("dotlessi", [0x131], False)

    def dotlessj(self):
        st, X, D = self.st, self.xh, self.desc
        S, x0 = st.stemLower, 0
        hook = self.hook_stem(x0, S, X, D, 330, 370, 96, 80, x0 + S + 330, st.barLower, self.ox)
        hook = hook.mirrored_x(x0 + S / 2).oriented(True)
        anchors = {"top": (x0 + S / 2, X), "bottom": (x0 + S / 2, 0)}
        return self._cell("dotlessj", [0x237], [hook, self._spur(x0, X)], anchors, "mono: ı spur over the j hook")

    def j(self):
        g = self.dotlessj()
        x = g.anchors["top"][0]
        g.contours.append(self.dot(x, self.xh + self.sh.dotGap * self.xh))
        g.name, g.unicodes, g.note = "j", [0x6A], "mono: dotless j + i dot"
        return g

    # ------------------------------------------------------------------- l f t
    def l(self):
        st, X, A = self.st, self.xh, self.asc
        S, x0 = st.stemLower, 0
        bend = self.sh.tHookBend * X
        tail = self.hook_stem(x0, S, A, 0, bend, bend + 0.05 * X, 150, 132, x0 + S + 330, st.barLower + 2, self.ox)
        anchors = {"top": (x0 + S / 2, A), "bottom": (x0 + S / 2 + 60, 0), "topright": (x0 + S + 50, A)}
        return self._cell("l", [0x6C], [tail, self._spur(x0, A)], anchors, "mono: spur at the ascender + t tail")

    def f(self):
        st, X, A = self.st, self.xh, self.asc
        S, x0 = st.stemLower, 0
        bend = self.sh.tHookBend * X
        hook = self.hook_stem(x0, S, A, 0, bend, bend + 0.05 * X, 170, 150, x0 + S + 360, st.archTop - 2, self.ox)
        hook = hook.mirrored_y(A / 2).oriented(True)
        bar = rect(x0 - 300, X - st.barLower, x0 + S + 300, X)
        anchors = {"top": (x0 + S / 2 + 60, X), "bottom": (x0 + S / 2, 0)}
        return self._cell("f", [0x66], [hook, bar], anchors, "mono: t hook mirrored to the ascender; bar both ways")

    def t(self):
        st, X = self.st, self.xh
        S, x0 = st.stemLower, 0
        top = round(self.sh.tTop * self.asc)
        bend = self.sh.tHookBend * X
        stem = self.hook_stem(x0, S, top, 0, bend, bend + 0.05 * X, 150, 132, x0 + S + 300, st.barLower + 2, self.ox)
        bar = rect(x0 - 300, X - st.barLower, x0 + S + 300, X)
        anchors = {"top": (x0 + S / 2, top), "bottom": (x0 + S / 2 + 60, 0), "topright": (x0 + S + 90, self.asc)}
        return self._cell("t", [0x74], [bar, stem], anchors, "mono: stem + bar both ways; u-like hook")

    # ----------------------------------------------------------------------- r
    # A slab-footed r looks odd in code; of foot, spur and
    # plain side by side, the plain wide arch reads as an r.
    R_STYLE = "plain"  # "plain": wider arch only; "foot": slab foot; "spur": i's spur

    def r(self):
        style = self.R_STYLE
        widths = {"r": self.wd.r + 60} if style == "plain" else {}
        with self._drawn_at(1.0, **widths):
            g = super().r()
        S, x = self.st.stemLower, self.sp.lowerStraight
        cs = [c.translated(-x, 0) for c in g.contours]
        if style == "foot":
            cs.append(self._foot(S / 2, self.slab["slab"] - 120))
        elif style == "spur":
            cs.append(self._spur(0, self.xh))
        anchors = {k: (v[0] - x, v[1]) for k, v in g.anchors.items()}
        return self._cell("r", [0x72], cs, anchors, f"mono: n arch cut wide ({style})")

    # ------------------------------------------------------------------- I 1 0
    def I(self):
        S, C, B = self.st.stemUpper, self.cap, self.st.barUpper
        w = self.slab["capSlab"]
        cs = [rect(-S / 2, 0, S / 2, C), rect(-w / 2, C - B, w / 2, C), rect(-w / 2, 0, w / 2, B)]
        anchors = {"top": (0, C), "bottom": (0, 0), "ogonek": (w / 2 - 80, 0)}
        return self._cell("I", [0x49], cs, anchors, "mono: H stem + slabs top and foot")

    def one(self):
        g = super().one()
        stem = g.contours[0].bounds()
        cx = (stem[0] + stem[2]) / 2
        w = self.slab["capSlab"]
        cs = list(g.contours) + [rect(cx - w / 2, 0, cx + w / 2, self.st.figureTop)]
        return self._cell("one", [0x31], cs, {}, "mono: H stem + straight flag + slab foot")

    def zero(self):
        g = super().zero()
        st, W, C = self.st, self.wd.figure, self.sys.m.figureHeight
        cx = g.width / 2
        rx, ry = W / 2 - st.figureSide, C / 2 + self.of - st.figureTop
        a = math.radians(58)
        ux, uy = math.cos(a), math.sin(a)
        r = 1 / math.hypot(ux / rx, uy / ry) + 30
        p, q = (cx - r * ux, C / 2 - r * uy), (cx + r * ux, C / 2 + r * uy)
        g.contours.append(stroke(p, q, st.punctStroke * ZERO_SLASH, "p"))
        g.note = "mono: 0 + slash across the counter, by default"
        return g

    def zero_slash(self):
        g = self.zero()
        return Glyph("zero.zero", [], g.width, list(g.contours), note="mono: the default zero is already slashed")

    # ------------------------------------------------- joins without blots
    def _lighter(self, name, factors):
        """The proportional recipe with some strokes scaled by ``factors``."""
        st = self.st
        self.st = Namespace({**st, **{k: st[k] * f for k, f in factors.items()}})
        try:
            return getattr(super(MonoMixin, self), name)()
        finally:
            self.st = st

    def A(self):
        return self._lighter("A", LIGHTER["A"])

    def V(self):
        return self._lighter("V", LIGHTER["V"])

    def N(self):
        return self._lighter("N", LIGHTER["N"])

    def _arm_leg(self, S, H, W, t_a, t_l, reach):
        """The K arm and leg, the arm rooted on the stem's right half rather
        than its centre line, so the crotch against the stem stays open."""
        root = (S * ROOT, self.sh.KArmRoot * H)
        tip = hcut_centre(root, W, H, t_a, +1)
        arm = stroke(root, tip, t_a, cut=("p", "h"))
        j = (root[0] + (tip[0] - root[0]) * 0.42, root[1] + (tip[1] - root[1]) * 0.42)
        leg = stroke(j, hcut_centre(j, W + reach, 0, t_l, +1), t_l, cut=("p", "h"))
        return arm, leg

    def K(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, t = self.wd.K, st.stemUpper, st.diagonalUpper * LIGHTER["K"]["diagonalUpper"]
        arm, leg = self._arm_leg(S, C, W, t - 10, t, 30)
        return self._cap_glyph("K", 0x4B, W + 30, [rect(0, 0, S, C), arm, leg], sp.upperStraight, sp.upperDiagonal + 6,
                               "mono: lighter arm and leg rooted on the stem's right half")

    def k(self):
        st, X, A, sp = self.st, self.xh, self.asc, self.sp
        W, S, t = self.wd.k, st.stemLower, st.diagonalLower * LIGHTER["k"]["diagonalLower"]
        arm, leg = self._arm_leg(S, X, W - 10, t - 6, t, 30)
        return self._lc("k", 0x6B, W + 20, [rect(0, 0, S, A), arm, leg], sp.lowerStraight, sp.lowerDiagonal,
                        "mono: lighter arm and leg rooted on the stem's right half", {"top": (S / 2, A), "bottom": (W * 0.45, 0)})

    def Y(self):
        return self._lighter("Y", LIGHTER["Y"])

    def percent(self):
        return self._lighter("percent", LIGHTER["percent"])

    def numbersign(self):
        C = self.cap
        W, t_v, t_h, sl = 1000, 160 * self.wk * HASH, 150 * self.wk * HASH, 60
        cs = [stroke((x - sl, 0), (x + sl, C), t_v) for x in (0.34 * W, 0.68 * W)]
        cs += [rect(0.04 * W, y - t_h / 2, 0.98 * W, y + t_h / 2) for y in (0.33 * C, 0.65 * C)]
        adv = self.wd.tabularAdvance
        return self._g("numbersign", 0x23, adv, cs, f"mono: slanted stems and bars x{HASH}", (adv - W) / 2)

    def four(self):
        st = self.st
        W, C = self.wd.figure, self._F
        S, tb = st.figureStem, (st.figureTop + 4) * 0.9
        xs, yb, t, reach = 0.64 * W, 0.215 * C, st.figureStem * FOUR_DIAG, 34
        p, q = (0, yb + tb), (xs, C)
        inner = offset_line(p, q, -t)
        y_i = intersect_lines(*inner, (xs, 0), (xs, C))[1]
        x_bi = intersect_lines(*inner, (0, yb + tb), (W, yb + tb))[0]
        diag = polygon([p, q, (xs, y_i), (x_bi, yb + tb)]).oriented(True)
        cs = [rect(xs, 0, xs + S, C), rect(0, yb, W + reach, yb + tb), diag]
        cs = [c.translated(-reach / 2, 0) for c in cs]
        return self._fig("four", 0x34, cs, f"mono: closed 4, diagonal x{FOUR_DIAG}, bar x0.9")

    def v(self):
        return self._lighter("v", LIGHTER["v"])

    def y(self):
        return self._lighter("y", LIGHTER["y"])

    def asterisk(self):
        return self._lighter("asterisk", LIGHTER["asterisk"])

    def at(self):
        return self._lighter("at", LIGHTER["at"])

    def _double_v(self, W, H, t, apex, inner):
        """Two V sharing the middle apex at ``apex`` x ``H``: outer strokes
        at ``t``, inner ones at ``inner`` x ``t``."""
        b, c, d = 0.25 * W, 0.5 * W, 0.75 * W
        ti = t * inner
        a = hcut_centre((b, 0), 0, H, t, -1)
        e = hcut_centre((d, 0), W, H, t, +1)
        top = (c, apex * H)
        return (shared_foot([stroke(a, (b, 0), t), stroke((b, 0), top, ti)])
                + shared_foot([stroke(top, (d, 0), ti), stroke((d, 0), e, t)]))

    def W(self):
        st, C, sp = self.st, self.cap, self.sp
        cs = self._double_v(self.wd.W, C, (st.diagonalUpper - 12) * OUTER, MID["W"], INNER)
        return self._cap_glyph("W", 0x57, self.wd.W, cs, sp.upperDiagonal, sp.upperDiagonal,
                               f"mono: middle apex at {MID['W']} cap, inner strokes x{INNER}")

    def w(self):
        st, X, sp = self.st, self.xh, self.sp
        cs = self._double_v(self.wd.w, X, (st.diagonalLower - 12) * OUTER, MID["w"], INNER)
        return self._lc("w", 0x77, self.wd.w, cs, sp.lowerDiagonal, sp.lowerDiagonal,
                        f"mono: middle apex at {MID['w']} x-height, inner strokes x{INNER}")

    def M(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, t = self.wd.M, st.stemN, st.diagonalM * INNER
        v = MID["M"] * C  # the vertex stands off the baseline
        wh = t
        for _ in range(30):
            wh = t / math.sin(math.atan2(C - v, W / 2 - wh / 2))
        left = polygon([(0, C), (wh, C), (W / 2 + wh / 2, v), (W / 2 - wh / 2, v)]).oriented(True)
        right = left.mirrored_x(W / 2).oriented(True)
        cs = [rect(0, 0, S, C), rect(W - S, 0, W, C), left, right]
        return self._cap_glyph("M", 0x4D, W, cs, sp.upperStraight - 4, sp.upperStraight - 4,
                               f"mono: N stems; diagonals x{INNER} meet in a flat vertex at {MID['M']} cap")

    # ------------------------------------------------- two letters in one cell
    # Ligature letters and two-part signs are drawn from narrower parts with a
    # lighter pen, rather than squeezed: squeezing thins the uprights and
    # fills the counters.
    def AE(self):
        with self._drawn_at(0.88, E=500):
            return super().AE()

    def OE(self):
        with self._drawn_at(0.88, E=500):
            return super().OE()

    def ae(self):
        with self._drawn_at(0.86, a=560, e=600):
            return super().ae()

    def oe(self):
        with self._drawn_at(0.86, o=600, e=600):
            return super().oe()

    def rupee(self):
        with self._drawn_at(0.86, R=600, s=520):
            return super().rupee()

    def numero(self):
        with self._drawn_at(0.88, N=540):
            return super().numero()

    def _vulgar(self, name, uni, num, den):
        """Numerator and denominator staggered about the fraction slash in
        one cell: they may pass each other where they do not meet in height."""
        figs = self.small_figures()

        def flat(name):
            g = figs[name]
            return list(g.contours) + [c.translated(dx, dy) for base, dx, dy in g.components for c in flat(base)]

        n, d, sl = flat(f"{num}.numr"), flat(f"{den}.dnom"), self.fraction().contours

        def box(cs):
            bs = [c.bounds() for c in cs]
            return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)

        bn, bd, bs = box(n), box(d), box(sl)
        cx = self.adv / 2
        gap = bn[1] - bd[3]  # white between the denominator top and the numerator foot
        ov = 70 if gap > 40 else -40
        cs = ([c.translated(cx + ov - bn[2], 0) for c in n]
              + [c.translated(cx - (bs[0] + bs[2]) / 2, 0) for c in sl]
              + [c.translated(cx - ov - bd[0], 0) for c in d])
        x0, y0, x1, y1 = box(cs)
        room = self.adv - 2 * self.sys.raw["mono"]["minSidebearing"]
        s = min(1.0, room / (x1 - x0))
        mid = (x0 + x1) / 2
        cs = [c.translated(cx - mid, 0).scaled(s, s, cx, (y0 + y1) / 2) for c in cs]
        return Glyph(name, [uni], self.adv, cs, note=f"mono: {num}.numr / {den}.dnom staggered in one cell (x{s:.2f})")

    def perthousand(self):
        with self._drawn_at(1.0, percent=680, percentRing=228, percentRingHeight=460):
            return super().perthousand()


# ------------------------------------------------------------------ the cell
# Shapes that must keep their proportions shrink in both directions; letters
# and signs that are wider than a cell are condensed instead.
# Mono joins (see the docstring): the middle apex of W and w as a share of
# their height, the vertex of M off the baseline, the weight of the inner
# strokes, and the strokes drawn lighter in the other letters.
MID = {"W": 0.70, "w": 0.76, "M": 0.30}
INNER, OUTER = 0.74, 0.92
ROOT = 0.8  # K arm root across the stem (the proportional K roots at 0.5)
HASH, FOUR_DIAG, ZERO_SLASH = 0.84, 0.64, 0.78
LIGHTER = {
    "A": {"diagonalUpper": 0.88}, "V": {"diagonalUpper": 0.88}, "N": {"diagonalN": 0.80},
    "K": {"diagonalUpper": 0.86}, "k": {"diagonalLower": 0.86},
    "v": {"diagonalLower": 0.92}, "y": {"diagonalLower": 0.92},
    "Y": {"diagonalUpper": 0.88}, "percent": {"punctStroke": 0.8},
    "asterisk": {"punctStroke": 0.85}, "at": {"hairStroke": 0.85},
}

UNIFORM = ("Square", "Triangle", "Diamond", "Circle", "Arrow", "emptyset", "circled", "copyright", "registered")
BARS = ("emdash",)  # no upright strokes to give weight back to

def _bounds(name, glyphs, cache):
    if name in cache:
        return cache[name]
    g = glyphs[name]
    boxes = [c.bounds() for c in g.contours]
    for base, dx, dy in g.components:
        b = _bounds(base, glyphs, cache)
        if b:
            boxes.append((b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy))
    cache[name] = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)) if boxes else None
    return cache[name]


def monospace(glyphs: dict[str, Glyph], system) -> list[str]:
    """Every glyph with an advance onto the mono advance, in place.  Returns
    the glyphs that had to be condensed to fit, with their factor."""
    adv, margin = system.raw["mono"]["advance"], system.raw["mono"]["minSidebearing"]
    cache: dict = {}
    boxes = {n: _bounds(n, glyphs, cache) for n in glyphs}
    delta, scale = {}, {}
    for name, g in glyphs.items():
        if g.width == 0:
            delta[name] = 0.0
            continue
        if getattr(g, "lib_centred", False) or g.width == adv:
            delta[name] = 0.0
        else:
            delta[name] = (adv - g.width) / 2
        b = boxes[name]
        if b and not g.components:
            x0, x1 = b[0] + delta[name], b[2] + delta[name]
            room = adv - 2 * margin
            if x1 - x0 > room:
                if any(k in name for k in UNIFORM + BARS):
                    scale[name] = room / (x1 - x0)
                else:  # the offset below adds stem (1 - s) / 2 to the width
                    h = system.st.stemLower / 2
                    scale[name] = (room - h) / (x1 - x0 - h)
            elif x0 < margin or x1 > adv - margin:
                delta[name] += adv / 2 - (x0 + x1) / 2
    report = []
    for name, g in glyphs.items():
        d = delta[name]
        g.contours = [c.translated(d, 0) for c in g.contours]
        g.components = [(base, dx + d - delta.get(base, 0.0), dy) for base, dx, dy in g.components]
        g.anchors = {k: (v[0] + d, v[1]) for k, v in g.anchors.items()}
        if name in scale:
            s, cx = scale[name], adv / 2
            mid = (boxes[name][0] + boxes[name][2]) / 2 + d
            cy = (boxes[name][1] + boxes[name][3]) / 2
            uniform = any(k in name for k in UNIFORM)
            sy = s if uniform else 1
            moved = [c.translated(cx - mid, 0).scaled(s, sy, cx, cy) for c in g.contours]
            if not uniform and not any(k in name for k in BARS):
                # Give back half the stem the squeeze took: verticals end at
                # 1 - (1 - s) / 2 of the pen, horizontals gain as much.
                e = system.st.stemLower * (1 - s) / 4
                moved = [c.offset(e) for c in moved]
            g.contours = moved
            g.anchors = {k: (cx + (v[0] - mid) * s, cy + (v[1] - cy) * sy) for k, v in g.anchors.items()}
            report.append(f"{name} x{s:.2f}" + (" (uniform)" if uniform else ""))
        if g.width:
            g.width = adv
    return report
