"""Draw the README images from the built fonts and symbols.

    .venv/bin/python scripts/specimen.py     (after the three builds)

Writes docs/fonts.svg and docs/symbols.svg.  All text is outlined, so the
images look the same on every machine.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uharfbuzz as hb  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

from pfsans.system import ROOT  # noqa: E402
from pfsymbols.kit import pen  # noqa: E402
from pfsymbols.registry import ICONS  # noqa: E402
from pfsymbols import svg as out  # noqa: E402

INK, MUTED, PAPER = "#16181d", "#6b7080", "#ffffff"
WIDTH = 1200


class Face:
    def __init__(self, path: str):
        data = (ROOT / path).read_bytes()
        self.font = TTFont(ROOT / path)
        self.hb = hb.Font(hb.Face(data))
        self.upm = self.font["head"].unitsPerEm
        self.glyphs = self.font.getGlyphSet()

    def text(self, s: str, x: float, y: float, size: float, fill: str = INK) -> str:
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf)
        k, cx, parts = size / self.upm, 0, []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            p = SVGPathPen(self.glyphs)
            self.glyphs[self.font.getGlyphName(info.codepoint)].draw(p)
            if p.getCommands():
                parts.append(f'<path transform="translate({cx + pos.x_offset} {pos.y_offset})" d="{p.getCommands()}"/>')
            cx += pos.x_advance
        assert cx * k + x <= WIDTH, f"too wide: {s!r}"
        return f'<g fill="{fill}" transform="translate({x} {y}) scale({k:.6f} {-k:.6f})">{"".join(parts)}</g>'


def page(name: str, height: int, body: list[str]) -> None:
    path = ROOT / "docs" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">'
        f'<rect width="{WIDTH}" height="{height}" rx="16" fill="{PAPER}"/>' + "".join(body) + "</svg>\n",
        encoding="utf-8")
    print(path.relative_to(ROOT), f"{path.stat().st_size:,} bytes")


def fonts() -> None:
    sans = {w: Face(f"fonts/otf/PFSans-{w}.otf") for w in ("Light", "Regular", "Medium", "Bold", "Black")}
    mono = Face("fonts/mono/otf/PFMono-Regular.otf")
    body = [sans["Bold"].text("Porto Faifo", 48, 150, 112),
            sans["Regular"].text("A typeface family for interfaces, with full Vietnamese support. 1,250,000 ₫", 48, 214, 32, MUTED)]
    y = 300
    for weight, face in sans.items():
        body += [sans["Regular"].text(weight, 48, y, 20, MUTED),
                 face.text("Clear at every size 0123456789 ĂẤỀỖỢỮ đ", 200, y, 40)]
        y += 66
    body += [sans["Regular"].text("Mono", 48, y + 20, 20, MUTED),
             mono.text('const total = price * 1.08; // 8% tax "₫"', 200, y + 20, 30)]
    page("fonts.svg", y + 76, body)


def symbols() -> None:
    sym_pen = pen("Regular", 24)
    columns, cell, margin = 18, 62, 42
    body = []
    for n, icon in enumerate(ICONS[:144]):
        x, y = margin + n % columns * cell + 12, margin + n // columns * cell + 12
        d = out.path_data(icon.draw(sym_pen, fill=False), 24, 24, False)
        ghost = out.path_data(icon.ghost(sym_pen), 24, 24, False) if icon.ghost else ""
        body.append(f'<g transform="translate({x} {y}) scale(1.4)" fill="{INK}"><path d="{d}"/>'
                    + (f'<path opacity="{out.GHOST}" d="{ghost}"/>' if ghost else "") + "</g>")
    page("symbols.svg", margin * 2 + 8 * cell, body)


if __name__ == "__main__":
    fonts()
    symbols()
