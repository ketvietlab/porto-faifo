"""Build Porto Faifo Symbols.

    .venv/bin/python scripts/build_symbols.py     (after scripts/build.py)

design-system.json + symbols/symbol-system.json give one pen per size and
weight, with the stroke taken from the Porto Faifo Sans stems.  The recipes in
scripts/pfsymbols then draw:

    symbols/svg/<size>/<weight>/<name>.svg   (and <name>-fill.svg)
    symbols/sprites/pf-symbols-<size>-<weight>.svg   <symbol id="pf-<name>">
    symbols/manifest.json                    names, aliases, groups, meanings
    symbols/preview.html                     every icon on one page

The ₫ symbol is read from the built OTF, so build the fonts first.

Checks: every icon draws something, stays on its canvas and inside the padding
(2 of 24 units) within a small tolerance, and ink grows steadily with weight.
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pfsans.system import ROOT  # noqa: E402
from pfsymbols import svg as out  # noqa: E402
from pfsymbols.kit import pen, symbol_system, union  # noqa: E402
from pfsymbols.registry import ICONS  # noqa: E402

SYMBOLS = ROOT / "symbols"
PAD_TOLERANCE = 0.75  # px a stroke end or miter may cross the padding
LICENCE = ("Porto Faifo Symbols. Copyright (c) 2026 The Porto Faifo Project Authors. "
           "SIL Open Font License 1.1, https://openfontlicense.org")


def stamp(text: str) -> str:
    """Put the owner and licence inside the root element of an SVG."""
    head, rest = text.split(">", 1)
    return f"{head}><!-- {LICENCE} -->{rest}"


def ink_check(ink) -> list[str]:
    """Ink grows a steady step per weight.  A jump means a boolean operation
    went wrong and filled a counter."""
    bad = []
    for (size, name), seq in sorted(ink.items()):
        for (w0, a0), (w1, a1) in zip(seq, seq[1:]):
            if a0 > 0 and not 0.98 <= a1 / a0 <= 1.6:
                bad.append(f"{size}/{name}: ink {w0} -> {w1} x{a1 / a0:.2f}")
    return bad


def main() -> int:
    sym = symbol_system()
    design = sym["grid"]["design"]
    sizes = sorted(int(s) for s in sym["sizes"] if s.isdigit())
    weights = sym["weights"]
    for sub in ("svg", "sprites"):
        shutil.rmtree(SYMBOLS / sub, ignore_errors=True)
    (SYMBOLS / "sprites").mkdir(parents=True)

    problems, ink, preview = [], {}, {}
    for size in sizes:
        hint = sym["sizes"][str(size)]["hint"]
        for weight in weights:
            p = pen(weight, size, sym)
            folder = SYMBOLS / "svg" / str(size) / weight.lower()
            folder.mkdir(parents=True)
            sprite = []
            for icon in ICONS:
                for fill in (False, True) if icon.fill else (False,):
                    reg = icon.draw(p, fill=fill)
                    ghost = icon.ghost(p) if icon.ghost and not fill else None
                    suffix = "-fill" if fill else ""
                    where = f"{size}/{weight}/{icon.name}{suffix}"
                    b = out.bounds(union(reg, ghost) if ghost else reg, size, design)
                    if b is None:
                        problems.append(f"{where}: empty")
                        continue
                    pad = sym["grid"]["padding"] * size / design
                    if min(b) < -1e-6 or max(b) > size + 1e-6:
                        problems.append(f"{where}: off canvas")
                    elif min(b) < pad - PAD_TOLERANCE or max(b) > size - pad + PAD_TOLERANCE:
                        problems.append(f"{where}: crosses padding")
                    if not fill:
                        ink.setdefault((size, icon.name), []).append((weight, abs(reg.area)))
                    d = out.path_data(reg, size, design, hint)
                    dg = out.path_data(ghost, size, design, hint) if ghost else ""
                    body = f'<path d="{d}"/>' + (f'<path opacity="{out.GHOST}" d="{dg}"/>' if dg else "")
                    for code in [icon.name] + icon.aliases:  # aliases ship as copies
                        (folder / f"{code}{suffix}.svg").write_text(stamp(out.svg(d, size, dg)), encoding="utf-8")
                        sprite.append(f'  <symbol id="pf-{code}{suffix}" viewBox="0 0 {size} {size}">{body}</symbol>')
                    if size == 24 and weight == "Regular":
                        preview[icon.name + suffix] = body
            (SYMBOLS / "sprites" / f"pf-symbols-{size}-{weight.lower()}.svg").write_text(
                f"<!-- {LICENCE} -->\n<!-- {size} px, {weight}. Aliases have their own ids. -->\n"
                '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n' + "\n".join(sprite) + "\n</svg>\n",
                encoding="utf-8")
    problems += ink_check(ink)

    version = sym["meta"]["version"]
    catalog = {
        "name": sym["meta"]["familyName"], "version": version, "license": "OFL-1.1",
        "sizes": sizes, "weights": weights,
        "files": "svg/<size>/<weight>/<name>.svg",
        "symbols": [
            {"name": i.name, "fill": i.fill, "aliases": i.aliases, "group": i.group, "meaning": i.meaning,
             "lucide": i.lucide, "freedesktop": [n for n in [i.fdo, *i.fdo_more] if n]}
            for i in ICONS
        ],
    }
    (SYMBOLS / "manifest.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cells = "\n".join(
        f'<figure title="{html.escape(i.meaning)}"><svg viewBox="0 0 24 24" width="24" height="24">{preview[i.name]}</svg>'
        f"<figcaption>{i.name}</figcaption></figure>" for i in ICONS)
    (SYMBOLS / "preview.html").write_text(
        '<!doctype html>\n<html lang="en"><meta charset="utf-8"><title>Porto Faifo Symbols</title>\n'
        "<style>:root{color-scheme:light dark}body{font:12px system-ui;margin:24px;display:grid;gap:8px;"
        "grid-template-columns:repeat(auto-fill,minmax(112px,1fr))}figure{margin:0;padding:12px 4px;text-align:center}"
        "svg{fill:currentColor}figcaption{margin-top:8px;overflow-wrap:anywhere}</style>\n" + cells + "\n</html>\n",
        encoding="utf-8")

    count = sum(1 + i.fill for i in ICONS)
    print(f"{len(ICONS)} symbols ({count} with fill variants) x {len(sizes)} sizes x {len(weights)} weights")
    if problems:
        print(f"{len(problems)} problem(s):\n  " + "\n  ".join(problems))
        return 1
    print("checks: all symbols non-empty, on canvas, inside the padding, ink steady across weights")
    return 0


if __name__ == "__main__":
    sys.exit(main())
