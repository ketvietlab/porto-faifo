"""Check PFSansVariable: axes, weight midpoints, names, OTS, overlap flags,
and that every master location reproduces the static and optical fonts.

    .venv/bin/python scripts/verify_variable.py

Instances are cut with fontTools' instancer and shaped with HarfBuzz, so the
checks exercise the real gvar, HVAR and variable GPOS data.
"""

from __future__ import annotations

import json
import tempfile
import unicodedata
from pathlib import Path

import freetype
import numpy as np
import ots
import pathops
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from pfsans.proof import Face
from pfsans.system import ROOT, load
from verify import TABULAR, Report
from verify_optical import pair_gap

WORDS = ["Nguyễn Thị Mỹ Hằng", "Đường Nguyễn Huệ", "ẤN ĐỘ", "Ưu đãi", "Thưởng 85.740.000 ₫",
         "ấ ầ ẩ ẫ ậ ế ề ể ễ ệ ố ồ ổ ỗ ộ", "Ģirts Ķekava", "Šťastný", "AVA Ty LT r. f/"]
DIFFICULT = ("ĩ}", "Fĩ", "/Ī", "[Î", "f/", "AV", "Ty", "LT", "r.", "ẤV")
# Outlines are compared on FreeType's monochrome (non-zero) raster at 2 units
# per pixel: `edge_gap` is how far the farthest differing pixel lies from the
# reference outline, rounded up to 2 units (a glyph shifted by 3 units reads 4).
# pathops cannot stand in: it unions some overlapping quadratic contours of the
# variable font wrongly (§ loses its counters), while every renderer fills them
# non-zero. Static fonts are unions of the contours the variable font keeps,
# converted to quadratics separately, and each conversion may stray 0.001 em
# (2 units) from the cubic, so edges differ by up to 4 units; so do precomposed
# ç ş, whose unioned cedilla is converted apart from the mark. A wrong master
# location moves edges by tens of units (Regular against Medium n: 40).
UNITS_PER_PX = 2
EDGE = 4
# Interior masters with overlapping variation supports can accumulate a
# one-unit rounding difference in advances and positioning. The outer
# masters and Medium match exactly.
ROUNDED = {"SemiBold", "Bold", "ExtraBold"}


class Mono:
    """Monochrome FreeType raster of positioned glyphs (glyph id, x, y in units)."""

    def __init__(self, path):
        self.ft = freetype.Face(str(path))
        self.ft.set_pixel_sizes(0, self.ft.units_per_EM // UNITS_PER_PX)

    def run(self, glyphs):
        layers = []
        for gid, x, y in glyphs:
            self.ft.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000),
                                  freetype.Vector(round(x * 64 / UNITS_PER_PX), round(y * 64 / UNITS_PER_PX)))
            self.ft.load_glyph(gid, freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            g = self.ft.glyph
            if g.bitmap.width:
                raw = np.frombuffer(bytes(g.bitmap.buffer), np.uint8).reshape(g.bitmap.rows, g.bitmap.pitch)
                layers.append((g.bitmap_top, g.bitmap_left, np.unpackbits(raw, axis=1)[:, :g.bitmap.width].astype(bool)))
        return layers

    def text(self, face, text):
        x, glyphs = 0, []
        for info, pos in face.shape(text):
            glyphs.append((info.codepoint, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance
        return self.run(glyphs)


def _dilate(m):
    d = m.copy()
    d[1:] |= m[:-1]
    d[:-1] |= m[1:]
    d[:, 1:] |= m[:, :-1]
    d[:, :-1] |= m[:, 1:]
    return d


def edge_gap(layers, reference, limit=32):
    every = layers + reference
    if not every:
        return 0
    top, left = max(t for t, _, _ in every) + 2, min(l for _, l, _ in every) - 2
    h = max(top - t + b.shape[0] for t, _, b in every) + 2
    w = max(l - left + b.shape[1] for _, l, b in every) + 2
    a, b = np.zeros((h, w), bool), np.zeros((h, w), bool)
    for canvas, group in ((a, layers), (b, reference)):
        for t, l, bits in group:
            canvas[top - t:top - t + bits.shape[0], l - left:l - left + bits.shape[1]] |= bits
    differ = a ^ b
    if not differ.any():
        return 0
    reach = _dilate(b) & _dilate(~b)
    for k in range(limit):
        if not (differ & ~reach).any():
            return (k + 1) * UNITS_PER_PX
        reach = _dilate(reach)
    return 10 ** 6


def within(a, b, tolerance):
    return len(a) == len(b) and all(x[0] == y[0] and all(abs(u - v) <= tolerance for u, v in zip(x[1:], y[1:])) for x, y in zip(a, b))


def positions(face, text):
    return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset) for i, p in face.shape(text)]


def ink(font, name):
    gs = font.getGlyphSet()
    rec = DecomposingRecordingPen(gs)
    gs[name].draw(rec)
    path, area = pathops.Path(), AreaPen()
    rec.replay(path.getPen())
    pathops.simplify(path, fix_winding=True).draw(area)
    return abs(area.value)


def stem(font, ch, y):
    from pfsans.measure import Outlines

    o = Outlines(font)
    runs = o.runs(ch, y, 1)
    return runs[0][1] - runs[0][0]


def main():
    report = Report()
    system = load()
    var, opt = system.raw["variable"], system.raw["opticalSizing"]["axis"]
    styles = system.masters
    path = ROOT / "fonts" / "variable" / f"{system.meta.postscriptFamily}{var['familySuffix']}.ttf"
    vf = TTFont(path)
    regular = TTFont(ROOT / "fonts" / "ttf" / f"{system.meta.postscriptFamily}-Regular.ttf")
    w = var["weight"]

    # ------------------------------------------------------------ structure
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in vf["fvar"].axes}
    report.check("variable", "axes wght 300-400-900 and opsz 8-16-72",
                 axes == {"wght": (w["minimum"], w["default"], w["maximum"]),
                          "opsz": (opt["minimum"], opt["default"], opt["maximum"])}, str(axes))
    from fontTools.varLib.models import piecewiseLinearMap

    seg = vf["avar"].segments["wght"]
    norm = lambda v: (v - w["default"]) / ((w["maximum"] - w["default"]) if v >= w["default"] else (w["default"] - w["minimum"]))
    mapped = {v: piecewiseLinearMap(norm(v), seg) for v in (500, 600, 700, 800, 900)}
    report.check("variable", "avar maps 600 and 800 to their design midpoints",
                 all(mapped[lo] < mapped[mid] < mapped[hi]
                     and abs(mapped[mid] - (mapped[lo] + mapped[hi]) / 2) <= 1 / 16384
                     for lo, mid, hi in ((500, 600, 700), (700, 800, 900))), str(mapped))
    names = vf["name"]
    got = [(names.getDebugName(i.subfamilyNameID), i.coordinates["wght"], i.coordinates["opsz"]) for i in vf["fvar"].instances]
    want = [(n, float(v), float(opt["default"])) for n, v in var["instances"].items()]
    report.check("variable", f"{len(want)} named instances, including SemiBold and ExtraBold", got == want, str(got) if got != want else "")
    stat = vf["STAT"].table
    values = {(stat.DesignAxisRecord.Axis[v.AxisIndex].AxisTag, names.getDebugName(v.ValueNameID)) for v in stat.AxisValueArray.AxisValue}
    report.check("variable", "STAT names every weight and optical size",
                 all(("wght", n) in values for n in var["instances"])
                 and {("opsz", f"{opt[key]}pt") for key in ("minimum", "default", "display", "maximum")} <= values)
    report.check("variable", "family name, default style and weight class",
                 names.getDebugName(1) == system.meta.familyName and names.getDebugName(2) == "Regular"
                 and vf["OS/2"].usWeightClass == 400)
    report.check("variable", "full charset and glyph order of the static fonts",
                 vf.getBestCmap() == regular.getBestCmap() and vf.getGlyphOrder() == regular.getGlyphOrder())
    report.check("variable", "embedding and line metrics as the static fonts", vf["OS/2"].fsType == 0 and all(
        getattr(vf["hhea"], k) == getattr(regular["hhea"], k) for k in ("ascent", "descent", "lineGap"))
        and all(getattr(vf["OS/2"], k) == getattr(regular["OS/2"], k) for k in ("sTypoAscender", "sTypoDescender", "usWinAscent", "usWinDescent")))
    for fmt in ("ttf", "woff2"):
        result = ots.sanitize(str(path.with_suffix("." + fmt)), capture_output=True)
        report.check("variable", f"OTS {fmt}", result.returncode == 0, result.stderr.decode() if result.returncode else "")
    web = TTFont(path.with_suffix(".woff2"))
    report.check("variable", "WOFF2 tables equal TTF", all(
        vf.getTableData(tag) == web.getTableData(tag) for tag in vf.keys() if tag not in ("GlyphOrder", "head")))

    # ---------------------------------------------------------- overlap flags
    glyf = vf["glyf"]
    unflagged = []
    for name in vf.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours == 0:
            continue
        gs = vf.getGlyphSet()
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        total, p, union = AreaPen(), pathops.Path(), AreaPen()
        rec.replay(total)
        rec.replay(p.getPen())
        pathops.simplify(p, fix_winding=True).draw(union)
        overlaps = abs(abs(total.value) - abs(union.value)) > 1
        flagged = (g.components[0].flags & 0x400) if g.isComposite() else (g.flags[0] & 0x40)
        if overlaps and not flagged:
            unflagged.append(name)
    report.check("variable", "overlapping glyphs carry OVERLAP_SIMPLE / OVERLAP_COMPOUND", not unflagged, ", ".join(unflagged[:12]))

    # Letters only: ≠ decomposes to = + U+0338, which the font does not carry.
    decomposed = [chr(cp) for cp in vf.getBestCmap() if len(unicodedata.normalize("NFD", chr(cp))) > 1 and unicodedata.category(chr(cp)).startswith("L")]
    worst = {}
    with tempfile.TemporaryDirectory(prefix="pfsans-wght-check-") as folder:
        def cut(wght, opsz):
            dest = Path(folder) / f"w{wght}-o{opsz}.ttf"
            if not dest.exists():
                instantiateVariableFont(vf, {"wght": wght, "opsz": opsz}, inplace=False).save(dest)
            return TTFont(dest), Face(dest)

        # ----------------------------------------- masters = static/optical
        for style in styles:
            wght = load(style).wght
            report.prefix = f"{style} {wght}: "
            static = ROOT / "fonts" / "ttf" / f"{system.meta.postscriptFamily}-{style}.ttf"
            optical = ROOT / "fonts" / "variable" / f"{system.meta.postscriptFamily}Optical-{style}.ttf"
            for label, opsz, ref_path, ref_axes in (("Text", opt["default"], static, None),
                                                   ("Display", opt["display"], optical, {"opsz": opt["display"]})):
                inst, face = cut(wght, opsz)
                ref = TTFont(ref_path)
                ref_file = ref_path
                if ref_axes:
                    ref = instantiateVariableFont(ref, ref_axes, inplace=False)
                    ref_file = Path(folder) / f"ref-{style}-{label}.ttf"
                    ref.save(ref_file)
                ref_face = Face(ref_file)
                tol = 1 if style in ROUNDED else 0
                adv = [n for n in inst.getGlyphOrder() if abs(inst["hmtx"][n][0] - ref["hmtx"][n][0]) > tol]
                report.check("variable", f"{label}: advances equal the {ref_path.parent.name} font" + (" (±1 unit)" if tol else ""),
                             not adv, ", ".join(adv[:12]))
                moved = [t for t in WORDS + list(DIFFICULT) if not within(positions(face, t), positions(ref_face, t), tol)]
                report.check("variable", f"{label}: kerning and mark positions equal (HarfBuzz)" + (" (±1 unit)" if tol else ""),
                             not moved, repr(moved[:6]))
                mono, ref_mono = Mono(Path(folder) / f"w{wght}-o{opsz}.ttf"), Mono(ref_file)
                gaps = {name: edge_gap(mono.run([(gid, 0, 0)]), ref_mono.run([(gid, 0, 0)]))
                        for gid, name in enumerate(inst.getGlyphOrder())}
                worst[f"{style} {label}"] = f"{sum(not g for g in gaps.values())}/{len(gaps)} identical, max {max(gaps.values())} units"
                bad = sorted(((g, n) for n, g in gaps.items() if g > EDGE), reverse=True)
                report.check("variable", f"{label}: outlines within {EDGE} units of the {ref_path.parent.name} font ({len(gaps)} glyphs)",
                             not bad, repr(bad[:8]))

        report.prefix = ""
        for name, weight in (("SemiBold", 600), ("ExtraBold", 800)):
            live = Face(path, {"wght": weight, "opsz": opt["default"]})
            _, instance = cut(weight, opt["default"])
            report.check("variable", f"CSS weight {weight} shapes as {name} without instancing (HarfBuzz)",
                         all(positions(live, t) == positions(instance, t) for t in WORDS + list(DIFFICULT)))

        # -------------------------------------------------- monotonic weight
        steps = [300, 350, 400, 450, 500, 600, 650, 700, 800, 900]
        fonts = {s: cut(s, opt["default"])[0] for s in steps}
        stems = {s: [stem(fonts[s], ch, y) for ch, y in (("n", 330), ("H", 440), ("o", 544), ("O", 728))] for s in steps}
        heavier = all(all(b > a for a, b in zip(stems[x], stems[y])) for x, y in zip(steps, steps[1:]))
        report.check("variable", "n H o O stems grow along the axis", heavier,
                     "; ".join(f"{s} " + " ".join(f"{v:.0f}" for v in stems[s]) for s in steps))
        thinner = []
        for name in vf.getGlyphOrder():
            areas = [ink(fonts[s], name) for s in steps]
            if any(b < a * 0.995 - 1 for a, b in zip(areas, areas[1:])):
                thinner.append(name)
        report.check("variable", "no glyph loses ink as the weight rises (10 weights)", not thinner, ", ".join(thinner[:12]))

        # ---------------------------------------------- between the masters
        for wght, opsz in ((350, 16), (650, 16), (800, 16), (800, 48), (900, 32)):
            report.prefix = f"wght {wght} opsz {opsz}: "
            inst, face = cut(wght, opsz)
            mono = Mono(Path(folder) / f"w{wght}-o{opsz}.ttf")
            stripped = TTFont(Path(folder) / f"w{wght}-o{opsz}.ttf")
            for table in stripped["cmap"].tables:
                table.cmap = {cp: n for cp, n in table.cmap.items() if len(unicodedata.normalize("NFD", chr(cp))) == 1}
            nfd_path = Path(folder) / f"nfd-{wght}-{opsz}.ttf"
            stripped.save(nfd_path)
            nfd, nfd_mono = Face(nfd_path), Mono(nfd_path)
            mismatch = {}
            for text in decomposed + WORDS:
                g = edge_gap(mono.text(face, text), nfd_mono.text(nfd, unicodedata.normalize("NFD", text)))
                if g > EDGE:
                    mismatch[text] = g
            report.check("variable", f"NFC = base + GPOS marks within {EDGE} units ({len(decomposed)} letters + {len(WORDS)} texts)",
                         not mismatch, repr(list(mismatch.items())[:10]))
            widths = {sum(p.x_advance for _, p in face.shape(ch, {"tnum": True})) for ch in TABULAR}
            report.check("variable", "tabular figures, currency and math share one width", len(widths) == 1, str(sorted(widths)))
            lo, hi = max(s for s in steps if s <= wght), min(s for s in steps if s >= wght)
            contacts = {}
            for pair in DIFFICULT:
                gap = pair_gap(inst, face, pair)
                ends = [pair_gap(*cut(s, opsz), pair) for s in {lo, hi, *(v for v in (300, 400, 500, 700, 900) if abs(v - wght) <= 200)}]
                if gap < min(0, min(ends)) - 2:
                    contacts[pair] = round(gap)
            report.check("variable", "difficult pairs no closer than at the neighbouring weights", not contacts, str(contacts))
            ys = [pt[1] for n in inst.getGlyphOrder() if inst["glyf"][n].numberOfContours
                  for pt in inst["glyf"][n].getCoordinates(inst["glyf"])[0]]
            report.check("variable", "win metrics cover every glyph", max(ys) <= vf["OS/2"].usWinAscent and min(ys) >= -vf["OS/2"].usWinDescent)
    report.prefix = ""
    report.info("variable", f"outline edges against the static/optical fonts ({UNITS_PER_PX} units per pixel)", json.dumps(worst, ensure_ascii=False))
    out = ROOT / "build" / "qa"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify-variable.json").write_text(json.dumps(report.rows, ensure_ascii=False, indent=2))
    passed = sum(row["ok"] is True for row in report.rows)
    print(f"\n{passed} passed, {len(report.failed)} failed")
    raise SystemExit(bool(report.failed))


if __name__ == "__main__":
    main()
