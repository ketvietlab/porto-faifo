"""Porto Faifo Symbols recipes: shell and tray, settings, system flows and files.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

import math

from pfsans.geometry import Contour, superellipse

from .icons import (
    HI,
    LO,
    R,
    Icon,
    _at,
    _front_knock,
    _u,
    bell,
    copy,
    folder,
    search,
    wifi,
)
from .kit import BIG, Pen, box, clip, contours, minus, mirrored, region, turned, union
from .svg import GHOST as GHOST_OPACITY


# ----------------------------------------------------------------- devices
def _gap(p: Pen) -> float:
    """Clear space between a glyph and what it cuts: about half a stroke."""
    return max(1.0, 0.45 * p.w)


# Skia path ops can misread a near-tangent crossing, as the flat top of the
# knock against the crown of the eye at Bold 14 px, and return a cut that
# drops half the base.  The union then breaks inclusion-exclusion, so a cut
# that fails it is redone with the knock moved a thousandth of a unit.
_NUDGES = (0.0, 0.001, -0.001, 0.002, -0.002)


def _sound(base, knock, cut) -> bool:
    a, k, both = abs(base.area), abs(knock.area), abs(clip(base, knock).area)
    return (abs(abs(union(base, knock).area) - (a + k - both)) < 0.05
            and abs(abs(cut.area) - (a - both)) < 0.05)


def _slash(p: Pen, base):
    a, b = (4.2, 19.8), (19.8, 4.2)
    for dy in _NUDGES:
        knock = p.stroked(p.w + 2 * _gap(p)).bar((a[0], a[1] + dy), (b[0], b[1] + dy))
        cut = minus(base, knock)
        if _sound(base, knock, cut):
            break
    else:
        raise ValueError("slash: no nudge gives a sound cut")
    return union(cut, p.bar(a, b))


def _badged(p: Pen, base, glyph):
    """``glyph(pen)`` draws the corner sign; the base is cut back by the
    same sign drawn a gap heavier."""
    return union(minus(base, glyph(p.stroked(p.w + 2 * _gap(p)))), glyph(p))


def _head(p: Pen, tip, d, s=3.2):
    """A chevron arrowhead with its point at ``tip``, facing ``d``."""
    n = (-d[1], d[0])
    back = _at(tip, d, -s)
    return p.line([_at(back, n, s), tip, _at(back, n, -s)])


def _arrow_down(c=(17.4, 7.0), s=2.6, length=6.4):
    def draw(p):
        x, y = c
        tip = y - length / 2
        return union(p.bar((x, y + length / 2), (x, tip), cut=("h", "p")), p.line([(x - s, tip + s), (x, tip), (x + s, tip + s)]))
    return draw


def _arrow_up(c=(17.4, 7.0), s=2.6, length=6.4):
    def draw(p):
        x, y = c
        tip = y + length / 2
        return union(p.bar((x, y - length / 2), (x, tip), cut=("h", "p")), p.line([(x - s, tip - s), (x, tip), (x + s, tip - s)]))
    return draw


def _sign_minus(c=(17.4, 7.0), half=3.0):
    return lambda p: p.bar((c[0] - half, c[1]), (c[0] + half, c[1]))


def _sign_plus(c=(17.4, 7.0), half=3.0):
    return lambda p: union(p.bar((c[0] - half, c[1]), (c[0] + half, c[1])), p.bar((c[0], c[1] - half), (c[0], c[1] + half)))


def _crescent(p: Pen, c, r, oc, orr):
    """A moon: the rim of one circle outside a second, and the rim of the
    second inside the first."""
    big = p.arc(*c, r, keep=minus(box(), region(superellipse(*oc, orr, orr, p.k.circle))))
    bite = p.arc(*oc, orr, keep=region(superellipse(*c, r, r, p.k.circle)))
    return union(big, bite)


def _exclaim(p: Pen, x, y0, y1):
    """An exclamation mark filling y0..y1: Porto Faifo dot and dot gap."""
    d = p.dot_d
    gap = max(0.8, p.dot_gap * (y1 - y0))
    stem0 = y0 + d + gap
    return union(p.bar((x, stem0), (x, y1), cut="h"), p.dot(x, y0 + d / 2))


# ---------------------------------------------------------- session, power
def restart(p, fill=False):
    """The power ring without its bar: the end turns into an arrowhead."""
    c, r = (12, 11.0), 8.0
    keep = minus(box(), box(8.2, c[1], 15.8, BIG))
    end = (15.8, c[1] + math.sqrt(r * r - 3.8 ** 2))
    th = math.atan2(end[1] - c[1], end[0] - c[0])
    return union(p.arc(*c, r, keep=keep), _head(p, end, (-math.sin(th), math.cos(th))))


def sleep(p, fill=False):
    z = p.line([(15.2, 20.4), (20.6, 20.4), (15.2, 15.0), (20.6, 15.0)])
    return union(_crescent(p, (10.4, 10.4), 7.6, (15.0, 14.6), 6.0), z)


def log_out(p, fill=False):
    door = p.line([(10.6, 20.2), (3.9, 20.2), (3.9, 3.8), (10.6, 3.8)], corners={1: p.radius, 2: p.radius})
    arrow = union(p.bar((8.8, 12), (20.0, 12), cut=("v", "p")), p.line([(15.4, 16.6), (20.0, 12), (15.4, 7.4)]))
    return union(door, arrow)


def switch_user(p, fill=False):
    person = union(p.ring(8.6, 15.4, 3.6), p.arc(8.6, 2.6, 5.4, 4.8, keep=box(y0=2.6)))
    right = union(p.bar((15.6, 14.8), (20.4, 14.8), cut=("v", "p")), p.line([(18.0, 17.2), (20.4, 14.8), (18.0, 12.4)]))
    left = union(p.bar((20.4, 7.8), (15.6, 7.8), cut=("v", "p")), p.line([(18.0, 10.2), (15.6, 7.8), (18.0, 5.4)]))
    return union(person, right, left)


def unlock(p, fill=False):
    """The shackle lifts off the left: only its right leg stays in the body."""
    body = (4.6, LO, 19.4, 11.0)
    shackle = union(p.arc(12, 16.2, 4.2, 4.4, keep=box(y0=16.2)), p.bar((16.2, 11.0), (16.2, 16.2), cut="p"), p.bar((7.8, 14.4), (7.8, 16.2), cut=("h", "p")))
    key = p.bar((12, 5.2), (12, 8.2), cut="h")
    if fill:
        return union(minus(p.rect_solid(*body), key), shackle)
    return union(p.rect(*body), shackle, key)


# ----------------------------------------------------------- notifications
def bell_off(p, fill=False):
    return _slash(p, bell(p, fill))


def check_all(p, fill=False):
    first = [(3.6, 12.4), (7.6, 8.4), (15.0, 15.8)]
    second = p.line([(10.1, 10.9), (12.6, 8.4), (20.0, 15.8)])
    return union(p.line(first), minus(second, p.stroked(p.w + 2 * _gap(p)).line(first)))


# -------------------------------------------------------------- networking
def _wifi_parts(p):
    c = (12, 6.2)
    arcs = [p.arc(*c, r, keep=box(y0=c[1] + r * math.sin(math.radians(45)))) for r in (3.9, 7.7, 11.5)]
    return p.root_dot(*c), arcs


def _wifi_level(n):
    def draw(p, fill=False):
        dot, arcs = _wifi_parts(p)
        return union(dot, *arcs[:n])

    def ghost(p):
        _, arcs = _wifi_parts(p)
        return union(*arcs[n:])

    return draw, ghost


wifi_none, wifi_none_ghost = _wifi_level(0)
wifi_low, wifi_low_ghost = _wifi_level(1)
wifi_medium, wifi_medium_ghost = _wifi_level(2)


def wifi_off(p, fill=False):
    return _slash(p, wifi(p))


def ethernet(p, fill=False):
    pts = [(4.4, 18.8), (19.6, 18.8), (19.6, 6.8), (15.6, 6.8), (15.6, 3.4), (8.4, 3.4), (8.4, 6.8), (4.4, 6.8)]
    rs = p.radius_small
    corners = {0: rs, 1: rs, 2: rs, 3: 0, 4: rs, 5: rs, 6: 0, 7: rs}
    pins = union(*(p.bar((x, 18.8), (x, 14.6), cut=("p", "h")) for x in (8.4, 12.0, 15.6)))
    return union(p.frame(pts, corners=corners), pins)


def network(p, fill=False):
    s = 5.4
    nodes = [(12 - s / 2, 15.6, 12 + s / 2, 21.0), (3.3, 2.9, 3.3 + s, 2.9 + s), (20.7 - s, 2.9, 20.7, 2.9 + s)]
    draw = p.rect_solid if fill else p.rect
    links = union(p.bar((12, 15.6), (12, 12.0), cut="p"), p.line([(6.0, 2.9 + s), (6.0, 12.0), (18.0, 12.0), (18.0, 2.9 + s)], cut="p", corners={1: p.radius_small, 2: p.radius_small}))
    return union(links, *(draw(*n, r=p.radius_small) for n in nodes))


def network_offline(p, fill=False):
    return _slash(p, network(p))


def ethernet_off(p, fill=False):
    return _slash(p, ethernet(p))


def hotspot(p, fill=False):
    """A mast that sends: two rings open at the foot round a dot on a stem,
    so it never reads as the Wi-Fi fan, which only opens upward."""
    c = (12, 11.6)
    arcs = [p.arc(*c, r, keep=box(y0=c[1] - r * math.sin(math.radians(35)))) for r in (4.4, 8.6)]
    stem = p.bar((12, c[1]), (12, LO), cut=("p", "h"))
    return union(p.root_dot(*c), stem, *arcs)


# Corner signs for the network states: desktops ask for one name per
# state (``-limited``, ``-locked``), so the sign ships precomposed on every
# level, as the charging bolt does on the battery.
def _sign_limited(p):
    # Right of the inner arc's tip and under the outer one: tall enough to
    # read as "!" at 16 px, its knock only trims the middle arc's end.
    return _exclaim(p, 19.6, LO, 11.2)


def _sign_locked(p):
    # Kept right of the Wi-Fi dot so the knock never bites it.
    x, half, top, r = 18.5, 2.6, 8.0, 1.9
    body = p.rect_solid(x - half, LO, x + half, 6.6, r=p.radius_small)
    legs = [p.bar((x + s * r, 6.6), (x + s * r, top), cut="p") for s in (-1, 1)]
    return union(body, p.arc(x, top, r, keep=box(y0=top)), *legs)


def _signed(base, base_ghost, sign):
    def draw(p, fill=False):
        return _badged(p, base(p), sign)

    def ghost(p):
        return minus(base_ghost(p), sign(p.stroked(p.w + 2 * _gap(p))))

    return draw, ghost if base_ghost else None


def _rune(p):
    return p.line([(7.0, 16.4), (16.8, 7.6), (12.0, 3.2), (12.0, 20.8), (16.8, 16.4), (7.0, 7.6)])


def bluetooth(p, fill=False):
    return _rune(p)


def bluetooth_off(p, fill=False):
    return _slash(p, _rune(p))


def bluetooth_connected(p, fill=False):
    return union(_rune(p), p.dot(3.6, 12), p.dot(20.4, 12))


def globe(p, fill=False):
    return union(p.ring(12, 12, R), p.ring(12, 12, 4.0, R), p.bar((LO, 12), (HI, 12), cut="p"))


# ------------------------------------------------------------------- audio
_CONE = [(3.4, 9.0), (7.6, 9.0), (12.4, 4.6), (12.4, 19.4), (7.6, 15.0), (3.4, 15.0)]
_CONE_CORNERS = {0: 1.0, 1: 0, 2: 1.0, 3: 1.0, 4: 0, 5: 1.0}


def _cone(p, fill=False):
    return (p.solid if fill else p.frame)(_CONE, corners=_CONE_CORNERS)


def _waves(p):
    cx = 12.4
    return [p.arc(cx, 12, r, keep=clip(box(x0=cx), box(y0=12 - r * 0.72, y1=12 + r * 0.72))) for r in (4.4, 8.2)]


def volume_low(p, fill=False):
    return union(_cone(p, fill), _waves(p)[0])


def volume_low_ghost(p):
    return _waves(p)[1]


def volume_mute(p, fill=False):
    c, s = (18.3, 12.0), 2.3
    x = union(p.bar((c[0] - s, c[1] - s), (c[0] + s, c[1] + s)), p.bar((c[0] - s, c[1] + s), (c[0] + s, c[1] - s)))
    return union(_cone(p, fill), x)


def speaker(p, fill=False):
    body = (4.9, LO, 19.1, HI)
    cone = p.ring(12, 9.2, 3.2)
    if fill:
        return minus(p.rect_solid(*body), cone, p.stroked(1.6 * p.w).dot(12, 16.8))
    return union(p.rect(*body), cone, p.dot(12, 16.8))


def headphones(p, fill=False):
    x0, x1, top = 3.6, 20.4, 11.8
    band = p.arc(12, top, (x1 - x0) / 2, keep=box(y0=top))
    draw = p.rect_solid if fill else p.rect
    return union(band, draw(x0, 3.0, 8.6, top, r=p.radius_small), draw(15.4, 3.0, x1, top, r=p.radius_small))


def microphone(p, fill=False):
    capsule = (8.8, 10.8, 15.2, HI)
    stand = p.arc(12, 13.2, 6.8, keep=box(y1=13.2))
    stem = p.bar((12, 13.2 - 6.8), (12, LO), cut=("p", "h"))
    base = p.bar((8.2, LO), (15.8, LO))
    head = (p.rect_solid if fill else p.rect)(*capsule, r=3.2)
    return union(head, stand, stem, base)


def microphone_mute(p, fill=False):
    return _slash(p, microphone(p, fill))


# ----------------------------------------------------------------- battery
_BAT = (LO, 6.6, 19.4, 17.4)
_BOLT = [(12.4, 15.6), (8.4, 11.3), (11.0, 11.3), (9.9, 8.4), (13.9, 12.7), (11.3, 12.7)]


def _battery_shell(p):
    x0, y0, x1, y1 = _BAT
    return union(p.rect(x0, y0, x1, y1), box(x1 + p.h - 0.2, 10.2, 21.8, 13.8))


def _battery_inside(p):
    x0, y0, x1, y1 = _BAT
    g = p.h + 1.1
    return x0 + g, y0 + g, x1 - g, y1 - g


def _bolt():
    c = Contour(_BOLT[0])
    for pt in _BOLT[1:]:
        c.line(pt)
    return c.close().oriented(True)


def _battery(level: float, charging: bool = False):
    """``level`` 0..1 of the inside; the outline and the nub never move."""
    def draw(p, fill=False):
        ix0, iy0, ix1, iy1 = _battery_inside(p)
        out = [_battery_shell(p)]
        if level > 0:
            charge = box(ix0, iy0, ix0 + (ix1 - ix0) * level, iy1)
            if charging:
                charge = minus(charge, region(_bolt().offset(_gap(p) * 0.8)))
            out.append(charge)
        if charging:
            out.append(region(_bolt()))
        return union(*out)
    return draw


battery_empty = _battery(0.0)
battery_low = _battery(0.22)
battery_full = _battery(1.0)
battery_charging = _battery(0.0, True)
battery_charging_low = _battery(0.22, True)
battery_charging_medium = _battery(0.5, True)
battery_charging_full = _battery(1.0, True)


def battery_warning(p, fill=False):
    x0, y0, x1, y1 = _BAT
    return union(_battery_shell(p), _exclaim(p, (x0 + x1) / 2, y0 + p.h + 0.7, y1 - p.h - 0.7))


# ----------------------------------------------------------------- display
def sun(p, fill=False):
    c = (12, 12)
    rays = [p.bar(_at(c, _u(a), 6.4), _at(c, _u(a), 9.6)) for a in range(0, 360, 45)]
    return union((p.disc if fill else p.ring)(12, 12, 3.6), *rays)


def brightness(p, fill=False):
    """Screen brightness: a half-lit core and dots for rays, so it never
    reads as the light theme (sun)."""
    c = (12, 12)
    half = clip(p.disc(12, 12, 3.6), box(x1=12))
    rays = [p.dot(*_at(c, _u(a), 8.2)) for a in range(0, 360, 45)]
    return union(p.ring(12, 12, 3.6), half, *rays)


def moon(p, fill=False):
    return _crescent(p, (11.6, 11.4), 8.0, (16.6, 15.8), 6.6)


def display(p, fill=False):
    """A monitor on a stand: the screen, never the computer."""
    stand = union(p.bar((12, 7.6), (12, 3.4), cut="p"), p.bar((7.4, 3.4), (16.6, 3.4)))
    return union((p.rect_solid if fill else p.rect)(LO, 7.6, HI, 20.4), stand)


# ------------------------------------------------------------------- input
def keyboard(p, fill=False):
    body = (LO, 5.4, HI, 18.6)
    keys = union(*(p.dot(x, 14.2) for x in (7.2, 12.0, 16.8)), p.bar((8.4, 9.0), (15.6, 9.0)))
    if fill:
        return minus(p.rect_solid(*body), keys)
    return union(p.rect(*body), keys)


def _letter_a(p, x0, x1, y0, y1, bar):
    legs = p.line([(x0, y0), ((x0 + x1) / 2, y1), (x1, y0)], cut="h")
    t = (bar - y0) / (y1 - y0)
    xa, xb = x0 + (x1 - x0) / 2 * t, x1 - (x1 - x0) / 2 * t
    return union(legs, p.bar((xa, bar), (xb, bar), cut="p"))


def language(p, fill=False):
    """Two scripts side by side: a 文-like sign (a cap with a tick over a
    cross) and a Porto Faifo A with its flat apex."""
    cap = union(p.bar((LO, 18.0), (12.0, 18.0)), p.bar((7.4, 18.0), (7.4, 21.0), cut=("p", "h")))
    cross = union(p.bar((3.8, 15.0), (10.8, 8.4)), p.bar((3.8, 8.4), (10.8, 15.0)))
    return union(cap, cross, _letter_a(p, 13.0, 21.0, 2.9, 13.4, 6.4))


def input_method(p, fill=False):
    """A key cap with a letter on it: typing in a script, not the keyboard."""
    return union(p.rect(3.5, 3.5, 20.5, 20.5), _letter_a(p, 8.0, 16.0, 7.0, 17.0, 10.4))


# ----------------------------------------------------------- control panel
def sliders(p, fill=False):
    """Three tracks, each with a hollow round knob: one pen for every part,
    the track cut where it passes under the knob.  Solid knobs (0.5.x) were
    twice the stroke and made the icon blotchy; square terminals rule out
    Lucide's upright ticks, which read as T; a wide pill crowded the next
    track.  At r 2.4 the counter stays open at Medium and the knob clears
    the neighbouring track.  Tracks sit at 6, 12 and 18, so at 16, 20 and
    24 px all three land the same way on the pixel grid."""
    r = 2.4
    out = []
    for y, x in ((18.0, 15.2), (12.0, 8.8), (6.0, 13.6)):
        out += [minus(p.bar((3.4, y), (20.6, y)), p.disc(x, y, r)), p.ring(x, y, r)]
    return union(*out)


def users(p, fill=False):
    front_head, front_r = (9.0, 14.6), 3.5
    front = union(p.ring(*front_head, front_r), p.arc(9.0, 2.6, 6.0, 5.0, keep=box(y0=2.6)))
    hide = union(p.disc(*front_head, front_r + _gap(p)), region(superellipse(9.0, 2.6, 6.0 + p.h + _gap(p), 5.0 + p.h + _gap(p), p.k.outer)))
    back = union(p.ring(17.4, 16.8, 2.6), p.arc(17.0, 2.6, 4.2, 4.4, keep=box(y0=2.6)))
    return union(front, minus(back, hide))


_SHIELD = [(12, 20.8), (19.2, 18.0), (19.2, 11.6), (12, 2.8), (4.8, 11.6), (4.8, 18.0)]
_SHIELD_CORNERS = {0: 2.0, 1: 1.2, 2: 5.0, 3: 1.0, 4: 5.0, 5: 1.2}


def shield(p, fill=False):
    return (p.solid if fill else p.frame)(_SHIELD, corners=_SHIELD_CORNERS)


def shield_check(p, fill=False):
    tick = p.line([(8.4, 12.2), (11.0, 9.6), (15.8, 14.4)])
    if fill:
        return minus(shield(p, True), tick)
    return union(shield(p), tick)


def palette(p, fill=False):
    blob = minus(region(superellipse(12, 12, R, R, p.k.circle)), region(superellipse(17.6, 6.0, 3.6, 3.6, p.k.circle)))
    rim = union(*(p.outline(c) for c in contours(blob)))
    paints = [p.dot(*_at((12, 12), _u(a), 5.2)) for a in (170, 120, 70, 25)]
    return union(rim, *paints)


def wallpaper(p, fill=False):
    hills = p.line([(LO, 10.6), (8.2, 15.6), (12.4, 11.8), (14.6, 13.8), (HI, 9.8)], cut="v")
    return union(display(p), hills)


def text_size(p, fill=False):
    big = union(p.bar((3.4, 19.6), (13.8, 19.6)), p.bar((8.6, 19.6), (8.6, 4.0), cut=("p", "h")))
    small = union(p.bar((14.6, 12.6), (20.8, 12.6)), p.bar((17.7, 12.6), (17.7, 4.0), cut=("p", "h")))
    return union(big, small)


def accessibility(p, fill=False):
    figure = union(
        p.dot(12, 17.2),
        p.bar((6.8, 13.2), (17.2, 13.2)),
        p.bar((12, 13.2), (12, 10.2), cut="p"),
        p.line([(9.2, 6.2), (12, 10.2), (14.8, 6.2)]),
    )
    return union(p.ring(12, 12, R), figure)


def mouse(p, fill=False):
    split = p.bar((12, 21.0), (12, 15.0), cut=("p", "h"))
    if fill:
        return minus(p.rect_solid(6.2, 3.0, 17.8, 21.0, r=5.0), split)
    return union(p.rect(6.2, 3.0, 17.8, 21.0, r=5.0), split)


def touchpad(p, fill=False):
    return union(p.rect(LO, 4.4, HI, 19.6), p.bar((LO, 9.4), (HI, 9.4), cut="p"), p.bar((12, 9.4), (12, 4.4), cut="p"))


def printer(p, fill=False):
    body = (LO, 7.0, HI, 15.8)
    sheet = (6.8, LO, 17.2, 11.4)
    tray = p.line([(6.8, 15.8), (6.8, 20.6), (17.2, 20.6), (17.2, 15.8)], cut="p", corners={1: p.radius_small, 2: p.radius_small})
    front = minus(p.rect(*body), _front_knock(p, *sheet, p.radius_small, gap=1.0))
    return union(front, tray, p.rect(*sheet, r=p.radius_small))


def camera(p, fill=False):
    bump = p.line([(8.0, 16.8), (9.4, 19.8), (14.6, 19.8), (16.0, 16.8)], cut="p", corners={1: p.radius_small, 2: p.radius_small})
    if fill:
        return union(minus(p.rect_solid(LO, 4.4, HI, 16.8), p.ring(12, 10.6, 2.8)), bump)
    return union(p.rect(LO, 4.4, HI, 16.8), bump, p.ring(12, 10.6, 2.8))


def cpu(p, fill=False):
    pins = []
    for t in (10.2, 13.8):
        pins += [
            p.bar((t, 17.8), (t, 21.0), cut=("p", "h")),
            p.bar((t, 6.2), (t, 3.0), cut=("p", "h")),
            p.bar((17.8, t), (21.0, t), cut=("p", "v")),
            p.bar((6.2, t), (3.0, t), cut=("p", "v")),
        ]
    return union(p.rect(6.2, 6.2, 17.8, 17.8), p.rect_solid(10.4, 10.4, 13.6, 13.6, r=0.6), *pins)


def memory(p, fill=False):
    """A RAM module: chips on a board and the contact row with its notch."""
    chips = [p.rect_solid(x - 0.8, 11.4, x + 0.8, 14.0, r=0.4) for x in (7.0, 12.0, 17.0)]
    pins = [p.bar((x, 8.0), (x, 4.6), cut=("p", "h")) for x in (5.4, 9.0, 15.0, 18.6)]
    return union(p.rect(LO, 8.0, HI, 17.4), *chips, *pins)


def storage(p, fill=False):
    rx, ry, top, bottom = 8.2, 2.8, 17.8, 6.2
    sides = union(p.bar((12 - rx, top), (12 - rx, bottom), cut="p"), p.bar((12 + rx, top), (12 + rx, bottom), cut="p"))
    shelves = union(p.arc(12, 12.0, rx, ry, keep=box(y1=12.0)), p.arc(12, bottom, rx, ry, keep=box(y1=bottom)))
    return union(p.ring(12, top, rx, ry), sides, shelves)


def chart_line(p, fill=False):
    axis = p.line([(3.4, 21), (3.4, 3.4), (21, 3.4)])
    return union(axis, p.line([(7.6, 8.4), (11.4, 13.6), (14.6, 10.6), (20.2, 17.2)]))


def key(p, fill=False):
    head, r = (8.0, 15.8), 4.2
    u, down = _u(-45), _u(225)
    a, b = _at(head, u, r), (19.6, 4.2)
    teeth = union(p.bar(_at(b, u, -1.8), _at(_at(b, u, -1.8), down, 2.6)), p.bar(_at(b, u, -5.2), _at(_at(b, u, -5.2), down, 2.0)))
    return union((p.disc if fill else p.ring)(*head, r), p.bar(a, b, cut=("p", "g")), teeth)


def password(p, fill=False):
    return union(p.rect(LO, 6.6, HI, 17.4), *(p.dot(x, 12) for x in (7.4, 12.0, 16.6)))


# ------------------------------------------------------------ applications
_HEX = [(12, 20.8), (19.8, 16.5), (19.8, 7.5), (12, 3.2), (4.2, 7.5), (4.2, 16.5)]


def package(p, fill=False):
    """An isometric box (the archive glyph is a storage box with a lid)."""
    top = p.line([(4.2, 16.5), (12, 12.2), (19.8, 16.5)], cut="p")
    return union(p.frame(_HEX, r=p.radius_small), top, p.bar((12, 12.2), (12, 3.2), cut="p"))


def install(p, fill=False):
    return _badged(p, package(p), _arrow_down())


def uninstall(p, fill=False):
    return _badged(p, package(p), _sign_minus())


def update(p, fill=False):
    """An upward arrow in a ring: a newer version (upload is a tray, a
    reload is the open refresh ring)."""
    arrow = union(p.bar((12, 6.4), (12, 17.0), cut=("h", "p")), p.line([(8.4, 13.4), (12, 17.0), (15.6, 13.4)]))
    if fill:
        return minus(p.disc(12, 12, R), arrow)
    return union(p.ring(12, 12, R), arrow)


def launch(p, fill=False):
    """A rocket, nose to the upper right."""
    c = Contour((12, 21.0))
    c.curve((15.6, 13.2), -38, -90, 0.6)
    c.line((14.6, 7.0)).line((9.4, 7.0)).line((8.4, 13.2))
    c.curve((12, 21.0), 90, 38, 0.6)
    body = p.outline(c.close())
    flame = p.bar((12, 7.0), (12, 3.0), cut=("p", "h"))
    return turned(union(body, p.dot(12, 14.6), flame), -45)


# ------------------------------------------------------------- task flow
def stop(p, fill=False):
    return (p.rect_solid if fill else p.rect)(5.4, 5.4, 18.6, 18.6)


def pause(p, fill=False):
    draw = p.rect_solid if fill else p.rect
    return union(draw(6.0, 4.4, 10.4, 19.6, r=p.radius_small), draw(13.6, 4.4, 18.0, 19.6, r=p.radius_small))


def resume(p, fill=False):
    return (p.solid if fill else p.frame)([(7.6, 19.6), (7.6, 4.4), (19.4, 12.0)], r=1.0)


def skip(p, fill=False):
    tri = (p.solid if fill else p.frame)([(5.0, 18.6), (5.0, 5.4), (14.8, 12.0)], r=1.0)
    return union(tri, p.bar((18.8, 18.6), (18.8, 5.4), cut="h"))


def history(p, fill=False):
    """A clock whose rim turns back on the upper left."""
    c, gap_top = (12, 12), 17.6
    keep = minus(box(), box(-BIG, c[1], c[0], gap_top))
    rim = p.arc(*c, R, keep=keep)
    th = math.asin((gap_top - c[1]) / R)
    end = (c[0] - R * math.cos(th), gap_top)
    a = math.pi - th
    hands = p.line([(12, 16.8), (12, 12), (15.4, 9.6)], cut=("h", "g"))
    return union(rim, _head(p, end, (-math.sin(a), math.cos(a))), hands)


# --------------------------------------------------------------- documents
_SAVE = [(LO, LO), (HI, LO), (HI, 16.6), (16.6, HI), (LO, HI)]


def save(p, fill=False):
    rs = p.radius_small
    shutter = p.line([(7.4, HI), (7.4, 15.8), (14.6, 15.8), (14.6, HI)], cut="p", corners={1: rs, 2: rs})
    label = p.line([(6.6, LO), (6.6, 10.0), (17.4, 10.0), (17.4, LO)], cut="p", corners={1: rs, 2: rs})
    corners = {0: p.radius, 1: p.radius, 2: 1.0, 3: 1.0, 4: p.radius}
    if fill:
        return minus(p.solid(_SAVE, corners=corners), shutter, label)
    return union(p.frame(_SAVE, corners=corners), shutter, label)


def _pencil(p):
    u, n = _u(45), _u(135)
    tip, hw = (12.8, 3.4), 1.6
    b, e = _at(tip, u, 2.6), _at(tip, u, 10.6)
    pts = [tip, _at(b, n, -hw), _at(e, n, -hw), _at(e, n, hw), _at(b, n, hw)]
    return p.solid(pts, corners={0: 0.4, 1: 0, 2: 0.6, 3: 0.6, 4: 0})


def save_as(p, fill=False):
    return _badged(p, save(p, fill), _pencil)


def replace(p, fill=False):
    """The new item takes the old one's place: an arrow from the upper
    square into the lower one."""
    rs = p.radius_small
    old = p.rect(LO, 11.8, 11.0, HI, r=rs)
    new = p.rect(12.8, LO, HI, 9.2, r=rs)
    arrow = union(p.line([(13.4, 16.6), (17.0, 16.6), (17.0, 12.6)], cut=("v", "p"), corners={1: rs}), p.line([(14.6, 15.0), (17.0, 12.6), (19.4, 15.0)]))
    return union(old, new, arrow)


# ------------------------------------------------------------------ backup
def backup(p, fill=False):
    """The storage drum with an arrow going in.  download and upload are
    trays, restore and undo are bare arrows, so none of them share a body."""
    return _badged(p, storage(p), _arrow_down())


def backup_restore(p, fill=False):
    """The storage drum with an arrow coming out."""
    return _badged(p, storage(p), _arrow_up())


# --------------------------------------------------------- system install
def partition(p, fill=False):
    """A disk layout bar in three parts; the first one is in use."""
    x0, y0, x1, y1 = LO, 7.0, HI, 17.0
    cuts = (9.4, 14.6)
    used = clip(p.rect_solid(x0, y0, x1, y1), box(x1=cuts[0]))
    return union(p.rect(x0, y0, x1, y1), used, *(p.bar((x, y0), (x, y1), cut="p") for x in cuts))


def disk_image(p, fill=False):
    return union(p.ring(12, 12, R), p.ring(12, 12, 2.4))


def startup(p, fill=False):
    """A gauge: what starts with the session and how much it weighs."""
    c = (12, 9.4)
    dial = p.arc(*c, R, keep=box(y0=c[1] - 3.6))
    return union(dial, p.bar(c, _at(c, _u(52), 6.2), cut=("p", "g")), p.dot(*c, big=True))


# ---------------------------------------------------------------- messages
def success(p, fill=False):
    tick = p.line([(7.4, 12.2), (10.6, 9.0), (16.8, 15.2)])
    if fill:
        return minus(p.disc(12, 12, R), tick)
    return union(p.ring(12, 12, R), tick)


_OCTAGON = [(12 + 9.4 * math.cos(math.radians(22.5 + 45 * i)), 12 + 9.4 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]


def error(p, fill=False):
    """An octagon, so an error differs from success and info by shape."""
    x = union(p.bar((9.0, 9.0), (15.0, 15.0)), p.bar((9.0, 15.0), (15.0, 9.0)))
    if fill:
        return minus(p.solid(_OCTAGON, r=p.radius_small), x)
    return union(p.frame(_OCTAGON, r=p.radius_small), x)


def help_(p, fill=False):
    hook_c, hr = (12, 14.2), 3.0
    hook = p.arc(*hook_c, hr, keep=union(box(y0=hook_c[1]), box(x0=hook_c[0])))
    mark = union(hook, p.bar((12, hook_c[1] - hr), (12, 9.8), cut=("p", "h")), p.dot(12, 6.8))
    if fill:
        return minus(p.disc(12, 12, R), mark)
    return union(p.ring(12, 12, R), mark)


def more_vertical(p, fill=False):
    return union(*(p.root_dot(12, y) for y in (5.4, 12, 18.6)))


def book_open(p, fill=False):
    pts = [(LO, 19.4), (9.0, 19.4), (12.0, 17.6), (15.0, 19.4), (HI, 19.4), (HI, 5.0), (15.0, 5.0), (12.0, 3.2), (9.0, 5.0), (LO, 5.0)]
    rs = p.radius_small
    corners = {0: rs, 1: 1.0, 2: 0, 3: 1.0, 4: rs, 5: rs, 6: 1.0, 7: 0, 8: 1.0, 9: rs}
    return union(p.frame(pts, corners=corners), p.bar((12.0, 17.6), (12.0, 3.2), cut="p"))


def brush(p, fill=False):
    handle = p.bar((19.6, 19.6), (13.6, 13.6), cut=("g", "p"))
    ferrule = p.stroked(1.5 * p.w).bar((13.8, 13.8), (11.0, 11.0), cut="p")
    bristles = p.solid([(12.2, 8.8), (4.0, 4.0), (8.8, 12.2)], corners={0: p.radius_small, 1: "flat", 2: p.radius_small})
    return union(handle, ferrule, bristles)


def system_install(p, fill=False):
    """Install the system onto a disk: an arrow down into a drive (the
    installer app and its "installing" state)."""
    slab = (LO, LO, HI, 9.8)
    inside = union(p.bar((6.6, 6.35), (11.4, 6.35)), p.dot(16.8, 6.35))
    arrow = union(p.bar((12, 21.0), (12, 13.6), cut=("h", "p")), p.line([(8.6, 17.0), (12, 13.6), (15.4, 17.0)]))
    return union(p.rect(*slab), inside, arrow)


def note(p, fill=False):
    """A note: a square sheet with a folded lower corner and two lines."""
    pts = [(LO, HI), (HI, HI), (HI, 8.6), (14.6, LO), (LO, LO)]
    fold = p.line([(HI, 8.6), (14.6, 8.6), (14.6, LO)], cut="p")
    lines = union(p.bar((7.4, 16.0), (16.6, 16.0)), p.bar((7.4, 11.6), (12.6, 11.6)))
    sheet = (p.solid if fill else p.frame)(pts, corners={0: p.radius, 1: p.radius, 2: 0, 3: 0, 4: p.radius})
    if fill:
        return minus(sheet, fold, lines)
    return union(sheet, fold, lines)


# ---------------------------------------------------------------- files P1
_PIN = [(9.0, 20.6), (15.0, 20.6), (15.0, 14.0), (18.4, 10.2), (5.6, 10.2), (9.0, 14.0)]


def pin(p, fill=False):
    head = (p.solid if fill else p.frame)(_PIN, r=p.radius_small)
    return union(head, p.bar((12, 10.2), (12, 2.9), cut=("p", "h")))


def unpin(p, fill=False):
    return _slash(p, pin(p, fill))


def _eye(p):
    upper = p.arc(12, 9.69, 8.71, keep=box(y0=12))
    lower = p.arc(12, 14.31, 8.71, keep=box(y1=12))
    return union(upper, lower)


# Lids: centres 12 -/+ 2.31, radius 8.71, so their centre line passes 6.4 above
# and below the pupil centre.
_LID_REACH = 9.69 + 8.71 - 12
_PUPIL_CLEAR = 0.2  # least gap between pupil and lid, in design units


def eye(p, fill=False):
    """The pupil keeps its 2.8 radius until a heavy pen at a small size would
    press it against the lids (Bold 14 px), then shrinks to keep a gap."""
    r = min(2.8, _LID_REACH - p.w - _PUPIL_CLEAR)
    return union(_eye(p), (p.disc if fill else p.ring)(12, 12, r))


def eye_off(p, fill=False):
    return _slash(p, eye(p, fill))


def zoom_in(p, fill=False):
    c = (10.2, 13.8)
    return union(search(p), p.bar((c[0] - 2.6, c[1]), (c[0] + 2.6, c[1])), p.bar((c[0], c[1] - 2.6), (c[0], c[1] + 2.6)))


def zoom_out(p, fill=False):
    c = (10.2, 13.8)
    return union(search(p), p.bar((c[0] - 2.6, c[1]), (c[0] + 2.6, c[1])))


def open_with(p, fill=False):
    """Three app tiles and an arrow leaving from the fourth: open in an app."""
    s, rs = 6.6, 1.5
    tiles = [p.rect(x0, y0, x0 + s, y0 + s, r=rs) for x0, y0 in ((3.4, 14.0), (14.0, 14.0), (3.4, 3.4))]
    arrow = union(p.bar((14.4, 4.0), (20.0, 9.6), cut=("h", "p")), p.line([(15.6, 9.6), (20.0, 9.6), (20.0, 5.2)]))
    return union(*tiles, arrow)


def copy_path(p, fill=False):
    return union(copy(p), p.bar((12.8, 6.2), (16.2, 12.8), cut="h"))


def link(p, fill=False):
    r = 3.6

    def half(p):
        return union(p.arc(6.5, 12, r, keep=box(x1=6.5)), p.bar((6.5, 12 + r), (9.8, 12 + r), cut=("p", "v")), p.bar((6.5, 12 - r), (9.8, 12 - r), cut=("p", "v")))

    return union(half(p), mirrored(half(p)), p.bar((8.2, 12), (15.8, 12)))


def move_to(p, fill=False):
    arrow = union(p.bar((7.0, 10.4), (16.4, 10.4), cut=("v", "p")), p.line([(13.4, 13.4), (16.4, 10.4), (13.4, 7.4)]))
    if fill:
        return minus(folder(p, True), arrow)
    return union(folder(p), arrow)


def _archive_box(p):
    """The archive glyph without its slot, so a corner sign does not read
    as a second sign beside the slot."""
    body = [(4.6, 15.2), (4.6, LO), (19.4, LO), (19.4, 15.2)]
    return union(p.rect(LO, 15.2, HI, 20.1, r=1.4), p.line(body, cut="p", corners={1: p.radius, 2: p.radius}))


def archive_create(p, fill=False):
    return _badged(p, _archive_box(p), _sign_plus())


def archive_extract(p, fill=False):
    return _badged(p, _archive_box(p), _arrow_up())


def _plug(p):
    body = p.rect(7.4, 8.4, 16.6, 15.2, r=p.radius_small)
    prongs = union(p.bar((10.0, 15.2), (10.0, 20.4), cut=("p", "h")), p.bar((14.0, 15.2), (14.0, 20.4), cut=("p", "h")))
    return union(body, prongs, p.bar((12, 8.4), (12, 3.0), cut=("p", "h")))


def connect(p, fill=False):
    return _plug(p)


def disconnect(p, fill=False):
    return _slash(p, _plug(p))


# ---------------------------------------------------------------- registry
# Group labels.
SHELL, NOTICE, NET, AUDIO, POWER, SCREEN, INPUT = "Session and power", "Notifications", "Network", "Sound", "Battery", "Display", "Input"
GENERAL, LOOK, DEVICE, PERF, SECURE = "General controls", "Appearance", "Devices", "Configuration and performance", "Account and security"
APPS, TASK, DOCS, BACKUP, OSINSTALL, MESSAGE, NAV, FILES = "Apps", "Running tasks", "Documents", "Backup", "OS installation", "Messages", "Navigation", "Files · extended"

V = "0.2.0"
V4 = "0.4.0"

SYSTEM_ICONS = [
    # session and power
    Icon("restart", restart, SHELL, "rotate-cw", "system-reboot", "spec", meaning="Restart", since=V, note="The power ring with its end turned into an arrowhead."),
    Icon("sleep", sleep, SHELL, "moon", "system-suspend", "kde", meaning="Sleep", since=V, note="A moon with a z, to stay distinct from moon (dark appearance)."),
    Icon("log-out", log_out, SHELL, "log-out", "system-log-out", "spec", meaning="Log out", since=V),
    Icon("switch-user", switch_user, SHELL, "users", "system-switch-user", "kde", meaning="Switch user", since=V),
    Icon("unlock", unlock, SHELL, "lock-open", "changes-allow", "spec", "status", fill=True, meaning="Unlock", since=V),
    # notifications
    Icon("bell-off", bell_off, NOTICE, "bell-off", "notifications-disabled", "gnome", "status", fill=True, meaning="Mute notifications / do not disturb", since=V),
    Icon("check-all", check_all, NOTICE, "check-check", "", "", meaning="Mark all as read", since=V),
    # networking
    Icon("wifi-off", wifi_off, NET, "wifi-off", "network-wireless-disabled", "gnome", "status", meaning="Wi-Fi off", since=V),
    Icon("wifi-none", wifi_none, NET, "wifi-zero", "network-wireless-signal-none", "gnome", "status", ghost=wifi_none_ghost, meaning="Wi-Fi on, no signal (0–5%)", since=V),
    Icon("wifi-low", wifi_low, NET, "wifi-low", "network-wireless-signal-weak", "gnome", "status", ghost=wifi_low_ghost, meaning="Weak signal (6–30%)", since=V),
    Icon("wifi-medium", wifi_medium, NET, "wifi", "network-wireless-signal-ok", "gnome", "status", ghost=wifi_medium_ghost, meaning="Medium signal (31–80%)", since=V, fdo_more=["network-wireless-signal-good"]),
    Icon("ethernet", ethernet, NET, "ethernet-port", "network-wired", "spec", "devices", meaning="Wired network", since=V),
    Icon("network", network, NET, "network", "network-workgroup", "spec", "places", fill=True, meaning="Network, network location", since=V),
    Icon("network-offline", network_offline, NET, "", "network-offline", "spec", "status", meaning="Network disconnected", since=V),
    Icon("bluetooth", bluetooth, NET, "bluetooth", "bluetooth", "gnome", "status", meaning="Bluetooth on", since=V),
    Icon("bluetooth-off", bluetooth_off, NET, "bluetooth-off", "bluetooth-disabled", "gnome", "status", meaning="Bluetooth off", since=V),
    Icon("bluetooth-connected", bluetooth_connected, NET, "bluetooth-connected", "bluetooth-active", "gnome", "status", meaning="Connecting to a Bluetooth device", since=V),
    Icon("globe", globe, NET, "globe", "applications-internet", "spec", "categories", meaning="Internet, browser", since=V),
    # audio
    Icon("volume-mute", volume_mute, AUDIO, "volume-x", "audio-volume-muted", "spec", "status", fill=True, meaning="Muted or 0%", since=V),
    Icon("volume-low", volume_low, AUDIO, "volume-1", "audio-volume-low", "spec", "status", fill=True, ghost=volume_low_ghost, meaning="Low volume (1–49%)", since=V,
         fdo_more=["audio-volume-medium"], note="Linux themes may also use this for audio-volume-medium: some mixers switch names at 25% and 75%, so the medium step (26–75%) takes the low drawing."),
    Icon("speaker", speaker, AUDIO, "speaker", "audio-speakers", "gnome", "devices", fill=True, meaning="Speaker (output device)", since=V),
    Icon("headphones", headphones, AUDIO, "headphones", "audio-headphones", "spec", "devices", fill=True, meaning="Headphones", since=V),
    Icon("microphone", microphone, AUDIO, "mic", "audio-input-microphone", "spec", "devices", fill=True, meaning="Microphone", since=V),
    Icon("microphone-mute", microphone_mute, AUDIO, "mic-off", "microphone-sensitivity-muted", "gnome", "status", fill=True, meaning="Mute microphone", since=V),
    # battery: one outline, the inside changes
    Icon("battery-empty", battery_empty, POWER, "battery", "battery-empty", "gnome", "status", meaning="Battery empty or very low (0–10%)", since=V,
         fdo_more=["battery-caution"]),
    Icon("battery-low", battery_low, POWER, "battery-low", "battery-low", "spec", "status", meaning="Battery low (11–30%)", since=V),
    Icon("battery-full", battery_full, POWER, "battery-full", "battery-full", "gnome", "status", meaning="Battery full (80–100%)", since=V),
    Icon("battery-charging", battery_charging, POWER, "battery-charging", "battery-empty-charging", "gnome", "status", meaning="Charging, battery 0–10% or unknown", since=V,
         fdo_more=["battery-caution-charging"]),
    Icon("battery-charging-low", battery_charging_low, POWER, "", "battery-low-charging", "gnome", "status", meaning="Charging, battery 11–30%", since=V),
    Icon("battery-charging-medium", battery_charging_medium, POWER, "", "battery-good-charging", "gnome", "status", meaning="Charging, battery 31–79%", since=V),
    Icon("battery-charging-full", battery_charging_full, POWER, "", "battery-full-charging", "gnome", "status", meaning="Charging, battery 80–100% or full while plugged in", since=V,
         fdo_more=["battery-full-charged"]),
    Icon("battery-warning", battery_warning, POWER, "battery-warning", "battery-missing", "gnome", "status", meaning="Battery fault (not detected, overheating, damaged)", since=V),
    # display
    Icon("sun", sun, SCREEN, "sun", "weather-clear", "spec", "status", fill=True, meaning="Light appearance", since=V),
    Icon("moon", moon, SCREEN, "moon", "weather-clear-night", "spec", "status", meaning="Dark appearance", since=V),
    Icon("brightness", brightness, SCREEN, "sun-medium", "display-brightness", "gnome", "status", meaning="Screen brightness", since=V),
    Icon("display", display, SCREEN, "monitor", "video-display", "spec", "devices", fill=True, meaning="Monitor", since=V, note="A screen on a stand; computer is the laptop."),
    # input
    Icon("keyboard", keyboard, INPUT, "keyboard", "input-keyboard", "spec", "devices", fill=True, meaning="Keyboard (device, key layout)", since=V),
    Icon("language", language, INPUT, "languages", "preferences-desktop-locale", "spec", "apps", meaning="Language", since=V),
    Icon("input-method", input_method, INPUT, "", "input-method", "kde", "status", meaning="Input method (for example Vietnamese typing)", since=V),
    # control panel
    Icon("sliders", sliders, GENERAL, "sliders-horizontal", "configure", "kde", meaning="Adjustments, view filters", since=V),
    Icon("users", users, GENERAL, "users", "system-users", "kde", "apps", meaning="Users (multiple accounts)", since=V),
    Icon("shield", shield, GENERAL, "shield", "security-medium", "gnome", "status", fill=True, meaning="Security, privacy", since=V),
    Icon("shield-check", shield_check, GENERAL, "shield-check", "security-high", "gnome", "status", fill=True, meaning="Protected / verified", since=V),
    Icon("palette", palette, LOOK, "palette", "preferences-desktop-theme", "spec", "apps", meaning="Appearance, colours", since=V),
    Icon("wallpaper", wallpaper, LOOK, "wallpaper", "preferences-desktop-wallpaper", "spec", "apps", meaning="Wallpaper", since=V),
    Icon("text-size", text_size, LOOK, "a-large-small", "preferences-desktop-font", "spec", "apps", meaning="Font size", since=V),
    Icon("accessibility", accessibility, LOOK, "accessibility", "preferences-desktop-accessibility", "spec", "apps", meaning="Accessibility", since=V),
    Icon("mouse", mouse, DEVICE, "mouse", "input-mouse", "spec", "devices", fill=True, meaning="Mouse", since=V),
    Icon("touchpad", touchpad, DEVICE, "", "input-touchpad", "gnome", "devices", meaning="Touchpad", since=V),
    Icon("printer", printer, DEVICE, "printer", "printer", "spec", "devices", meaning="Printer", since=V),
    Icon("camera", camera, DEVICE, "camera", "camera-photo", "spec", "devices", fill=True, meaning="Camera", since=V),
    Icon("cpu", cpu, PERF, "cpu", "", "", meaning="CPU", since=V),
    Icon("memory", memory, PERF, "memory-stick", "", "", meaning="RAM", since=V, note="A RAM stick, not a computer or drive shape."),
    Icon("storage", storage, PERF, "database", "drive-multidisk", "spec", "devices", meaning="Storage capacity", since=V),
    Icon("chart-line", chart_line, PERF, "chart-line", "", "", meaning="Chart over time", since=V),
    Icon("key", key, SECURE, "key-round", "", "", fill=True, meaning="Keys, recovery codes", since=V),
    Icon("password", password, SECURE, "rectangle-ellipsis", "dialog-password", "spec", "status", meaning="Password", since=V),
    # applications
    Icon("package", package, APPS, "package", "package-x-generic", "spec", "mimetypes", meaning="Application package", since=V),
    Icon("install", install, APPS, "package-plus", "", "", meaning="Install (unlike download)", since=V, note="A package with an arrow going in: installed, not just downloaded."),
    Icon("uninstall", uninstall, APPS, "package-minus", "", "", meaning="Uninstall", since=V),
    Icon("update", update, APPS, "circle-arrow-up", "system-software-update", "spec", "apps", fill=True, meaning="Update", since=V),
    Icon("launch", launch, APPS, "rocket", "system-run", "spec", meaning="Launch app", since=V),
    # running work
    Icon("pause", pause, TASK, "pause", "media-playback-pause", "spec", fill=True, meaning="Pause", since=V),
    Icon("resume", resume, TASK, "play", "media-playback-start", "spec", fill=True, meaning="Resume", since=V),
    Icon("stop", stop, TASK, "square", "media-playback-stop", "spec", fill=True, meaning="Stop", since=V, aliases=["end-task"]),
    Icon("history", history, TASK, "history", "document-open-recent", "spec", meaning="History", since=V),
    # documents
    Icon("save", save, DOCS, "save", "document-save", "spec", fill=True, meaning="Save", since=V),
    Icon("save-as", save_as, DOCS, "", "document-save-as", "spec", meaning="Save as", since=V),
    Icon("replace", replace, DOCS, "replace", "edit-find-replace", "spec", meaning="Replace (overwrite an existing item)", since=V),
    Icon("skip", skip, DOCS, "skip-forward", "media-skip-forward", "spec", fill=True, meaning="Skip", since=V),
    # backup
    Icon("backup", backup, BACKUP, "database-backup", "", "", meaning="Backup", since=V, note="The body is storage: unlike download/upload (tray) and archive (compression)."),
    Icon("backup-restore", backup_restore, BACKUP, "archive-restore", "", "", meaning="Restore from backup", since=V, note="Unlike restore (trash), undo and upload."),
    # operating system install
    Icon("partition", partition, OSINSTALL, "", "", "", meaning="Disk partitions", since=V),
    Icon("disk-image", disk_image, OSINSTALL, "disc-3", "media-optical", "spec", "devices", meaning="Disk image, optical disc", since=V),
    Icon("startup", startup, TASK, "gauge", "", "", meaning="Apps that start with the session", since=V),
    # messages
    Icon("success", success, MESSAGE, "circle-check", "dialog-ok", "kde", "status", fill=True, meaning="Success", since=V),
    Icon("error", error, MESSAGE, "octagon-x", "dialog-error", "spec", "status", fill=True, meaning="Error", since=V, note="An octagon: differs from success/info by shape, not only colour."),
    Icon("help", help_, MESSAGE, "circle-help", "help-browser", "spec", "apps", fill=True, meaning="Help", since=V),
    Icon("more-vertical", more_vertical, NAV, "ellipsis-vertical", "view-more", "gnome", meaning="More actions (vertical)", since=V),
    Icon("book-open", book_open, APPS, "book-open", "accessories-dictionary", "spec", "apps", meaning="Read, view a document", since=V),
    Icon("brush", brush, APPS, "brush", "applications-graphics", "spec", "categories", meaning="Draw, graphics", since=V),
    Icon("system-install", system_install, OSINSTALL, "hard-drive-download", "system-software-install", "spec", "apps", meaning="Install the system to a drive (installing state)", since=V),
    Icon("note", note, APPS, "sticky-note", "accessories-text-editor", "spec", "apps", fill=True, meaning="Notes", since=V, note="Added so that a notes app has a 16 px symbol."),
    # files, extended flows
    Icon("pin", pin, FILES, "pin", "view-pin", "gnome", fill=True, meaning="Pin (pushpin)", since=V),
    Icon("unpin", unpin, FILES, "pin-off", "", "", fill=True, meaning="Unpin", since=V),
    Icon("eye", eye, FILES, "eye", "view-reveal", "gnome", fill=True, meaning="Show (hidden files, password)", since=V),
    Icon("eye-off", eye_off, FILES, "eye-off", "view-conceal", "gnome", fill=True, meaning="Hide", since=V),
    Icon("zoom-in", zoom_in, FILES, "zoom-in", "zoom-in", "spec", meaning="Zoom in", since=V),
    Icon("zoom-out", zoom_out, FILES, "zoom-out", "zoom-out", "spec", meaning="Zoom out", since=V),
    Icon("open-with", open_with, FILES, "", "", "", meaning="Open with another app", since=V),
    Icon("copy-path", copy_path, FILES, "", "", "", meaning="Copy path", since=V),
    Icon("link", link, FILES, "link-2", "insert-link", "spec", meaning="Link", since=V),
    Icon("move-to", move_to, FILES, "folder-input", "", "", fill=True, meaning="Move to", since=V),
    Icon("archive-create", archive_create, FILES, "", "", "", meaning="Compress into an archive", since=V),
    Icon("archive-extract", archive_extract, FILES, "", "", "", meaning="Extract", since=V),
    Icon("connect", connect, FILES, "plug", "", "", meaning="Connect", since=V),
    Icon("disconnect", disconnect, FILES, "unplug", "", "", meaning="Disconnect", since=V),
]

# Network states.
_STATES = {"limited": (_sign_limited, "connected without internet access"), "locked": (_sign_locked, "password-protected network")}
_BASES = [
    ("wifi-none", wifi_none, wifi_none_ghost, "Wi-Fi with no signal"),
    ("wifi-low", wifi_low, wifi_low_ghost, "Wi-Fi weak signal"),
    ("wifi-medium", wifi_medium, wifi_medium_ghost, "Wi-Fi medium signal"),
    ("wifi", wifi, None, "Wi-Fi strong signal"),
    ("ethernet", ethernet, None, "Wired network connected"),
]
for _code, _base, _ghost, _label in _BASES:
    for _state, (_sign, _what) in _STATES.items():
        _draw, _g = _signed(_base, _ghost, _sign)
        SYSTEM_ICONS.append(Icon(f"{_code}-{_state}", _draw, NET, "", "", "", "status", ghost=_g, meaning=f"{_label}, {_what}", since=V4,
                             note="Corner sign precomposed under the freedesktop name; an interface may still add its own lock or label."))
SYSTEM_ICONS += [
    Icon("ethernet-off", ethernet_off, NET, "", "network-wired-disconnected", "gnome", "status", meaning="Network cable unplugged", since=V4),
    Icon("hotspot", hotspot, NET, "", "network-wireless-hotspot", "gnome", "status", meaning="Wi-Fi hotspot", since=V4),
]
