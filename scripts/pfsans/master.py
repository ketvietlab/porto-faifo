"""Assemble one Porto Faifo Sans master: glyphs, Vietnamese marks, kerning, features."""

from __future__ import annotations

from pathlib import Path
import math
from copy import deepcopy

from fontTools.pens.boundsPen import BoundsPen

from .geometry import superellipse

from . import glyphs as G
from . import kerning as K
from . import latin as L
from . import marks as M
from . import symbols as S
from .system import load
from .ufo import write_master


def add_proportional_figures(glyphs, builder):
    """Keep the existing tabular drawings and space the default figures by ink."""
    bearing = max(64, (builder.wd.tabularAdvance - builder.wd.figure) / 2)
    for name in (*S.FIGURES, "zero.zero"):
        glyph = glyphs[name]
        tabular = deepcopy(glyph)
        tabular.name += ".tnum"
        tabular.unicodes = []
        glyphs[tabular.name] = tabular
        if name == "zero.zero":
            glyph.width = glyphs["zero"].width
            glyph.shifted(zero_shift)
            continue
        pen = BoundsPen(None)
        for contour in glyph.contours:
            contour.draw(pen)
        left, _, right, _ = pen.bounds
        glyph.width = right - left + 2 * bearing
        shift = bearing - left
        glyph.shifted(shift)
        if name == "zero":
            zero_shift = shift


def add_support_glyphs(glyphs, builder):
    width, height = builder.wd.tabularAdvance, builder.xh
    radius, dot_radius = 0.32 * height, 42 + 0.14 * builder.st.markStroke
    dots = []
    for index in range(10):
        angle = math.tau * index / 10
        x, y = width / 2 + radius * math.cos(angle), height / 2 + radius * math.sin(angle)
        dots.append(superellipse(x, y, dot_radius, dot_radius, builder.ten.circle))
    anchors = {
        "top": (width / 2, height),
        "bottom": (width / 2, 0),
        "horn": (width / 2 + radius, height / 2 + radius / 3),
        "ogonek": (width / 2 + radius * 0.7, height / 2 - radius * 0.8),
    }
    glyphs["uni25CC"] = G.Glyph("uni25CC", [0x25CC], width, dots, anchors=anchors)
    for codepoint in (0x2028, 0x2029):
        name = f"uni{codepoint:04X}"
        glyphs[name] = G.Glyph(name, [codepoint], 0)


def assemble(master: str = "Regular", optical: str | None = None, mono: bool = False):
    system = load(master, mono=mono)
    if mono:
        from .mono import MonoMixin, monospace

        builder = type("MonoLatin", (MonoMixin, L.Latin), {})(system)
    else:
        builder = L.Latin(system)
    glyphs = G.build_core(builder)
    glyphs.update(L.build_latin(builder))
    glyphs.update(S.build_symbols(builder))
    add_support_glyphs(glyphs, builder)
    if mono:
        # Bases go on the cell first, so the Vietnamese letters are built on
        # the mono bases; then whatever the marks step adds.
        condensed = monospace(glyphs, system)
        glyphs.update(M.build_marks_and_letters(builder, glyphs))
        condensed += monospace(glyphs, system)
        system.raw["mono"]["condensed"] = condensed
        return system, glyphs, {}, {}
    glyphs.update(M.build_marks_and_letters(builder, glyphs))
    add_proportional_figures(glyphs, builder)
    if optical == "Display":
        from .optical import display_spacing

        text_glyphs = deepcopy(glyphs)
        _, text_kerning = K.build(text_glyphs)
        display_spacing(glyphs, system)
    if optical:
        system.raw["meta"]["familyName"] += " Optical"
        system.raw["meta"]["postscriptFamily"] += "Optical"
    groups, kerning = K.build(glyphs)
    if optical == "Display":
        kerning.update(K.optical_exceptions(
            text_glyphs, glyphs, groups, text_kerning, kerning,
            system.raw["opticalSizing"]["display"]["minimumPairGap"],
        ))
    return system, glyphs, groups, kerning


def write(path: Path, master: str = "Regular", optical: str | None = None, mono: bool = False):
    system, glyphs, groups, kerning = assemble(master, optical, mono)
    font = write_master(glyphs, system, master, path, features=M.features(glyphs) + S.features(glyphs), groups=groups, kerning=kerning)
    return font, glyphs
