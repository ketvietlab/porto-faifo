"""Build Porto Faifo Sans from the design system.

    .venv/bin/python scripts/build.py

1. design-system.json  -> sources/PFSans-<Master>.ufo  (generated, committed;
                          one per weight, from Light through Black)
2. fontmake            -> TTF (quadratic) and OTF (CFF), overlaps removed
                          (then pfsans.cleanup drops shapeless points),
                          nested components flattened
3. ttfautohint         -> hinted TTF for Windows/Linux small sizes
4. fontTools           -> WOFF2 from the hinted TTF
5. win metrics from the real glyph bounds of the whole family (the same in
   every weight), fixed timestamps (reproducible)
6. Text/Display spacing -> one opsz-only TTF/WOFF2 per fixed weight; static
   hinted fonts remain available alongside the optical files
7. every weight at Text and Display -> PortoFaifoSans[opsz,wght] (wght 300-900, opsz
   8-72)
"""

from __future__ import annotations

import os
from copy import deepcopy
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fontTools.ttLib import TTFont, newTable  # noqa: E402
from fontTools.ttLib.tables.ttProgram import Program  # noqa: E402
from fontTools.designspaceLib import DesignSpaceDocument  # noqa: E402
from fontTools.otlLib.builder import buildStatTable  # noqa: E402

from pfsans import master  # noqa: E402
from pfsans.system import ROOT, load  # noqa: E402

VENV_BIN = Path(sys.executable).parent
# 2026-10-20 00:00:00 UTC: fixed so identical sources give identical binaries.
SOURCE_DATE_EPOCH = "1792454400"


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def fix_metrics(path: Path, y_max: int, y_min: int) -> None:
    font = TTFont(path, recalcTimestamp=False)
    os2, hhea = font["OS/2"], font["hhea"]
    os2.usWinAscent = max(y_max, os2.sTypoAscender)
    os2.usWinDescent = max(-y_min, -os2.sTypoDescender)
    hhea.ascent = os2.sTypoAscender
    hhea.descent = os2.sTypoDescender
    hhea.lineGap = os2.sTypoLineGap
    font.save(path)


def set_script_metadata(font: TTFont) -> None:
    font["meta"] = newTable("meta")
    font["meta"].data = {"dlng": "Latn", "slng": "Latn"}


def set_unhinted_gasp(font: TTFont) -> None:
    font["gasp"] = newTable("gasp")
    font["gasp"].gaspRange = {0xFFFF: 0x000F}


def main() -> None:
    styles = load().masters
    raw = {style: compile_master(style) for style in styles}
    # One set of win metrics for the family, so weights share a line box.
    heads = [TTFont(path)["head"] for pair in raw.values() for path in pair]
    y_max, y_min = max(h.yMax for h in heads), min(h.yMin for h in heads)
    for style in styles:
        finish_master(style, *raw[style], y_max, y_min)
        build_optical(style, y_max, y_min)
    build_variable(styles, y_max, y_min)


def compile_master(style: str) -> tuple[Path, Path]:
    system = load(style)
    family = system.font_stem
    src = ROOT / "sources" / f"{system.meta.sourceFamily}-{style}.ufo"
    src.parent.mkdir(parents=True, exist_ok=True)
    master.write(src, style)
    print("wrote", src.relative_to(ROOT))

    tmp = ROOT / "build" / "fontmake" / style
    shutil.rmtree(tmp, ignore_errors=True)
    # scripts/ on the path so fontmake can load the post-overlap cleanup filter.
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts"))
    # One fontmake call per format: a combined "-o ttf otf" run lets the CFF
    # decomposition leak into the TTF, turning every Vietnamese composite into
    # re-approximated contours (caught by the NFC/NFD pixel check).
    for fmt in ("ttf", "otf"):
        run(
            [
                VENV_BIN / "fontmake", "-u", src, "-o", fmt,
                "--output-path", tmp / f"{family}-{style}.{fmt}", "--overlaps-backend", "pathops",
                "--filter", "pfsans.cleanup::CleanupFilter",
                "--flatten-components", "--verbose", "WARNING",
            ],
            env=env,
            cwd=ROOT,
        )
    return tmp / f"{family}-{style}.ttf", tmp / f"{family}-{style}.otf"


def finish_master(style: str, raw_ttf: Path, raw_otf: Path, y_max: int, y_min: int) -> None:
    family = load(style).font_stem
    fonts = ROOT / "fonts"
    for sub in ("ttf", "otf", "woff2"):
        (fonts / sub).mkdir(parents=True, exist_ok=True)
    otf = fonts / "otf" / f"{family}-{style}.otf"
    ttf = fonts / "ttf" / f"{family}-{style}.ttf"
    shutil.copy(raw_otf, otf)
    fix_metrics(raw_ttf, y_max, y_min)
    fix_metrics(otf, y_max, y_min)

    import ttfautohint

    ttfautohint.ttfautohint(
        in_file=str(raw_ttf),
        out_file=str(ttf),
        hinting_range_min=8,
        hinting_range_max=50,
        hinting_limit=200,
        default_script="latn",
        fallback_script="none",
        increase_x_height=14,
        windows_compatibility=True,
        no_info=True,
    )
    # ttfautohint rewrites tables; restore the fixed timestamp.
    for path in (ttf, otf):
        f = TTFont(path, recalcTimestamp=False)
        set_script_metadata(f)
        f["head"].modified = f["head"].created
        if path == ttf:
            f["head"].flags |= 1 << 3  # hinted: round ppem to integers
        f.save(path, reorderTables=True)

    woff2 = fonts / "woff2" / f"{family}-{style}.woff2"
    f = TTFont(ttf, recalcTimestamp=False)
    f.flavor = "woff2"
    f.save(woff2)
    for p in (ttf, otf, woff2):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")


def build_optical(style: str, y_max: int, y_min: int) -> None:
    """One opsz-only variable font per weight; no cross-weight interpolation.

    These fonts are unhinted. Keep the existing hinted static TTF/WOFF2 set for
    clients which need it. Optical masters translate whole glyphs, so outline
    topology remains identical within each designspace.
    """
    system = load(style)
    settings = system.raw["opticalSizing"]["axis"]
    family = system.font_stem + "Optical"
    source_dir = ROOT / "build" / "optical-sources"
    source_dir.mkdir(parents=True, exist_ok=True)
    ds = DesignSpaceDocument()
    ds.addAxisDescriptor(
        name="Optical Size", tag="opsz", minimum=settings["minimum"],
        default=settings["default"], maximum=settings["maximum"],
        map=[tuple(pair) for pair in settings["map"]],
    )
    for label, coord in (("Text", settings["default"]), ("Display", settings["maximum"])):
        path = source_dir / f"{family}-{style}-{label}.ufo"
        font, glyphs = master.write(path, style, optical=label)
        # Union once, then translate the same contours at Display. Independent
        # pathops unions can choose different start points or round a joined
        # cedilla/ogonek differently, even for translated input.
        from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter
        from pfsans.cleanup import CleanupFilter
        from pfsans.optical import display_spacing

        if label == "Text":
            reductions = display_spacing(glyphs, system)
            RemoveOverlapsFilter(backend="pathops")(font)
            CleanupFilter()(font)
            text_font = font
        else:
            for glyph in font:
                glyph.clearContours()
                for source in text_font[glyph.name].contours:
                    contour = deepcopy(source)
                    for point in contour.points:
                        point.x -= reductions[glyph.name][0]
                    glyph.appendContour(contour)
        font.save(path, overwrite=True)
        ds.addSourceDescriptor(
            path=str(path), name=f"{style} {label}",
            familyName=system.meta.familyName + " Optical", styleName=style,
            location={"Optical Size": coord},
            copyInfo=label == "Text", copyLib=label == "Text",
            copyFeatures=label == "Text",
        )
        ds.addInstanceDescriptor(
            name=f"{style} {label}", familyName=system.meta.familyName + " Optical",
            styleName=style if label == "Text" else style + " Display",
            postScriptFontName=f"{family}-{style}" + ("Display" if label == "Display" else ""),
            userLocation={"Optical Size": settings["default"] if label == "Text" else settings["display"]},
        )
    ds_path = source_dir / f"{family}-{style}.designspace"
    ds.write(ds_path)
    dest = ROOT / "fonts" / "variable"
    dest.mkdir(parents=True, exist_ok=True)
    ttf = dest / f"{family}-{style}.ttf"
    run([
        VENV_BIN / "fontmake", "-m", ds_path, "-o", "variable",
        "--output-path", ttf, "--overlaps-backend", "pathops",
        "--filter", "pfsans.cleanup::CleanupFilter", "--flatten-components",
        "--verbose", "WARNING",
    ], env=dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts")), cwd=ROOT)
    fix_metrics(ttf, y_max, y_min)
    font = TTFont(ttf, recalcTimestamp=False)
    # A fixed weight in STAT helps applications group the opsz files.
    buildStatTable(font, [
        {"tag": "wght", "name": "Weight", "ordering": 0,
         "values": [{"value": system.wght, "name": style, "flags": 2 if style == "Regular" else 0}]},
        {"tag": "opsz", "name": "Optical Size", "ordering": 1,
         "values": [
             {"nominalValue": settings["default"], "rangeMinValue": settings["minimum"],
              "rangeMaxValue": settings["default"], "name": "Text", "flags": 2},
             {"value": settings["display"], "name": "Display"},
         ]},
    ], macNames=False)
    set_script_metadata(font)
    set_unhinted_gasp(font)
    # Smart dropout for monochrome rasterizers, not stem/grid hinting.
    font["prep"] = newTable("prep")
    font["prep"].program = Program()
    font["prep"].program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 1)
    font["head"].modified = font["head"].created
    font.save(ttf, reorderTables=True)
    font.flavor = "woff2"
    woff2 = ttf.with_suffix(".woff2")
    font.save(woff2)
    for path in (ttf, woff2):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")


def overlapping(font, name) -> bool:
    """True when the glyph's contours (components drawn in) overlap: their
    signed areas add up to more than the area of their union."""
    import pathops
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    rec = DecomposingRecordingPen(font)
    font[name].draw(rec)
    if not rec.value:
        return False
    total, path = AreaPen(), pathops.Path()
    rec.replay(total)
    rec.replay(path.getPen())
    union = AreaPen()
    pathops.simplify(path, fix_winding=True).draw(union)
    return abs(abs(total.value) - abs(union.value)) > 1


def build_variable(styles: list[str], y_max: int, y_min: int) -> None:
    """One font with wght (Light 300 … Black 900) and opsz (Text 16 … Display 48).

    Every weight is a master at Text and at Display spacing, all written from
    the same recipes, so the outlines interpolate point for point. Overlaps are
    kept and flagged: a union per master gives each weight its own topology.
    The intermediate weights use the same design sources as the static fonts.
    Unhinted, like the optical fonts.
    """
    system = load()
    var, opt = system.raw["variable"], system.raw["opticalSizing"]["axis"]
    family = system.meta.familyName
    ps = system.font_stem
    source_dir = ROOT / "build" / "variable-sources"
    shutil.rmtree(source_dir, ignore_errors=True)
    source_dir.mkdir(parents=True)
    wmap = [tuple(pair) for pair in var["weight"]["map"]]
    from fontTools.varLib.models import piecewiseLinearMap

    design = lambda wght: piecewiseLinearMap(wght, dict(wmap))  # user weight -> design coordinate
    ds = DesignSpaceDocument()
    ds.addAxisDescriptor(name="Weight", tag="wght", minimum=var["weight"]["minimum"],
                         default=var["weight"]["default"], maximum=var["weight"]["maximum"], map=wmap)
    ds.addAxisDescriptor(name="Optical Size", tag="opsz", minimum=opt["minimum"], default=opt["default"],
                         maximum=opt["maximum"], map=[tuple(pair) for pair in opt["map"]])
    sources = []
    for style in styles:
        for label, coord in (("Text", opt["default"]), ("Display", opt["maximum"])):
            path = source_dir / f"{ps}-{style}-{label}.ufo"
            font, _ = master.write(path, style, optical=label)
            sources.append((path, font, style, label, coord))
    flagged = {n for _, font, *_ in sources for n in font.keys() if overlapping(font, n)}
    for path, font, style, label, coord in sources:
        default = style == "Regular" and label == "Text"
        for name in flagged:
            font[name].lib["public.truetype.overlap"] = True
        if default:
            info = font.info
            info.familyName = info.styleMapFamilyName = family
            info.styleName, info.styleMapStyleName = "Regular", "regular"
            info.postscriptFontName, info.postscriptFullName = f"{ps}-Regular", f"{family} Regular"
        font.save(path, overwrite=True)
        ds.addSourceDescriptor(
            path=str(path), name=f"{style} {label}", familyName=family, styleName=f"{style} {label}",
            location={"Weight": design(load(style).wght), "Optical Size": coord},
            copyInfo=default, copyLib=default, copyFeatures=default,
        )
    for name, wght in var["instances"].items():
        ds.addInstanceDescriptor(
            name=name, familyName=family, styleName=name,
            postScriptFontName=f"{ps}-{name}",
            userLocation={"Weight": wght, "Optical Size": opt["default"]},
        )
    ds_path = source_dir / f"{ps}.designspace"
    ds.write(ds_path)
    ttf = ROOT / "fonts" / "variable" / f"{system.variable_stem}.ttf"
    run([
        VENV_BIN / "fontmake", "-m", ds_path, "-o", "variable", "--output-path", ttf,
        "--flatten-components", "--verbose", "WARNING",
    ], env=dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts")), cwd=ROOT)
    fix_metrics(ttf, y_max, y_min)
    font = TTFont(ttf, recalcTimestamp=False)
    # fontmake round-trips instance positions through the design map. Restore
    # the exact named weight when the map has a short rounding plateau.
    for inst in font["fvar"].instances:
        style = font["name"].getDebugName(inst.subfamilyNameID)
        inst.coordinates["wght"] = var["instances"][style]
        if style == "Regular":
            inst.subfamilyNameID = 2
            inst.postscriptNameID = 6
    weights = [{"value": w, "name": n, "flags": 2 if n == "Regular" else 0, **({"linkedValue": 700} if n == "Regular" else {})}
               for n, w in var["instances"].items()]
    buildStatTable(font, [
        {"tag": "wght", "name": "Weight", "ordering": 0, "values": weights},
        {"tag": "opsz", "name": "Optical Size", "ordering": 1,
         "values": [{"value": size, "name": f"{size}pt"}
                    for size in sorted({opt[key] for key in ("minimum", "default", "display", "maximum")})]},
    ], macNames=False)
    set_script_metadata(font)
    set_unhinted_gasp(font)
    # Smart dropout for monochrome rasterizers, not stem/grid hinting.
    font["prep"] = newTable("prep")
    font["prep"].program = Program()
    font["prep"].program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 1)
    font["head"].modified = font["head"].created
    font.save(ttf, reorderTables=True)
    font.flavor = "woff2"
    woff2 = ttf.with_suffix(".woff2")
    font.save(woff2)
    print(f"{len(flagged)} glyphs flagged as overlapping")
    for path in (ttf, woff2):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
