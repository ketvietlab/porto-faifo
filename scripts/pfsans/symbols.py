"""GF Latin Plus symbols, built from the letter, figure and punctuation masters.

    small figures        ⁰–⁹ ₀–₉ and the .numr / .dnom figures of ``frac``: the
                         figures drawn at the small stroke, then scaled (as ª)
    fractions            ⁄ ¼ ½ ¾ ⅓ ⅔ (numerator + fraction slash + denominator)
    math                 ± ¬ ≠ ≤ ≥ ≈ on the math axis and tabular advance, like
                         + − = < >; √ ∑ tabular; ∞ ∂ ∅ ∆ ∏ ∫ µ π Ω ℓ
    arrows               ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙: punctStroke shaft and a 90° open
                         head, so the diagonal heads run along the axes
    currency             ฿ ₡ ₦ ₪ ₭ ₮ ₱ ₲ ₴ ₵ ₸ ₹ ₺ ₼ ₽ ₾ ₿ narrowed letters on the
                         tabular advance, like $ € ₫; ₩ ₨ keep the letter widths
    geometric shapes     ■ □ ▲ △ ▶ ▷ ▼ ▽ ◀ ◁ ◆ ◇ ◊ ○ ● on the cap height; the
                         small ones (▪ ▫ ▴ ▵ ▸ ▹ ▾ ▿ ◂ ◃ ◦) on the bullet
    marks                ¦ ‖ † ‡ ′ ″ ‰ № ℮ Ⓓ ⟨ ⟩

Sizes and positions follow SF Pro (opsz 17) and Inter (opsz 14) at 400,
measured in cap heights; strokes come from the Porto Faifo masters.
"""

from __future__ import annotations

import math
from contextlib import contextmanager

from fontTools.misc.bezierTools import curveCurveIntersections

from .geometry import Contour, intersect_lines, offset_cubic, offset_line, polygon, rect, shared_foot, split_cubic, stroke, superellipse
from .glyphs import Glyph
from .system import Namespace
from .upper import hcut_centre

FIGURES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
SUPERIOR = [0x2070, 0xB9, 0xB2, 0xB3, 0x2074, 0x2075, 0x2076, 0x2077, 0x2078, 0x2079]
INFERIOR = [0x2080 + i for i in range(10)]
SMALL = 0.53  # small figure height / figure height (SF 0.51, Inter 0.55)
# Bottom of the small figures in cap heights: superiors top out at 1.10 (SF
# 1.05, Inter 1.15), inferiors drop to -0.18 (SF -0.15, Inter -0.20);
# numerators end on the cap height and denominators sit on the baseline.
SUPS_Y, SINF_Y, NUMR_Y = 0.57, -0.18, 1 - SMALL


class SymbolMixin:
    # ------------------------------------------------------------- helpers
    @contextmanager
    def _drawn_at(self, strokes=1.0, **widths):
        """Build with every stroke x ``strokes`` and some proportions replaced."""
        st, wd = self.st, self.wd
        if strokes != 1.0:
            self.st = Namespace({n: v * strokes for n, v in st.items() if isinstance(v, (int, float))})
        self.wd = Namespace({**wd, **widths})
        try:
            yield
        finally:
            self.st, self.wd = st, wd

    @staticmethod
    def _ink(cs):
        b = [c.bounds() for c in cs]
        return min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)

    def _letter(self, method, **widths):
        """Contours of a letter built at other proportions, ink starting at x 0."""
        with self._drawn_at(**widths):
            g = getattr(self, method)()
        x0 = self._ink(g.contours)[0]
        return [c.translated(-x0, 0) for c in g.contours]

    def _tab(self, name, uni, cs, note):
        """Ink centred on the tabular advance (figures, currency, math)."""
        adv = self.wd.tabularAdvance
        x0, _, x1, _ = self._ink(cs)
        return Glyph(name, [uni], adv, [c.translated((adv - x1 - x0) / 2, 0) for c in cs], note=note)

    def _own(self, name, uni, cs, sb, note):
        """Ink between two equal side bearings."""
        x0, _, x1, _ = self._ink(cs)
        return Glyph(name, [uni] if uni else [], x1 - x0 + 2 * sb, [c.translated(sb - x0, 0) for c in cs], note=note)

    @property
    def _tb(self):
        # Currency bars: punctStroke - 10 at Regular, as on € ¥ ¢, growing at
        # 0.55 the stroke's rate so Black's bars leave the letters readable.
        reg = self.reg.punctStroke
        return reg - 10 + 0.55 * (self.st.punctStroke - reg)

    @property
    def _currency_strokes(self):
        """Past Regular the narrowed currency letters thicken at 0.7 the stem
        rate, so Bold and Black keep counters inside the tabular advance."""
        reg, stem = self.reg.stemUpper, self.st.stemUpper
        return 1.0 if stem <= reg else (reg + 0.7 * (stem - reg)) / stem

    @property
    def _dS(self):
        """Stem added over Regular (0 at Regular, negative in Light)."""
        return self.st.stemUpper - self.reg.stemUpper

    @property
    def _fw(self):
        return self.wd.figure

    # ------------------------------------------------------ small figures
    def _small(self, fig):
        """``fig`` drawn at superiorWeight / SMALL x every stroke, widened by
        what an offset would add, then scaled to SMALL: the stroke reads
        superiorWeight x the figure's and the outline keeps the figure's
        points, so it interpolates (ª is built the same way)."""
        weight = self.sh.superiorWeight
        grow = (weight - SMALL) * self.st.figureStem / SMALL
        with self._drawn_at(weight / SMALL, figure=self.wd.figure + grow, tabularAdvance=self.wd.tabularAdvance + grow):
            g = getattr(self, fig)()
        pad = 30
        return [c.scaled(SMALL).translated(pad, 0) for c in g.contours], g.width * SMALL + 2 * pad

    def small_figures(self) -> dict[str, Glyph]:
        out = {}
        C = self.cap
        for i, fig in enumerate(FIGURES):
            cs, w = self._small(fig)
            dnom = f"{fig}.dnom"
            out[dnom] = Glyph(dnom, [], w, cs, note=f"{fig} x{SMALL}, stroke x superiorWeight, on the baseline (frac)")
            for name, uni, y, role in ((f"{fig}.numr", None, NUMR_Y, "top on the cap height (frac)"),
                                       (f"{fig}superior", SUPERIOR[i], SUPS_Y, f"bottom at {SUPS_Y} cap height"),
                                       (f"{fig}inferior", INFERIOR[i], SINF_Y, f"bottom at {SINF_Y} cap height")):
                g = Glyph(name, [uni] if uni else [], w, note=f"{dnom} raised: {role}")
                g.components = [(dnom, 0, y * C)]
                out[name] = g
        return out

    def fraction(self):
        C, t = self.cap, 0.75 * self.st.punctStroke
        adv, dx = 300, 0.52 * C
        c = stroke((adv / 2 - dx / 2, 0), (adv / 2 + dx / 2, C), t)
        return Glyph("fraction", [0x2044], adv, [c], note="slash from the baseline to the cap height, x0.75 punctStroke (about the small figures' stroke); reaches under its neighbours")

    def _vulgar(self, name, uni, num, den):
        w = self.small_figures()[f"{num}.dnom"].width
        f = self.fraction().width
        g = Glyph(name, [uni], 2 * w + f, note=f"{num}.numr + fraction + {den}.dnom")
        g.components = [(f"{num}.numr", 0, 0), ("fraction", w, 0), (f"{den}.dnom", w + f, 0)]
        return g

    def onequarter(self):
        return self._vulgar("onequarter", 0xBC, "one", "four")

    def onehalf(self):
        return self._vulgar("onehalf", 0xBD, "one", "two")

    def threequarters(self):
        return self._vulgar("threequarters", 0xBE, "three", "four")

    def onethird(self):
        return self._vulgar("onethird", 0x2153, "one", "three")

    def twothirds(self):
        return self._vulgar("twothirds", 0x2154, "two", "three")

    def zero_slash(self):
        g = self.zero()
        st, W, C = self.st, self.wd.figure, self.sys.m.figureHeight
        cx = g.width / 2
        rx, ry = W / 2 - st.figureSide, C / 2 + self.of - st.figureTop
        # The slash spans the counter at 58° and runs 30 units into the ring.
        a = math.radians(58)
        ux, uy = math.cos(a), math.sin(a)
        r = 1 / math.hypot(ux / rx, uy / ry) + 30
        p, q = (cx - r * ux, C / 2 - r * uy), (cx + r * ux, C / 2 + r * uy)
        cs = list(g.contours) + [stroke(p, q, st.punctStroke, "p")]
        return Glyph("zero.zero", [], g.width, cs, note="0 + slash across the counter (zero)")

    # ------------------------------------------------------------------ math
    def plusminus(self):
        t, L = self.st.punctStroke, 880
        g = 180  # the gap of =
        top = 0.78 * self.cap
        yp = (t + g + top) / 2
        cs = [rect(-L / 2, 0, L / 2, t), rect(-L / 2, yp - t / 2, L / 2, yp + t / 2), rect(-t / 2, t + g, t / 2, top)]
        return self._math("plusminus", 0xB1, cs, "plus over a minus with the gap of =, from the baseline to 0.78 cap height")

    def logicalnot(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        cs = [rect(-L / 2, ym - t / 2, L / 2, ym + t / 2), rect(L / 2 - t, 0.15 * self.cap, L / 2, ym)]
        return self._math("logicalnot", 0xAC, cs, "minus + drop to 0.15 cap height at the right end")

    def notequal(self):
        t, L, ym = self.st.punctStroke, 880, self._ym
        h = 0.40 * self.cap
        dx = h * 620 / 1880  # the angle of /
        cs = [rect(-L / 2, ym + 90, L / 2, ym + 90 + t), rect(-L / 2, ym - 90 - t, L / 2, ym - 90), stroke((-dx, ym - h), (dx, ym + h), t)]
        return self._math("notequal", 0x2260, cs, "= + stroke at the angle of /")

    def _lessequal_contours(self):
        t = self.st.punctStroke
        dt = t - self.reg.punctStroke
        # Regular: a 560 chevron 300 above the bar; heavier strokes grow the
        # chevron and close the gap more slowly, so neither turns into a stub.
        w, h, gap = 800, 560 + 0.6 * dt, 300 - 0.8 * dt
        yc = t + gap + h / 2
        hw = t / 2 / math.sin(math.atan2(h / 2, w))
        cs = self._chevron(-w / 2 + hw, yc, w - hw, h, t, True)
        return cs + [rect(-w / 2, 0, w / 2, t)]

    def lessequal(self):
        return self._math("lessequal", 0x2264, self._lessequal_contours(), "< flattened to 560, 300 over a bar on the baseline")

    def greaterequal(self):
        adv = self.wd.tabularAdvance
        g = self.lessequal()
        return Glyph("greaterequal", [0x2265], adv, [c.mirrored_x(adv / 2).oriented(True) for c in g.contours], note="≤ mirrored")

    def approxequal(self):
        tilde = self.asciitilde()
        d = 0.13 * self.cap + 0.75 * (self.st.punctStroke - self.reg.punctStroke)
        cs = [c.translated(0, d) for c in tilde.contours] + [c.translated(0, -d) for c in tilde.contours]
        return Glyph("approxequal", [0x2248], tilde.width, cs, note="two ~ at ±0.13 cap height")

    def radical(self):
        t, C = self.st.punctStroke, self.cap
        W = 900
        xv = 0.40 * W
        tick = (0.0, 0.46 * C)
        cs = shared_foot([stroke(tick, (xv, 0), t), stroke((xv, 0), (W, C), t)])
        return self._tab("radical", 0x221A, cs, "short and long stroke meeting in a flat foot on the baseline; no overbar (Inter)")

    def summation(self):
        st, C = self.st, self.cap
        W, T, yb = 0.94 * self._fw, st.barUpper, -0.19 * C
        ym = (C + yb) / 2
        t = st.diagonalUpper - 20
        h = C - T / 2 - yb - T / 2
        w = 0.56 * W
        hw = t / 2 / math.sin(math.atan2(h / 2, w))
        arms = [c.mirrored_x((W * 0.04 + 0.56 * W) / 2).oriented(True) for c in self._chevron(W * 0.04 + hw, ym, w - hw, h, t, True)]
        cs = [rect(0, C - T, W, C), rect(0, yb, W, yb + T)] + arms
        return self._tab("summation", 0x2211, cs, "Σ: cap bars from the cap height to -0.19, > between them; tabular")

    def product(self):
        st, C, sp = self.st, self.cap, self.sp
        W, S, T, yb = self.wd.H, st.stemUpper, st.barUpper, -0.2 * C
        e = 0.06 * W
        cs = [rect(0, C - T, W, C), rect(e, yb, e + S, C - T + 10), rect(W - e - S, yb, W - e, C - T + 10)]
        return self._own("product", 0x220F, cs, sp.upperStraight, "Π on H stems down to -0.2 cap height; bar overhangs 0.06")

    def increment(self):
        st, C, sp = self.st, self.cap, self.sp
        W = 0.92 * self.wd.A
        t, T, f = st.diagonalUpper - 20, st.barUpper, 0.5 * st.diagonalUpper
        outer = [(0, 0), (W, 0), (W / 2 + f / 2, C), (W / 2 - f / 2, C)]
        left = offset_line(outer[3], outer[0], t)
        right = offset_line(outer[1], outer[2], t)
        base = ((0, T), (W, T))
        inner = [intersect_lines(*left, *base), intersect_lines(*right, *base), intersect_lines(*left, *right)]
        cs = [polygon(outer).oriented(True), polygon(inner).oriented(False)]
        return self._own("increment", 0x2206, cs, sp.upperDiagonal + 20, "triangle on A diagonals - 20 and a cap bar; flat apex")

    def Ohm(self):
        st, C, sp = self.st, self.cap, self.sp
        W = self.wd.O
        side, top, S, T = st.roundUpperSide, st.roundUpperTop, st.stemUpper, st.barUpper
        rx, ry = W / 2, 0.43 * C
        cx, cy = W / 2, C + self.oc - ry
        g = 0.30 * rx
        # A C ring built on its side, so its terminal cuts are vertical once
        # it is turned to open at the bottom.
        ring = self.cut_ring(cx, cy, ry, rx, top, side, cy + g, cy - g).rotated(-90, cx, cy).oriented(True)
        y_join = cy - ry + top / 2
        foot = 0.26 * rx
        cs = [ring]
        for sgn in (-1, 1):
            xi = cx + sgn * g
            xo = xi + sgn * S
            cs.append(rect(min(xi, xo), 0, max(xi, xo), y_join).oriented(True))
            cs.append(rect(min(xi, xo + sgn * foot), 0, max(xi, xo + sgn * foot), T).oriented(True))
        return self._own("Ohm", 0x2126, cs, sp.upperRound, "O ring opened at the bottom, H-stem legs and cap-bar feet")

    def infinity(self):
        t, ym = self.st.punctStroke, self._ym
        W, H = self.wd.get("infinity", 1.12 * self.cap), 0.56 * self.cap
        a, b = W / 2 - t / 2, H / 2 - t / 2
        k = 0.58

        def lobe(sgn):
            # Centre line of one loop: from the crossing out round the loop and
            # back, 90° apart at the crossing.  Offset to both sides; the two
            # loops overlap into the X.
            c = Contour((0, ym))
            c.curve((sgn * a / 2, ym + b), 90 - sgn * 45, 90 - sgn * 90, k)
            c.curve((sgn * a, ym), 90 - sgn * 90, 270, k)
            c.curve((sgn * a / 2, ym - b), 270, 90 + sgn * 90, k)
            c.curve((0, ym), 90 + sgn * 90, 90 + sgn * 45, k)
            segs = list(c.beziers())
            out = []
            for d in (t / 2, -t / 2):
                offs = [offset_cubic(s, sgn * d) for s in segs]
                # The pieces meet at the crossing on the tangent lines.
                m = intersect_lines(offs[-1][2], offs[-1][3], offs[0][0], offs[0][1])
                if d < 0:
                    # Inside the corner the first and last pieces cross before
                    # their ends: cut both at the crossing.
                    hit = curveCurveIntersections(offs[-1], offs[0])[0]
                    m = hit.pt
                    offs[-1] = split_cubic(offs[-1], hit.t1)[0]
                    offs[0] = split_cubic(offs[0], hit.t2)[1]
                p = Contour(m)
                if d > 0:
                    p.line(offs[0][0])
                for o in offs:
                    if p.current != o[0]:
                        p.line(o[0])
                    p.cubic(o[1], o[2], o[3])
                out.append(p.close())
            return [out[0].oriented(True), out[1].oriented(False)]

        cs = lobe(-1) + lobe(1)
        return self._own("infinity", 0x221E, cs, 170, "two loops of punctStroke crossing at 90° on the math axis")

    def partialdiff(self):
        outline, counter = self._six_contours()
        x0, _, x1, _ = self._ink([outline])
        cs = [outline.mirrored_x((x0 + x1) / 2).oriented(True), counter.mirrored_x((x0 + x1) / 2).oriented(False)]
        return self._own("partialdiff", 0x2202, cs, 120, "6 mirrored: the bowl's right side rises and curls back to the left")

    def emptyset(self):
        t, C = self.st.punctStroke + 10, self.cap
        D = 0.86 * C
        r = D / 2
        cx, cy = r, 0.42 * C
        k = self.ten.circle
        ring = [superellipse(cx, cy, r, r, k), superellipse(cx, cy, r - t, r - t, k).reversed()]
        e = 0.62 * D
        sl = stroke((cx - 0.62 * e, cy - e), (cx + 0.62 * e, cy + e), t)
        return self._own("emptyset", 0x2205, ring + [sl], 110, "circle 0.86 cap height + slash beyond it")

    def integral(self):
        st, C = self.st, self.cap
        S = 0.85 * st.stemLower
        yb, yt = -0.25 * C, 1.05 * C
        yc = (yb + yt) / 2
        x0 = 0.0
        reach = 0.30 * C
        # j's lower hook, then turned 180° for the upper one.
        hook = self.hook_stem(x0, S, yc + 60, yb, 0.22 * C, 0.24 * C, 110, 96, x0 + S + reach, st.barLower, 0)
        low = hook.mirrored_x(x0 + S / 2).oriented(True)
        cs = [low, low.rotated180(x0 + S / 2, yc).oriented(True)]
        return self._own("integral", 0x222B, cs, 60, "stem x0.85 from -0.25 to 1.05 cap height; j hook below, turned above")

    def micro(self):
        u = self.u()
        S = self.st.stemLower
        x0 = self._ink(u.contours)[0]
        cs = list(u.contours) + [rect(x0, self.desc, x0 + S, self.xh)]
        return Glyph("micro", [0xB5], u.width, cs, note="u + left stem to the descender")

    def pi(self):
        st, X, sp = self.st, self.xh, self.sp
        S, T = st.stemLower, st.barLower
        W = 1100 + 1.6 * (S - self.reg.stemLower)  # the legs keep a counter
        e = 0.12 * W
        cs = [rect(0, X - T, W, X), rect(e, 0, e + S, X - T + 10), rect(W - e - S, 0, W - e, X - T + 10)]
        return self._own("pi", 0x3C0, cs, sp.lowerStraight - 40, "x-height bar on two n stems; bar overhangs 0.12")

    def literSign(self):
        st, k = self.st, self.ten
        A = self.asc
        # Script l: a straight 45° entry stroke crosses the t stem and runs up
        # into a loop whose left side is the stem.  The loop is an outline and
        # a counter drawn separately, not an offset centre line, so it cannot
        # fold over itself.  Past Regular the stroke grows at 0.75 the stem
        # rate, the sign widens by twice the added stroke and the crossing
        # drops, which keeps the counter open in Black.
        reg = 0.92 * self.reg.stemLower
        t = reg + 0.75 * (0.92 * st.stemLower - reg)
        h = t * st.barLower / st.stemLower
        W = 760 + 2.0 * (t - reg)
        xs = 0.30 * W
        a = math.radians(45)
        sa, ca = math.sin(a), math.cos(a)
        px, py = xs + t / 2, 0.47 * A - 1.2 * (t - reg)
        # The entry stroke's upper edge meets the stem's right side at the
        # counter tip q and its left side at the notch m.
        qx, qy = px + t / 2, py + t / 2 * (1 + sa) / ca
        mx, my = px - t / 2, qy - t * math.tan(a)
        wi = 170 - 0.2 * (t - reg)
        hc = A - h - qy
        ye, xt = qy + 0.6 * hc, qx + 0.5 * wi
        ri = (qx + 0.15 * hc / math.tan(a), qy + 0.15 * hc)
        ro = (ri[0] + t * sa, ri[1] - t * ca)
        yf = my - mx * math.tan(a)  # the entry stroke starts in a level cut at x = 0
        outline = Contour((mx, my)).line((mx, ye))
        outline.curve((xt, A), 90, 0, k.outer)
        outline.curve((qx + wi + t, ye), 0, 270, k.outer)
        outline.curve(ro, 270, 225, 0.55)
        outline.line((t / sa, yf)).line((0, yf))
        counter = Contour((qx, qy)).line(ri)
        counter.curve((qx + wi, ye), 45, 90, 0.55)
        counter.curve((xt, A - h), 90, 180, k.inner)
        counter.curve((qx, ye), 180, 270, k.inner)
        stem = self.hook_stem(xs, t, py, 0, 0.12 * A, 0.15 * A, 130, 116, W, st.barLower, self.ox)
        cs = [stem, outline.close().oriented(True), counter.close().oriented(False)]
        return self._own("literSign", 0x2113, cs, 70, "script l: 45° entry stroke over the t stem into a loop with a drawn counter")

    # ---------------------------------------------------------------- arrows
    @property
    def _arrow_t(self):
        return self.st.punctStroke

    @property
    def _head(self):
        """Outer edge length of an arrow head's arms (0.6 of the diagonal box)."""
        return 0.6 * 0.81 * self.cap

    def _corner(self):
        """Arrow head as two arms meeting in a square corner at the origin,
        pointing up-right (the diagonal arrows' head)."""
        t, a = self._arrow_t, self._head
        return [rect(-a, -t, 0, 0), rect(-t, -a, 0, -t + 10)]

    def _arrow(self, L, heads=(True, False)):
        """Horizontal arrow from x 0 to L on y 0; True in ``heads`` puts a head
        on the (right, left) end.  The head is the diagonal arrows' corner
        turned 45°, so every arrow shares one head."""
        t = self._arrow_t
        cs = []
        x0, x1 = 0.0, L
        if heads[0]:
            cs += [c.rotated(-45, 0, 0).translated(L, 0).oriented(True) for c in self._corner()]
            x1 = L - 0.7 * t
        if heads[1]:
            cs += [c.rotated(135, 0, 0).oriented(True) for c in self._corner()]
            x0 = 0.7 * t
        cs.append(rect(x0, -t / 2, x1, t / 2))
        return cs

    def _arrow_glyph(self, name, uni, cs, note):
        return self._own(name, uni, cs, 0.14 * self.cap, note)

    def rightArrow(self):
        cs = [c.translated(0, self._ym) for c in self._arrow(self.cap)]
        return self._arrow_glyph("rightArrow", 0x2192, cs, "punctStroke shaft, 1 cap long, on the math axis; the diagonal head turned 45°")

    def leftArrow(self):
        cs = [c.mirrored_x(self.cap / 2).oriented(True).translated(0, self._ym) for c in self._arrow(self.cap)]
        return self._arrow_glyph("leftArrow", 0x2190, cs, "→ mirrored")

    def leftRightArrow(self):
        cs = [c.translated(0, self._ym) for c in self._arrow(1.2 * self.cap, (True, True))]
        return self._arrow_glyph("leftRightArrow", 0x2194, cs, "→ with a head at both ends, 1.2 cap long")

    def upArrow(self):
        C = self.cap
        cs = [c.rotated(90, 0, 0).translated(0, 0).oriented(True) for c in self._arrow(C)]
        return self._arrow_glyph("upArrow", 0x2191, cs, "→ turned upright, baseline to cap height")

    def downArrow(self):
        C = self.cap
        cs = [c.rotated(-90, 0, 0).translated(0, C).oriented(True) for c in self._arrow(C)]
        return self._arrow_glyph("downArrow", 0x2193, cs, "→ turned down, cap height to baseline")

    def upDownArrow(self):
        C = self.cap
        cs = [c.rotated(90, 0, 0).translated(0, -0.1 * C).oriented(True) for c in self._arrow(1.2 * C, (True, True))]
        return self._arrow_glyph("upDownArrow", 0x2195, cs, "↔ turned upright, centred on half the cap height")

    def _diagonal(self):
        """↗ in a D x D box: the head is a corner along the axes."""
        t, D = self._arrow_t, 0.81 * self.cap
        c0 = 0.354 * t
        cs = [c.translated(D, D) for c in self._corner()] + [stroke((c0, c0), (D - 0.6 * t, D - 0.6 * t), t, "p")]
        dy = self.cap / 2 - D / 2
        return [c.translated(0, dy) for c in cs], D

    def northEastArrow(self):
        cs, _ = self._diagonal()
        return self._arrow_glyph("northEastArrow", 0x2197, cs, "shaft at 45° into a corner head, 0.81 cap box centred on half the cap height")

    def northWestArrow(self):
        cs, D = self._diagonal()
        return self._arrow_glyph("northWestArrow", 0x2196, [c.mirrored_x(D / 2).oriented(True) for c in cs], "↗ mirrored")

    def southEastArrow(self):
        cs, D = self._diagonal()
        return self._arrow_glyph("southEastArrow", 0x2198, [c.mirrored_y(self.cap / 2).oriented(True) for c in cs], "↗ flipped")

    def southWestArrow(self):
        cs, D = self._diagonal()
        return self._arrow_glyph("southWestArrow", 0x2199, [c.rotated180(D / 2, self.cap / 2).oriented(True) for c in cs], "↗ turned 180°")

    # -------------------------------------------------------------- currency
    def _bars(self, x0, x1, ys):
        tb = self._tb
        return [rect(x0, y - tb / 2, x1, y + tb / 2) for y in ys]

    def _vbar(self, x, y0=None, y1=None):
        tb, C = self._tb, self.cap
        return rect(x - tb / 2, -150 if y0 is None else y0, x + tb / 2, C + 150 if y1 is None else y1)

    def naira(self):
        C, e = self.cap, 60
        W = 1.07 * self._fw - 2 * e
        cs = self._letter("N", N=W) + self._bars(-e, W + e, (0.37 * C, 0.63 * C))
        return self._tab("naira", 0x20A6, cs, "N narrowed + two bars; tabular")

    def won(self):
        C, e = self.cap, 40
        cs = self._letter("W")
        W = self._ink(cs)[2]
        cs += self._bars(-e, W + e, (0.37 * C, 0.63 * C))
        return self._own("won", 0x20A9, cs, 60, "W + two bars; keeps the W width (as SF, Inter)")

    def kip(self):
        C, e = self.cap, 70
        cs = self._letter("K", K=self._fw - 30 - e)
        W = self._ink(cs)[2]
        cs += self._bars(-e, 0.72 * W, (0.5 * C,))
        return self._tab("kip", 0x20AD, cs, "K narrowed + bar at half the cap height; tabular")

    def tugrik(self):
        C = self.cap
        cs = self._letter("T", T=0.96 * self._fw)
        W = self._ink(cs)[2]
        L = 0.46 * W + self._dS  # the bars keep their reach past a heavier stem
        rise = L / 2 * math.tan(math.radians(22))
        cs += [stroke((W / 2 - L / 2, y - rise), (W / 2 + L / 2, y + rise), self._tb, "v") for y in (0.30 * C, 0.52 * C)]
        return self._tab("tugrik", 0x20AE, cs, "T narrowed + two bars rising 22° across the stem; tabular")

    def peso(self):
        C, e = self.cap, 70
        cs = self._letter("P", P=0.98 * self._fw - e)
        W = self._ink(cs)[2]
        cs += self._bars(-e, W, (0.56 * C, 0.76 * C))
        return self._tab("peso", 0x20B1, cs, "P narrowed + two bars through the bowl; tabular")

    def ruble(self):
        C, e = self.cap, 70
        cs = self._letter("P", P=0.97 * self._fw - e)
        W = self._ink(cs)[2]
        cs += self._bars(-e, 0.62 * W, (0.27 * C,))
        return self._tab("ruble", 0x20BD, cs, "P narrowed + bar below the bowl; tabular")

    def guarani(self):
        cs = self._letter("G", G=1.02 * self._fw)
        x0, _, x1, _ = self._ink(cs)
        return self._tab("guarani", 0x20B2, cs + [self._vbar((x0 + x1) / 2)], "G narrowed + vertical bar through it; tabular")

    def _c_narrow(self):
        W = 1.02 * self._fw + 30
        cs = self._letter("C", C=W)
        return cs, W / 2  # ring centre

    def cedi(self):
        cs, cx = self._c_narrow()
        return self._tab("cedi", 0x20B5, cs + [self._vbar(cx)], "C narrowed + vertical bar through it; tabular")

    def colonsign(self):
        C = self.cap
        cs, cx = self._c_narrow()
        dx = (C + 300) * 620 / 1880 / 2  # the angle of /
        gap = 0.18 * self._fw
        cs += [stroke((x - dx, -150), (x + dx, C + 150), self._tb) for x in (cx - gap / 2, cx + gap / 2)]
        return self._tab("colonsign", 0x20A1, cs, "C narrowed + two strokes at the angle of /; tabular")

    def hryvnia(self):
        C, e = self.cap, 30
        cs = self._letter("S", S=0.95 * self._fw - 2 * e)
        W = self._ink(cs)[2]
        cs = [c.mirrored_x(W / 2).oriented(True) for c in cs] + self._bars(-e, W + e, (0.39 * C, 0.61 * C))
        return self._tab("hryvnia", 0x20B4, cs, "S mirrored (the spine falls to the left) + two bars; tabular")

    def tenge(self):
        st, C = self.st, self.cap
        W, S, T = 0.90 * self._fw, st.stemUpper, st.barUpper
        y2 = C - T - 0.85 * T
        cs = [rect(0, C - T, W, C), rect(0, y2 - T, W, y2), rect(W / 2 - S / 2, 0, W / 2 + S / 2, y2 - T + 10)]
        return self._tab("tenge", 0x20B8, cs, "T with a second bar above the stem; tabular")

    def rupeeIndian(self):
        st, C = self.st, self.cap
        W, T, Tw = 0.81 * self._fw, st.barUpper, st.bowlWaist
        y2, y0 = 0.73 * C, 0.42 * C
        lobe = self.side_bowl(0.10 * W, y0, C, 0.90 * W, T, Tw, st.roundUpperSide - 10, overlap=0.10 * W)
        top = (0.30 * W, y0 + Tw / 2)
        leg = stroke(top, hcut_centre(top, W, 0, st.diagonalUpper, +1), st.diagonalUpper, cut=("p", "h"))
        cs = [rect(0, C - T, W, C), rect(0, y2 - T + 10, W, y2 + 10), lobe, leg]
        return self._tab("rupeeIndian", 0x20B9, cs, "two cap bars, an R bowl from the top bar and a straight leg; tabular")

    def liraTurkish(self):
        st, C = self.st, self.cap
        W, S = 0.94 * self._fw, st.stemUpper
        # J's stem and bowl, mirrored: the stem on the left, the bowl rising
        # to a c terminal at 0.46 cap height on the right.
        body = self.cut_cup(W, S, C, 0.50 * C, W / 2, self.oc, st.roundUpperTop, 0.46 * C).mirrored_x(W / 2).oriented(True)
        sx = S / 2
        L = 0.62 * W + self._dS
        rise = L / 2 * math.tan(math.radians(24))
        bars = [stroke((sx - 0.36 * L, y - 0.72 * rise), (sx + 0.64 * L, y + 1.28 * rise), self._tb, "v") for y in (0.46 * C, 0.66 * C)]
        return self._tab("liraTurkish", 0x20BA, [body] + bars, "J mirrored, terminal at 0.48 cap height, + two bars rising 24°; tabular")

    def manat(self):
        st, C = self.st, self.cap
        S = st.stemUpper
        W = max(0.96 * self._fw, 3 * S + 2 * 120)  # three stems keep 120 between them
        H = 0.86 * C
        arch = self.cup(0, W, S, S, H, 0.42 * H, st.roundUpperTop, self.oc).rotated180(W / 2, H / 2).oriented(True)
        return self._tab("manat", 0x20BC, [arch, rect(W / 2 - S / 2, 0, W / 2 + S / 2, C)], "U turned into an arch 0.86 cap high + stem to the cap height; tabular")

    def sheqel(self):
        st, C = self.st, self.cap
        # Four stems side by side: they thicken at 0.6 the stem rate and the
        # sign widens to keep 110 between them, past the tabular advance in
        # Bold and Black (as SF and Inter, which never set ₪ tabular).
        S, T = st.stemUpper - 10 - 0.4 * max(0.0, self._dS), st.barUpper
        W = max(1.08 * self._fw, 4 * S + 3 * 110)
        g = (W - 4 * S) / 3
        x2 = 2 * S + 2 * g
        R = 1.6 * S
        r = max(R - S, 30)
        k = self.ten.outer
        c = Contour((0, 0)).line((0, C)).line((x2 + S - R, C))
        c.curve((x2 + S, C - R), 0, 270, k)
        c.line((x2 + S, 0.30 * C)).line((x2, 0.30 * C)).line((x2, C - T - r))
        c.curve((x2 - r, C - T), 90, 180, k)
        c.line((S, C - T)).line((S, 0))
        a = c.close().oriented(True)
        return self._own("sheqel", 0x20AA, [a, a.rotated180(W / 2, C / 2).oriented(True)], 80, "two square hooks with a round outer corner, interlocked")

    def lari(self):
        st, C = self.st, self.cap
        W = self._fw
        rx, ry = 0.46 * W, C / 2
        cx, cy = rx, C / 2
        top = st.roundUpperTop
        # The lower cut stays inside the counter (Black's bottom is thicker).
        y_lo = max(cy - 0.72 * ry, cy - ry + top + 30)
        ring = self.cut_ring(cx, cy, rx, ry, st.roundUpperSide, top, cy + self.sh.CTerminalUpper * ry, y_lo)
        cs = [ring, rect(0.30 * rx, 0, W, st.barUpper)]
        cs += [self._vbar(cx + d * rx, C - top - 0.12 * C, C + 150) for d in (-0.20, 0.20)]
        return self._tab("lari", 0x20BE, cs, "C ring on a baseline bar + two bars through its top; tabular")

    def baht(self):
        cs = self._letter("B", B=0.85 * self._fw)
        W = self._ink(cs)[2]
        return self._tab("baht", 0x0E3F, cs + [self._vbar(0.45 * W)], "B narrowed + vertical bar through it; tabular")

    def bitcoin(self):
        C = self.cap
        cs = self._letter("B", B=0.85 * self._fw)
        W = self._ink(cs)[2]
        cs += [self._vbar(x, y0, y1) for x in (0.34 * W, 0.62 * W) for y0, y1 in ((-150, 40), (C - 40, C + 150))]
        return self._tab("bitcoin", 0x20BF, cs, "B narrowed + two bar ends above and below; tabular")

    def rupee(self):
        R, s = self.R(), self.s()
        cs = list(R.contours) + [c.translated(R.width - 40, 0) for c in s.contours]
        return Glyph("rupee", [0x20A8], R.width + s.width - 40, cs, note="R + s, 40 tighter")

    # ------------------------------------------------------ geometric shapes
    @property
    def _shape_t(self):
        return self.st.punctStroke

    def _shape(self, name, uni, cs, size, small, note):
        sb = 120 if small else 0.14 * self.cap
        return self._own(name, uni, cs, sb, note)

    def _square(self, s, yc, white, t):
        cs = [rect(0, yc - s / 2, s, yc + s / 2)]
        if white:
            cs.append(rect(t, yc - s / 2 + t, s - t, yc + s / 2 - t).oriented(False))
        return cs

    def _triangle(self, w, h, yc, white, t):
        """Pointing up, base w, height h, box centred on yc."""
        pts = [(0, yc - h / 2), (w, yc - h / 2), (w / 2, yc + h / 2)]
        cs = [polygon(pts).oriented(True)]
        if white:
            lines = [offset_line(pts[i], pts[(i + 1) % 3], t) for i in range(3)]
            inner = [intersect_lines(*lines[i - 1], *lines[i]) for i in range(3)]
            cs.append(polygon(inner).oriented(False))
        return cs

    def _diamond(self, w, h, yc, white, t):
        pts = [(w / 2, yc - h / 2), (w, yc), (w / 2, yc + h / 2), (0, yc)]
        cs = [polygon(pts).oriented(True)]
        if white:
            lines = [offset_line(pts[i], pts[(i + 1) % 4], t) for i in range(4)]
            inner = [intersect_lines(*lines[i - 1], *lines[i]) for i in range(4)]
            cs.append(polygon(inner).oriented(False))
        return cs

    def _circle(self, d, yc, white, t):
        k = self.ten.circle
        cs = [superellipse(d / 2, yc, d / 2, d / 2, k)]
        if white:
            cs.append(superellipse(d / 2, yc, d / 2 - t, d / 2 - t, k).reversed())
        return cs

    def shapes(self) -> dict[str, Glyph]:
        C, t = self.cap, self._shape_t
        yb = 0.47 * self.xh  # the bullet's centre
        # Small shapes are 0.38 of the large ones (SF ▴ ▸ 0.38 cap) with a
        # 0.55 outline; from Regular up they grow by 2.5 x the added outline
        # so the small white triangles keep a counter.
        ts = 0.55 * t
        k = 0.38 + 2.5 * max(0.0, ts - 0.55 * self.reg.punctStroke) / C
        out = {}

        def add(name, uni, cs, small, note):
            out[name] = self._shape(name, uni, cs, None, small, note)

        for white, (big, small_n), (ub, us) in ((False, ("blackSquare", "blackSmallSquare"), (0x25A0, 0x25AA)),
                                               (True, ("whiteSquare", "whiteSmallSquare"), (0x25A1, 0x25AB))):
            add(big, ub, self._square(C, C / 2, white, t), False, "square of the cap height" + (", punctStroke outline" if white else ""))
            add(small_n, us, self._square(k * C, yb, white, ts), True, f"square x{k:.2f} on the bullet" + (", x0.55 outline" if white else ""))
        tri = {"up": (0, ("upBlackTriangle", "upWhiteTriangle", "upBlackSmallTriangle", "upWhiteSmallTriangle"), (0x25B2, 0x25B3, 0x25B4, 0x25B5)),
               "right": (-90, ("rightBlackTriangle", "rightWhiteTriangle", "rightBlackSmallTriangle", "rightWhiteSmallTriangle"), (0x25B6, 0x25B7, 0x25B8, 0x25B9)),
               "down": (180, ("downBlackTriangle", "downWhiteTriangle", "downBlackSmallTriangle", "downWhiteSmallTriangle"), (0x25BC, 0x25BD, 0x25BE, 0x25BF)),
               "left": (90, ("leftBlackTriangle", "leftWhiteTriangle", "leftBlackSmallTriangle", "leftWhiteSmallTriangle"), (0x25C0, 0x25C1, 0x25C2, 0x25C3))}
        w, h = 1.0 * C, 0.9 * C
        for direction, (angle, names, unis) in tri.items():
            for i, (white, small) in enumerate(((False, False), (True, False), (False, True), (True, True))):
                s = k if small else 1.0
                yc = yb if small else C / 2
                cs = self._triangle(s * w, s * h, 0, white, ts if small else t)
                cs = [c.rotated(angle, s * w / 2, 0).translated(0, yc).oriented(c.signed_area() > 0) for c in cs]
                add(names[i], unis[i], cs, small, f"triangle {w / C:.1f} x {h / C:.1f} cap, pointing {direction}" + (f", x{k:.2f} on the bullet" if small else "") + (", outlined" if white else ""))
        add("blackDiamond", 0x25C6, self._diamond(1.2 * C, 1.2 * C, C / 2, False, t), False, "square diamond 1.2 cap across")
        add("whiteDiamond", 0x25C7, self._diamond(1.2 * C, 1.2 * C, C / 2, True, t), False, "◆ outlined")
        # The narrow lozenge's outline grows at half the stroke rate, or Black closes it.
        tl = self.reg.punctStroke + 0.5 * (t - self.reg.punctStroke)
        add("lozenge", 0x25CA, self._diamond(0.64 * C, 0.96 * C, C / 2, True, tl), False, "narrow diamond 0.64 x 0.96 cap, outlined")
        add("blackCircle", 0x25CF, self._circle(1.08 * C, C / 2, False, t), False, "circle 1.08 cap across")
        add("whiteCircle", 0x25CB, self._circle(1.08 * C, C / 2, True, t), False, "● outlined")
        d = 1.5 * self._d
        g = Glyph("whiteBullet", [0x25E6], d + 2 * 120, [c.translated(120, 0) for c in self._circle(d, yb, True, 0.6 * t)], note="bullet outlined at 0.6 punctStroke")
        out["whiteBullet"] = g
        return out

    # ------------------------------------------------------------------ marks
    def brokenbar(self):
        g = self.bar()
        x0, y0, x1, y1 = self._ink(g.contours)
        ym, gap = self._ym, 90
        cs = [rect(x0, y0, x1, ym - gap), rect(x0, ym + gap, x1, y1)]
        return Glyph("brokenbar", [0xA6], g.width, cs, note="| split round the math axis")

    def dblverticalbar(self):
        g = self.bar()
        x0, y0, x1, y1 = self._ink(g.contours)
        gap = 260
        t = x1 - x0
        cs = [rect(x0, y0, x1, y1), rect(x1 + gap, y0, x1 + gap + t, y1)]
        return Glyph("dblverticalbar", [0x2016], g.width + gap + t, cs, note="two |, 260 apart")

    def _dagger(self, name, uni, y0, bars, note):
        st, C = self.st, self.cap
        wt, wb = 176 * self.wk, 140 * self.wk
        W = 0.52 * C
        cx = W / 2
        stem = polygon([(cx - wb / 2, y0), (cx + wb / 2, y0), (cx + wt / 2, C), (cx - wt / 2, C)]).oriented(True)
        tb = st.barUpper - 16
        cs = [stem] + [rect(0, y - tb / 2, W, y + tb / 2) for y in bars]
        return self._own(name, uni, cs, 90, note)

    def dagger(self):
        C = self.cap
        return self._dagger("dagger", 0x2020, 0.26 * C, (0.73 * C,), "tapered stem (176 -> 140) from 0.26 to the cap height + bar, as Inter")

    def daggerdbl(self):
        C = self.cap
        return self._dagger("daggerdbl", 0x2021, 0, (0.75 * C, 0.26 * C), "tapered stem from the baseline + two bars")

    def _prime(self, x):
        C = self.cap
        wt, wb = 168 * self.wk, 120 * self.wk
        lean = 0.12 * C
        y0 = 0.62 * C
        return polygon([(x - wb / 2, y0), (x + wb / 2, y0), (x + lean + wt / 2, C), (x + lean - wt / 2, C)]).oriented(True)

    def minute(self):
        return self._own("minute", 0x2032, [self._prime(0)], 110, "the ' tick leaning 0.12 cap height to the right")

    def second(self):
        step = 168 * self.wk + 90
        return self._own("second", 0x2033, [self._prime(0), self._prime(step)], 110, "two ′")

    def perthousand(self):
        g = self.percent()
        lo = g.contours[2:4]
        x0, _, x1, _ = self._ink(lo)
        dx = x1 - x0 + 110
        cs = list(g.contours) + [c.translated(dx, 0) for c in lo]
        return Glyph("perthousand", [0x2030], g.width + dx, cs, note="% + a third ring, 110 after the lower one")

    def numero(self):
        N = self.N()
        o = self.ordmasculine()
        dx = N.width - self.sp.upperStraight + 30
        cs = list(N.contours) + [c.translated(dx, 0) for c in o.contours]
        return Glyph("numero", [0x2116], dx + o.width, cs, note="N + º")

    def estimated(self):
        e = self.e()
        return Glyph("estimated", [0x212E], e.width, list(e.contours), note="the e drawing")

    def Dcircled(self):
        D = self.D()
        cs, w = self._scaled(D, 0.42, 0.7 - 1.2 * (0.77 - self.sh.superiorWeight), 0, 0)
        h = self._ink(cs)[3]
        W, C = 1540, self.cap
        cs = [c.translated(W / 2 - w / 2 + 20, C / 2 - h / 2) for c in cs]
        return self._circled(cs, "Dcircled", 0x24B9, "hair ring + D x0.42, as ®")

    def _angle(self):
        t = self.st.punctStroke
        g = self.parenleft()
        _, y0, _, y1 = self._ink(g.contours)
        w, h = 0.27 * self.cap, y1 - y0
        hw = t / 2 / math.sin(math.atan2(h / 2, w))
        return self._chevron(hw, (y0 + y1) / 2, w - hw, h, t, True)

    def leftanglebracket_math(self):
        return self._own("leftanglebracket-math", 0x27E8, self._angle(), 110, "tall < spanning the parentheses")

    def rightanglebracket_math(self):
        cs = self._angle()
        x0, _, x1, _ = self._ink(cs)
        return self._own("rightanglebracket-math", 0x27E9, [c.mirrored_x((x0 + x1) / 2).oriented(True) for c in cs], 110, "⟨ mirrored")


SYMBOLS = [
    "fraction", "onequarter", "onehalf", "threequarters", "onethird", "twothirds", "zero_slash",
    "plusminus", "logicalnot", "notequal", "lessequal", "greaterequal", "approxequal", "radical", "summation",
    "product", "increment", "Ohm", "infinity", "partialdiff", "emptyset", "integral", "micro", "pi", "literSign",
    "rightArrow", "leftArrow", "leftRightArrow", "upArrow", "downArrow", "upDownArrow",
    "northEastArrow", "northWestArrow", "southEastArrow", "southWestArrow",
    "naira", "won", "kip", "tugrik", "peso", "ruble", "guarani", "cedi", "colonsign", "hryvnia", "tenge",
    "rupeeIndian", "liraTurkish", "manat", "sheqel", "lari", "baht", "bitcoin", "rupee",
    "brokenbar", "dblverticalbar", "dagger", "daggerdbl", "minute", "second", "perthousand", "numero",
    "estimated", "Dcircled", "leftanglebracket_math", "rightanglebracket_math",
]
GROUPS = ["small_figures", "shapes"]


CURRENCY = ["naira", "won", "kip", "tugrik", "peso", "ruble", "guarani", "cedi", "colonsign", "hryvnia", "tenge",
            "rupeeIndian", "liraTurkish", "manat", "sheqel", "lari", "baht", "bitcoin", "rupee"]


def build_symbols(builder) -> dict[str, Glyph]:
    out = {}
    for group in GROUPS:
        out.update(getattr(builder, group)())
    for method in SYMBOLS:
        if method in CURRENCY:
            with builder._drawn_at(builder._currency_strokes):
                g = getattr(builder, method)()
        else:
            g = getattr(builder, method)()
        out[g.name] = g
    return out


def features(glyphs: dict[str, Glyph]) -> str:
    """frac (numerators up to the fraction slash, denominators after it), sups,
    sinf and zero."""
    figs = " ".join(FIGURES)
    cls = lambda suffix: " ".join(f + suffix for f in FIGURES)
    tabular = "zero.tnum" in glyphs
    return "\n".join([
        f"@Figures = [{figs}];",
        f"@FiguresNumr = [{cls('.numr')}];",
        f"@FiguresDnom = [{cls('.dnom')}];",
        f"@FiguresSups = [{cls('superior')}];",
        f"@FiguresSinf = [{cls('inferior')}];",
        "",
        "feature frac {",
        "    lookup FractionSlash {",
        "        sub slash by fraction;",
        "    } FractionSlash;",
        "    lookup Numerators {",
        "        sub @Figures by @FiguresNumr;",
        "    } Numerators;",
        "    lookup Denominators {",
        "        sub [fraction @FiguresDnom] @FiguresNumr' by @FiguresDnom;",
        "    } Denominators;",
        "} frac;",
        "",
        "feature sups {",
        "    sub @Figures by @FiguresSups;",
        "} sups;",
        "",
        "feature sinf {",
        "    sub @Figures by @FiguresSinf;",
        "} sinf;",
        "",
        "feature subs {",
        "    sub @Figures by @FiguresSinf;",
        "} subs;",
        "",
        *(["feature tnum {",
           f"    sub @Figures by [{cls('.tnum')}];",
           "} tnum;",
           ""] if tabular else []),
        "feature zero {",
        "    sub zero by zero.zero;",
        *(["    sub zero.tnum by zero.zero.tnum;"] if tabular else []),
        "} zero;",
        "",
    ])
