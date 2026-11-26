"""Porto Faifo Symbols recipes: notes and text editing.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import Icon
from .kit import union

V9 = "0.9.0"
TEXT = "Text"


def checklist(p, fill=False):
    """Two items: one ticked, one still an empty box, each with its line.
    The tick without a box keeps the done item readable at 16 px, where a
    tick inside a box closes up."""
    s = p.radius_small
    tick = p.line([(3.4, 16.8), (5.6, 14.6), (9.6, 18.8)])
    box = (p.rect_solid if fill else p.rect)(3.6, 4.6, 9.4, 10.4, r=s)
    lines = union(p.bar((13.0, 16.4), (20.6, 16.4)), p.bar((13.0, 7.5), (20.6, 7.5)))
    return union(tick, box, lines)


NOTES_ICONS = [
    Icon("checklist", checklist, TEXT, "list-todo", fill=True, meaning="Checklist", since=V9,
         note="One ticked item, one empty box; unlike check-all (select all) and clipboard-list."),
]
