"""Load the Porto Faifo Sans design system (``design-system.json``) for one master
or one interpolated instance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PATH = ROOT / "design-system.json"


class Namespace(dict):
    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError as exc:  # pragma: no cover - programming error
            raise AttributeError(key) from exc
        return Namespace(value) if isinstance(value, dict) else value


@dataclass
class System:
    raw: dict
    master: str

    @property
    def meta(self):
        return Namespace(self.raw["meta"])

    @property
    def font_stem(self) -> str:
        return self.meta.familyName.replace(" ", "")

    @property
    def variable_stem(self) -> str:
        return f"{self.font_stem}[opsz,wght]"

    @property
    def m(self):
        return Namespace(self.raw["metrics"])

    def _layer(self, key):
        """Family-wide values with this master's overrides on top."""
        values = dict(self.raw[key])
        values.update(self.raw["masters"][self.master].get(key, {}))
        return Namespace(values)

    @property
    def masters(self) -> list[str]:
        return list(self.raw["masters"])

    @property
    def k(self):
        return self._layer("curves")

    @property
    def st(self):
        return Namespace(self.raw["masters"][self.master]["stroke"])

    @property
    def wght(self) -> int:
        return self.raw["masters"][self.master]["wght"]

    @property
    def sh(self):
        return self._layer("shapes")

    @property
    def w(self):
        return self._layer("proportions")

    @property
    def sp(self):
        return self._layer("spacing")


LAYERS = ("curves", "shapes", "proportions", "spacing")


def _interpolate(a: dict, b: dict, t: float) -> dict:
    """``a + t (b - a)`` for every number in both tables; whole numbers stay whole."""
    out = {}
    for key, va in a.items():
        vb = b.get(key, va)
        if isinstance(va, bool) or not all(isinstance(v, (int, float)) for v in (va, vb)):
            continue
        v = va + t * (vb - va)
        out[key] = round(v) if isinstance(va, int) and isinstance(vb, int) else round(v, 4)
    return out


def expand_instances(raw: dict) -> dict:
    """Add every ``instances`` entry to ``masters`` (ordered by wght),
    using the nearest available endpoints, including earlier instances."""
    instances = ((name, spec["wght"]) for name, spec in raw.get("instances", {}).items() if name != "comment")
    for name, weight in sorted(instances, key=lambda item: item[1]):
        raw["masters"][name] = _pen_at(raw, weight)
    raw["masters"] = dict(sorted(raw["masters"].items(), key=lambda kv: kv[1]["wght"]))
    return raw


def load(master: str = "Regular", path: Path = SYSTEM_PATH, mono: bool = False) -> System:
    raw = expand_instances(json.loads(path.read_text(encoding="utf-8")))
    if mono:
        apply_mono(raw, master)
    return System(raw, master)


def _pen_at(raw: dict, w) -> dict:
    """A master's table by name, or the strokes and shapes at weight ``w``
    interpolated between the masters around it, as ``instances`` are."""
    if isinstance(w, str):
        return raw["masters"][w]
    ms = [m for m in raw["masters"].values() if isinstance(m.get("wght"), (int, float))]
    lo = max((m for m in ms if m["wght"] <= w), key=lambda m: m["wght"])
    hi = min((m for m in ms if m["wght"] >= w), key=lambda m: m["wght"])
    if lo is hi:
        return lo
    t = (w - lo["wght"]) / (hi["wght"] - lo["wght"])
    out = {"wght": w, "stroke": _interpolate(lo["stroke"], hi["stroke"], t)}
    for key in LAYERS:
        out[key] = _interpolate({**raw[key], **lo.get(key, {})}, {**raw[key], **hi.get(key, {})}, t)
    return out


def apply_mono(raw: dict, master: str) -> None:
    """Porto Faifo Mono: the ``mono`` widths over the pen ``mono.pens`` gives
    ``master`` (a heavier weight: a mono line holds more white than a
    proportional one), under ``master``'s name and weight class and the Mono
    family names.  Symbol recipes keep scaling against the proportional
    Regular strokes (``referenceStroke``)."""
    mono = raw["mono"]
    raw["referenceStroke"] = dict(raw["masters"]["Regular"]["stroke"])
    w = mono.get("pens", {}).get(master, raw["masters"][master]["wght"])
    pen = _pen_at(raw, w)
    entry = {**pen, "wght": raw["masters"][master]["wght"], "comment": f"Mono {master} on the wght {w} pen."}
    entry["proportions"] = {**raw["proportions"], **pen.get("proportions", {}), **mono["proportions"]}
    entry["stroke"] = {k: round(v * mono.get("strokeFactor", {}).get(k, 1)) for k, v in pen["stroke"].items()}
    raw["masters"][master] = entry
    for key in ("familyName", "sourceFamily", "brandName", "version"):
        raw["meta"][key] = mono[key]
