"""Porto Faifo Symbols recipes: calendar.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

import math

from .icons import HI, LO, Icon
from .icons_system import _head
from .kit import minus, turned, union

V9 = "0.9.0"
CAL = "Calendar"


# ------------------------------------------------------------------ repeat
def repeat(p, fill=False):
    """Two arrows round an open loop, each turning a corner and running back
    over the other: again and again.  Not ``refresh`` (one round arc),
    ``restart`` (the power ring) or ``rotate-left`` (a picture and a quarter
    turn)."""
    y, s, tip = 17.0, 3.0, HI - 1.4  # the sharp tip grows by h·√2 at Bold
    top = union(p.line([(LO, 12.0), (LO, y), (tip - 0.4, y)], cut=("h", "p"), corners={1: 3.6}),
                _head(p, (tip, y), (1.0, 0.0), s=s))
    return union(top, turned(top, 180))


# ----------------------------------------------------------------- map pin
_PIN_C, _PIN_R, _PIN_TIP = (12.0, 14.2), 6.9, (12.0, 2.9)


def _drop():
    """The pin's centre-line outline: a circle and the kite from its centre
    to the tip, the two sides tangent to the circle."""
    (cx, cy), r, (tx, ty) = _PIN_C, _PIN_R, _PIN_TIP
    a = math.acos(r / (cy - ty))  # from straight down to a tangent point
    side = (r * math.sin(a), -r * math.cos(a))
    return [(tx, ty), (cx + side[0], cy + side[1]), (cx, cy), (cx - side[0], cy + side[1])]


def _drop_solid(p):
    kite = p.solid(_drop(), corners={0: 0.8, 1: p.radius_small, 2: 0, 3: p.radius_small})
    return union(p.disc(*_PIN_C, _PIN_R), kite)


def map_pin(p, fill=False):
    """A teardrop standing on its point with a hole in its head: a place on a
    map.  Not ``pin`` (a thumbtack that holds something in place)."""
    outer = _drop_solid(p)
    hole = (_PIN_C[0], _PIN_C[1], 2.4)
    if fill:
        return minus(outer, p.disc(*hole))
    inner_kite = minus(p.solid(_drop(), corners={0: 0.8}), p.frame(_drop(), corners={0: 0.8}))
    inner = union(minus(p.disc(*_PIN_C, _PIN_R), p.ring(*_PIN_C, _PIN_R)), inner_kite)
    return union(minus(outer, inner), p.ring(*hole))


CALENDAR_ICONS = [
    Icon("repeat", repeat, CAL, "repeat", "appointment-recurring", "kde", meaning="Repeat (recurring event)", since=V9,
         fdo_more=["media-playlist-repeat"],
         note="Two arrows chasing each other round an open ring; unlike refresh (one arc), restart (power ring) and rotate-left."),
    Icon("map-pin", map_pin, CAL, "map-pin", "mark-location", "kde", fill=True, meaning="Place", since=V9,
         note="A drop standing on its tip, with a hole at the head; unlike pin (a pushpin)."),
]
