"""Build Porto Faifo Mono Regular and Medium.

    .venv/bin/python scripts/build_mono.py

For each style, the recipes on that style's ``mono.pens`` pen with the ``mono``
widths and the mono letters (``pfsans.mono``), every glyph on the 1180-unit
cell, no kerning:

1. sources/PFMono-<style>.ufo
2. fontmake -> TTF and OTF, overlaps removed (as build.py)
3. ttfautohint -> hinted TTF; WOFF2 from it
4. fonts/mono/{otf,ttf,woff2}/PFMono-<style>.*

The fixed pitch is declared everywhere a client looks: post.isFixedPitch,
OS/2 PANOSE proportion 9 (monospaced) and one advance in hmtx.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fontTools.ttLib import TTFont  # noqa: E402

from build import SOURCE_DATE_EPOCH, VENV_BIN, fix_metrics, run, set_script_metadata  # noqa: E402
from pfsans import master  # noqa: E402
from pfsans.system import ROOT, load  # noqa: E402

STYLES = ("Regular", "Medium")


def source(STYLE: str) -> Path:
    system = load(STYLE, mono=True)
    family = system.meta.postscriptFamily
    src = ROOT / "sources" / f"{family}-{STYLE}.ufo"
    font, _ = master.write(src, STYLE, mono=True)
    info = font.info
    info.postscriptIsFixedPitch = True
    info.postscriptUnderlineThickness = system.raw["mono"]["underlineThickness"]
    info.openTypeOS2Panose = [2, 11, 5, 9, 0, 0, 0, 0, 0, 0]  # Latin text, sans, book, monospaced
    info.openTypeNameDescription = ("Porto Faifo Mono: the Porto Faifo Sans pen on a fixed 0.576 em cell, for code and "
                                    "tabular text in Vietnamese interfaces.")
    font.save(src, overwrite=True)
    print("wrote", src.relative_to(ROOT))
    return src


def compile_(src: Path) -> tuple[Path, Path]:
    family, STYLE = src.stem.split("-")
    tmp = ROOT / "build" / "fontmake" / "mono" / STYLE
    shutil.rmtree(tmp, ignore_errors=True)
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, PYTHONPATH=str(ROOT / "scripts"))
    for fmt in ("ttf", "otf"):
        run([VENV_BIN / "fontmake", "-u", src, "-o", fmt,
             "--output-path", tmp / f"{family}-{STYLE}.{fmt}", "--overlaps-backend", "pathops",
             "--filter", "pfsans.cleanup::CleanupFilter", "--flatten-components", "--verbose", "WARNING"],
            env=env, cwd=ROOT)
    return tmp / f"{family}-{STYLE}.ttf", tmp / f"{family}-{STYLE}.otf"


def finish(raw_ttf: Path, raw_otf: Path, y_max: int, y_min: int) -> list[Path]:
    import ttfautohint

    family, STYLE = raw_ttf.stem.split("-")
    out = ROOT / "fonts" / "mono"
    for sub in ("ttf", "otf", "woff2"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    otf, ttf = out / "otf" / f"{family}-{STYLE}.otf", out / "ttf" / f"{family}-{STYLE}.ttf"
    shutil.copy(raw_otf, otf)
    fix_metrics(raw_ttf, y_max, y_min)
    fix_metrics(otf, y_max, y_min)
    ttfautohint.ttfautohint(in_file=str(raw_ttf), out_file=str(ttf), hinting_range_min=8, hinting_range_max=50,
                            hinting_limit=200, default_script="latn", fallback_script="none",
                            increase_x_height=14, windows_compatibility=True, no_info=True)
    for path in (ttf, otf):
        f = TTFont(path, recalcTimestamp=False)
        set_script_metadata(f)
        f["head"].modified = f["head"].created
        if path == ttf:
            f["head"].flags |= 1 << 3
        f["post"].isFixedPitch = 1
        f.save(path, reorderTables=True)
    woff2 = out / "woff2" / f"{family}-{STYLE}.woff2"
    f = TTFont(ttf, recalcTimestamp=False)
    f.flavor = "woff2"
    f.save(woff2)
    for p in (ttf, otf, woff2):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")
    return [ttf, otf, woff2]


def check(paths: list[Path]) -> None:
    """One advance for every spacing glyph, marks at zero, fixed pitch set."""
    adv = load("Regular", mono=True).raw["mono"]["advance"]
    for p in paths:
        f = TTFont(p)
        widths = {w for w, _ in f["hmtx"].metrics.values()}
        assert widths <= {0, adv}, f"{p.name}: advances {sorted(widths)}"
        assert f["post"].isFixedPitch and f["OS/2"].panose.bProportion == 9, p.name
        assert "kern" not in f and ("GPOS" not in f or not any(
            l.LookupType == 2 for l in f["GPOS"].table.LookupList.Lookup)), f"{p.name}: kerning left"
    print(f"check: {len(paths)} files, every advance {adv} or 0, fixed pitch, no kerning")


def main() -> None:
    styles = sys.argv[1:] or STYLES
    raw = {style: compile_(source(style)) for style in dict.fromkeys((*STYLES, *styles))}
    heads = [TTFont(path)["head"] for pair in raw.values() for path in pair]
    y_max, y_min = max(head.yMax for head in heads), min(head.yMin for head in heads)
    for style in styles:
        check(finish(*raw[style], y_max, y_min))


if __name__ == "__main__":
    main()
