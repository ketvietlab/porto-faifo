"""Porto Faifo Symbols recipes: business apps, navigation, windows and status.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

import math

from pfsans.geometry import polygon

from .icons import HI, LO, R, Icon, _at, _u, arrow_up_right, info
from .icons_desktop import _crossed
from .icons_system import _gap
from .kit import BIG, box, clip, minus, mirrored, region, turned, union

V6 = "0.6.0"

APP = "Apps"
TALK = "Communication"
WORK = "Business"
NAV = "Navigation"
WINDOW = "Windows"
STATUS = "Status"


def _flipped(r):
    """``r`` upside down (mirrored about y = 12)."""
    return turned(mirrored(r), 180)


def _circle(c, r, a0, a1, n=48):
    """Points on the circle (c, r) from ``a0`` to ``a1`` degrees."""
    return [_at(c, _u(a0 + (a1 - a0) * i / n), r) for i in range(n + 1)]


# ----------------------------------------------------------------- products
def layers(p, fill=False):
    """Three sheets: the top one whole, the two below only their front edges."""
    top = [(12, 20.9), (21.0, 16.9), (12, 12.9), (3.0, 16.9)]
    sheet = (p.solid if fill else p.frame)(top, corners={0: p.radius_small, 2: p.radius_small})
    edges = [p.line([(3.0, 16.9 - d), (12, 12.9 - d), (21.0, 16.9 - d)], corners={1: p.radius_small}) for d in (5.0, 10.0)]
    return union(sheet, *edges)


def dashboard(p, fill=False):
    """Four panels of two heights, crossed so no column reads as a grid (apps)."""
    rect = p.rect_solid if fill else p.rect
    return union(rect(3.4, 11.6, 10.0, 20.6, r=1.5), rect(3.4, 3.4, 10.0, 7.6, r=1.5),
                 rect(14.0, 16.4, 20.6, 20.6, r=1.5), rect(14.0, 3.4, 20.6, 12.4, r=1.5))


def building(p, fill=False):
    """A tower between two lower wings: an office, a company."""
    s = p.radius_small
    windows = union(*(p.bar((10.4, y), (13.6, y)) for y in (16.8, 12.8, 8.8)))
    wings = union(p.line([(7.4, 11.6), (3.6, 11.6), (3.6, LO), (7.4, LO)], corners={1: s, 2: s}),
                  p.line([(16.6, 15.0), (20.4, 15.0), (20.4, LO), (16.6, LO)], corners={1: s, 2: s}))
    if fill:
        return union(minus(p.rect_solid(7.4, LO, 16.6, HI, r=s), windows), wings)
    return union(p.rect(7.4, LO, 16.6, HI, r=s), windows, wings)


def hotel(p, fill=False):
    """One block with windows and an arched door: a place to stay."""
    windows = union(*(p.dot(x, y) for x in (8.8, 15.2) for y in (17.0, 13.0)))
    door = p.line([(9.8, LO), (9.8, 8.6), (14.2, 8.6), (14.2, LO)], corners={1: 2.2, 2: 2.2})
    if fill:
        knock = p.solid([(9.8, LO - 2), (14.2, LO - 2), (14.2, 8.6), (9.8, 8.6)], corners={2: 2.2, 3: 2.2})
        return minus(p.rect_solid(4.6, LO, 19.4, HI), windows, knock)
    return union(p.rect(4.6, LO, 19.4, HI), windows, door)


def branch(p, fill=False):
    """A branch leaving the main line in a quarter turn (git branch, a flow)."""
    ring = p.disc if fill else p.ring
    return union(ring(6.6, 6.2, 2.6), ring(17.4, 17.0, 2.6), p.bar((6.6, HI), (6.6, 8.8), cut=("h", "p")),
                 p.arc(9.2, 14.4, 8.2, keep=box(x0=9.2, y1=14.4)))


def route(p, fill=False):
    """A road between two stops, doubling back once."""
    ring = p.disc if fill else p.ring
    road = p.line([(8.0, 5.4), (19.2, 5.4), (19.2, 12.0), (4.8, 12.0), (4.8, 18.6), (16.0, 18.6)],
                  cut="p", corners={1: 3.2, 2: 3.2, 3: 3.2, 4: 3.2})
    return union(ring(5.6, 5.4, 2.4), ring(18.4, 18.6, 2.4), road)


def target(p, fill=False):
    c = 12
    if fill:
        return union(minus(p.disc(c, c, R), p.disc(c, c, 4.8 + _gap(p))), p.ring(c, c, 4.8), p.dot(c, c, big=True))
    return union(p.ring(c, c, R), p.ring(c, c, 4.8), p.dot(c, c, big=True))


def megaphone(p, fill=False):
    """A horn opening to the right, its handle under the narrow end."""
    horn = [(4.0, 9.6), (19.4, 4.6), (19.4, 19.4), (4.0, 14.4)]
    handle = p.bar((8.4, 8.2), (8.4, LO), cut="h")
    return union((p.solid if fill else p.frame)(horn), handle)


def radio_tower(p, fill=False):
    """A mast under a beacon that sends on both sides.  No cross brace: with
    one the mast reads as the letter A."""
    c = (12, 15.6)
    waves = [p.arc(*c, r, keep=box(y0=c[1] - 0.5 * r, y1=c[1] + 0.5 * r)) for r in (4.3, 8.4)]
    mast = p.line([(8.0, LO), (12, 11.8), (16.0, LO)], cut="h")
    return union(p.dot(*c, big=fill), *waves, mast)


def _star(c, big, small, k=0.42):
    """A four-point star: tips ``big`` out on the axes, waist ``k * big``."""
    pts = []
    for i in range(8):
        a = 90 + 45 * i
        pts.append(_at(c, _u(a), big if i % 2 == 0 else k * big))
    return pts


def sparkles(p, fill=False):
    """A star with a small plus beside it: something made for you (AI)."""
    star = _star((10.4, 10.4), 7.6, 0)
    corners = {i: (p.radius_small if i % 2 == 0 else p.radius) for i in range(8)}
    x, y, s = 18.0, 18.0, 2.9
    plus_ = union(p.bar((x, y - s), (x, y + s)), p.bar((x - s, y), (x + s, y)))
    return union((p.solid if fill else p.frame)(star, corners=corners), plus_)


def bot(p, fill=False):
    """A robot head: antenna, ears and two dot eyes."""
    s = p.radius_small
    head = (5.4, 3.4, 18.6, 15.6)
    eyes = union(p.dot(9.2, 9.8), p.dot(14.8, 9.8))
    antenna = p.line([(12, 15.6), (12, 19.8), (8.6, 19.8)], corners={1: s})
    ears = union(p.bar((LO, 9.6), (5.4, 9.6)), p.bar((18.6, 9.6), (HI, 9.6)))
    if fill:
        return union(minus(p.rect_solid(*head), eyes), antenna, ears)
    return union(p.rect(*head), eyes, antenna, ears)


def flask(p, fill=False):
    """A conical flask, a third full: a lab, an experiment."""
    body = [(9.8, 19.4), (9.8, 13.4), (4.2, 3.2), (19.8, 3.2), (14.2, 13.4), (14.2, 19.4)]
    corners = {1: p.radius_small, 2: p.radius, 3: p.radius, 4: p.radius_small}
    rim = p.bar((8.0, 19.4), (16.0, 19.4))
    if fill:
        liquid = clip(p.solid(body[1:5], corners={0: 0, 1: p.radius, 2: p.radius, 3: 0}), box(y1=8.8))
        return union(p.line(body, corners=corners), rim, liquid)
    return union(p.line(body, corners=corners), rim, p.bar((7.25, 8.8), (16.75, 8.8), cut="p"))


def scale(p, fill=False):
    """Scales of justice: a pole, a beam and two hanging pans."""
    pole = p.bar((12, 19.6), (12, LO), cut="h")
    base = p.bar((7.6, LO), (16.4, LO))
    beam = p.bar((3.6, 17.4), (20.4, 17.4))

    def pan(x):
        strings = p.line([(x - 2.4, 10.4), (x, 17.4), (x + 2.4, 10.4)], cut="h", corners={1: 1.0})
        bowl = p.arc(x, 10.4, 2.4, keep=box(y1=10.4))
        return union(strings, bowl, clip(p.disc(x, 10.4, 2.4), box(y1=10.4)) if fill else bowl)

    return union(pole, base, beam, pan(5.6), pan(18.4))


# --------------------------------------------------------------------- money
def wallet(p, fill=False):
    """A wallet with its clasp on the right and a card behind the flap."""
    s = p.radius_small
    clasp = p.line([(HI, 14.4), (16.0, 14.4), (16.0, 9.6), (HI, 9.6)], corners={1: s, 2: s})
    card = p.line([(6.0, 17.4), (17.2, 20.6), (17.2, 17.4)], corners={1: s})
    if fill:
        knock = p.stroked(p.w + 2 * _gap(p)).solid([(HI + 2, 14.4), (16.0, 14.4), (16.0, 9.6), (HI + 2, 9.6)], r=s)
        return union(minus(p.rect_solid(LO, 3.4, HI, 17.4), knock), clasp, card)
    return union(p.rect(LO, 3.4, HI, 17.4), clasp, card)


def credit_card(p, fill=False):
    stripe = p.bar((LO, 14.4), (HI, 14.4))
    chip = p.bar((6.4, 8.8), (10.4, 8.8))
    if fill:
        return minus(p.rect_solid(LO, 5.0, HI, 19.0), chip, p.stroked(p.w + 2 * _gap(p)).bar((LO - 2, 14.4), (HI + 2, 14.4)))
    return union(p.rect(LO, 5.0, HI, 19.0), stripe, chip)


def calculator(p, fill=False):
    """A display and a 2 x 2 keypad: three columns of keys lose their gaps at Bold."""
    display = p.bar((8.6, 16.6), (15.4, 16.6))
    keys = union(*(p.dot(x, y) for x in (9.0, 15.0) for y in (11.6, 6.8)))
    if fill:
        return minus(p.rect_solid(5.0, LO, 19.0, HI), display, keys)
    return union(p.rect(5.0, LO, 19.0, HI), display, keys)


def shopping_bag(p, fill=False):
    """A shopping bag: bevelled top, a band, a smile for a handle."""
    bag = [(4.0, LO), (20.0, LO), (20.0, 16.4), (17.4, 20.6), (6.6, 20.6), (4.0, 16.4)]
    corners = {0: p.radius_small, 1: p.radius_small, 2: 0, 3: p.radius_small, 4: p.radius_small, 5: 0}
    band = p.bar((4.0, 16.4), (20.0, 16.4))
    smile = p.arc(12, 13.0, 3.4, keep=box(y1=13.0))
    if fill:
        return union(p.frame(bag, corners=corners), minus(p.solid(bag, corners=corners), box(y0=16.4 - p.h - _gap(p)), smile), band)
    return union(p.frame(bag, corners=corners), band, smile)


def trending_up(p, fill=False):
    c = (20.6, 16.8)
    trend = p.line([(3.4, 7.6), (8.8, 13.0), (12.8, 9.0), c], cut="p")
    return union(trend, p.line([(14.6, c[1]), c, (c[0], c[1] - 6.0)]))


def trending_down(p, fill=False):
    return _flipped(trending_up(p))


def arrow_down_left(p, fill=False):
    return turned(arrow_up_right(p), 180)


# --------------------------------------------------------------- talk, mail
def _handset(grip=3.8, pad=6.4, reach=5.2, flare=0.4):
    """The handset centre line, symmetric about y = x: earpiece top left,
    mouthpiece bottom right, the back a quarter circle round (20.6, 20.6).
    The pads are wider than the grip (6.4 against 3.8) and step down to it
    in a 45-degree notch: with a grip as wide as the pads the handset reads
    as a band, not as a phone.  A heavy pen widens the grip so its counter
    stays open.  The arcs drop their samples next to the rounded corners, so
    each rounding has a whole segment to turn on (at 1024 px a 0.6-unit
    segment left a kink).  Returns the points and the index of the last
    point of the back."""
    c, ro = (20.6, 20.6), 17.6
    ri = ro - grip
    top = (3.0 + pad, c[1])
    foot = (top[0] + flare, c[1] - reach)
    # the notch runs down-left from the foot until it meets the grip
    u, v = c[0] - foot[0], c[1] - foot[1]
    t = (-(u + v) + math.sqrt((u + v) ** 2 - 2 * (u * u + v * v - ri * ri))) / 2
    a0 = math.degrees(math.atan2(foot[1] - t - c[1], foot[0] - t - c[0])) % 360
    flip = lambda q: (q[1], q[0])
    back = _circle(c, ro, 270, 180)
    back = back[:1] + back[4:-4] + back[-1:]
    grip_ = _circle(c, ri, a0, 450 - a0, 24)
    grip_ = grip_[:1] + grip_[4:-4] + grip_[-1:]
    return back + [top, foot] + grip_ + [flip(foot), flip(top)], len(back) - 1


def phone(p, fill=False):
    pts, n = _handset(grip=max(3.8, p.w + 1.4))
    corners = {i: 0 for i in range(len(pts))}
    corners.update({0: 1.6, n: 1.6})
    for i in (n + 1, n + 2, n + 3, len(pts) - 3, len(pts) - 2, len(pts) - 1):
        corners[i] = p.radius_small
    return (p.solid if fill else p.frame)(pts, corners=corners)


def _call(p, tip, tail):
    """A 45-degree call arrow from ``tail`` to the corner ``tip``."""
    d = (1 if tip[0] > tail[0] else -1)
    n = 5.4
    head = p.line([(tip[0] - d * n, tip[1]), tip, (tip[0], tip[1] - d * n)])
    return union(p.bar(tail, tip, cut=("h", "p")), head)


def phone_incoming(p, fill=False):
    return union(phone(p, fill), _call(p, (15.2, 15.2), (20.2, 20.2)))


def phone_outgoing(p, fill=False):
    return union(phone(p, fill), _call(p, (20.6, 20.6), (15.2, 15.2)))


def phone_off(p, fill=False):
    """The slash runs bottom left to top right, against the rule: the usual
    one would lie along the grip and read as a seam, not as "off"."""
    return mirrored(_crossed(p, mirrored(phone(p, fill))))


def smartphone(p, fill=False):
    if fill:
        return minus(p.rect_solid(6.0, LO, 18.0, HI), p.dot(12, 7.0))
    return union(p.rect(6.0, LO, 18.0, HI), p.dot(12, 7.0))


def chat(p, fill=False):
    """A round speech bubble, its tail at the bottom left."""
    c = (12.4, 12.4)
    pts = _circle(c, 8.0, 245, 565, 64) + [(3.6, 3.6)]
    corners = {i: 0 for i in range(len(pts))}
    corners[len(pts) - 1] = p.radius_small
    return (p.solid if fill else p.frame)(pts, corners=corners)


def inbox(p, fill=False):
    """A tray: the drop in its lip is where mail lands."""
    s = p.radius_small
    tray = [(LO, 3.4), (HI, 3.4), (HI, 11.4), (18.0, 19.6), (6.0, 19.6), (LO, 11.4)]
    lip = [(LO, 11.4), (8.0, 11.4), (9.6, 8.4), (14.4, 8.4), (16.0, 11.4), (HI, 11.4)]
    corners = {0: p.radius, 1: p.radius, 2: 0, 3: s, 4: s, 5: 0}
    if fill:
        below = polygon([(-BIG, 11.4)] + lip[1:-1] + [(BIG, 11.4), (BIG, -BIG), (-BIG, -BIG)])
        load = clip(p.solid(tray, corners=corners), region(below.oriented(True)))
        return union(load, p.frame(tray, corners=corners), p.line(lip, corners={1: s, 2: s, 3: s, 4: s}))
    return union(p.frame(tray, corners=corners), p.line(lip, corners={1: s, 2: s, 3: s, 4: s}))


# ------------------------------------------------------------ window, status
def enlarge(p, fill=False):
    """Two corners pushed out along the diagonal (a panel grows)."""
    n, c = 6.2, 20.6
    one = union(p.line([(c - n, c), (c, c), (c, c - n)]), p.bar((14.0, 14.0), (c, c), cut=("h", "p")))
    return union(one, turned(one, 180))


def shrink(p, fill=False):
    """Two corners pulled in along the diagonal (a panel folds away)."""
    n, c = 6.2, 10.4
    one = union(p.line([(c - n, c), (c, c), (c, c - n)]), p.bar((3.4, 3.4), (c, c), cut=("h", "p")))
    return union(one, turned(one, 180))


def alert(p, fill=False):
    """``info`` upside down: the stroke above the dot reads as "!"."""
    return turned(info(p, fill), 180)


# ------------------------------------------------------------- business
def warehouse(p, fill=False):
    """A wide shed under a pitched roof over a roller door: stock.  The
    roof is what keeps it from reading as a bin (archive, trash).  The door
    is square (rounded, with one slat, it read as a letter A) and gets two
    slats where the pen leaves a unit between them; at Medium and Bold one
    slat sits under the lintel, the shutter rolled up."""
    shed = [(LO, LO), (HI, LO), (HI, 13.8), (12, 20.4), (LO, 13.8)]
    corners = {0: p.radius, 1: p.radius, 2: p.radius_small, 3: p.radius_small, 4: p.radius_small}
    top = 12.0
    door = p.line([(7.0, LO), (7.0, top), (17.0, top), (17.0, LO)], corners={1: 0, 2: 0})
    if (top - LO) / 3 - p.w >= 1.0:
        ys = [top - (top - LO) / 3, top - 2 * (top - LO) / 3]
    else:  # one slat, a gap under the lintel: the rolled-up shutter, not a crossbar
        ys = [top - p.w - 1.1]
    slat = union(*(p.bar((7.0, y), (17.0, y), cut="p") for y in ys))
    if fill:
        knock = p.stroked(p.w + 2 * _gap(p)).solid([(7.0, LO - 2), (17.0, LO - 2), (17.0, top), (7.0, top)], r=0)
        return union(minus(p.solid(shed, corners=corners), knock), door, slat)
    return union(p.frame(shed, corners=corners), door, slat)


def cart(p, fill=False):
    """A shopping cart: handle, a basket narrowing to the bottom, two wheels."""
    basket = p.line([(LO, 20.4), (5.0, 20.4), (7.8, 9.4), (18.6, 9.4), (20.8, 16.6), (5.9, 16.6)],
                    corners={1: p.radius_small, 2: p.radius_small, 3: p.radius_small, 4: p.radius_small})
    if fill:
        basket = union(basket, p.solid([(5.9, 16.6), (7.8, 9.4), (18.6, 9.4), (20.8, 16.6)], r=p.radius_small))
    return union(basket, p.dot(9.4, 4.6, big=True), p.dot(17.4, 4.6, big=True))


def send(p, fill=False):
    """A paper plane leaving to the top right."""
    plane = [(20.8, 20.8), (14.6, 3.2), (11.0, 11.0), (3.2, 14.6)]
    corners = {0: p.radius_small, 1: p.radius_small, 2: 0, 3: p.radius_small}
    fold = p.bar((11.0, 11.0), (20.8, 20.8), cut="p")
    if fill:
        return minus(p.solid(plane, corners=corners), p.stroked(_gap(p)).bar((11.0, 11.0), (19.4, 19.4), cut="p"))
    return union(p.frame(plane, corners=corners), fold)


def contact(p, fill=False):
    """A person on a card: a contact, a customer record."""
    head = (12, 13.6)
    person = union((p.disc if fill else p.ring)(*head, 2.6), p.arc(12, LO, 4.4, 4.0, keep=box(y0=LO)))
    if fill:
        return minus(p.rect_solid(LO, LO, HI, HI), p.stroked(p.w + 2 * _gap(p)).ring(*head, 2.6), clip(p.disc(12, LO, 4.4 + _gap(p), 4.0 + _gap(p)), box(y0=LO)), p.disc(*head, 2.6))
    return union(p.rect(LO, LO, HI, HI), person)


def store(p, fill=False):
    """A shop front: a scalloped awning over a door."""
    c = 3.04  # scallop radius: three across LO..HI
    awning = [(4.2, 20.6), (19.8, 20.6), (HI, 14.6), (LO, 14.6)]
    corners = {0: p.radius_small, 1: p.radius_small, 2: p.radius_small, 3: p.radius_small}
    scallops = union(*(p.arc(LO + c * (2 * i + 1), 14.6, c, keep=box(y1=14.6)) for i in range(3)))
    walls = union(p.bar((4.6, 12.6), (4.6, LO), cut=("p", "h")), p.bar((19.4, 12.6), (19.4, LO), cut=("p", "h")),
                  p.bar((4.6, LO), (19.4, LO), cut="p"))
    door = p.line([(9.8, LO), (9.8, 7.6), (14.2, 7.6), (14.2, LO)], corners={1: p.radius_small, 2: p.radius_small})
    if fill:
        scallops = union(scallops, *(clip(p.disc(LO + c * (2 * i + 1), 14.6, c), box(y1=14.6)) for i in range(3)))
    return union((p.solid if fill else p.frame)(awning, corners=corners), scallops, walls, door)


def truck(p, fill=False):
    """A lorry: a box, a cab with a sloped front, two wheels on the line."""
    y, r = 5.8, 2.4
    wheels = [(7.4, y), (17.4, y)]
    s = p.radius_small
    box_ = p.line([(7.4 - r, y), (LO, y), (LO, 19.6), (13.6, 19.6), (13.6, y)], corners={1: p.radius, 2: p.radius, 3: s})
    cab = p.line([(13.6, 15.2), (17.4, 15.2), (HI, 10.8), (HI, y), (17.4 + r, y)], corners={1: s, 2: s, 3: p.radius})
    under = p.bar((7.4 + r, y), (17.4 - r, y))
    return union(box_, cab, under, *(p.ring(*w, r) for w in wheels))


def factory(p, fill=False):
    """A chimney and a sawtooth roof, three windows: production."""
    s = p.radius_small
    hall = [(LO, LO), (LO, 20.6), (8.6, 20.6), (8.6, 12.6), (14.8, 16.4), (14.8, 12.6), (HI, 16.4), (HI, LO)]
    corners = {0: p.radius, 1: s, 2: s, 3: s, 4: s, 5: s, 6: s, 7: p.radius}
    windows = union(*(p.dot(x, 7.4) for x in (8.2, 12.4, 16.6)))
    if fill:
        return minus(p.solid(hall, corners=corners), windows)
    return union(p.frame(hall, corners=corners), windows)


def banknote(p, fill=False):
    """A note with a coin in the middle; the side dots go when the pen would close their gaps."""
    note = (LO, 5.4, HI, 18.6)
    coin = p.ring(12, 12, 2.6)
    dots = [p.dot(x, 12) for x in (6.4, 17.6)] if 6.4 - LO - p.h - p.dot_d / 2 >= 1.0 and 12 - 2.6 - p.h - 6.4 - p.dot_d / 2 >= 0.9 else []
    if fill:
        return minus(p.rect_solid(*note, r=p.radius_small), p.ring(12, 12, 2.6), *dots)
    return union(p.rect(*note, r=p.radius_small), coin, *dots)


def newspaper(p, fill=False):
    """A front page with its back column folded out on the left."""
    s = p.radius_small
    page = (6.6, 3.4, HI, 20.6)
    back = p.line([(6.6, 13.0), (LO, 13.0), (LO, 3.4), (6.6, 3.4)], cut="p", corners={1: s, 2: p.radius})
    lines = union(p.bar((10.4, 16.3), (17.6, 16.3)), p.bar((10.4, 12.0), (17.6, 12.0)), p.bar((10.4, 7.7), (14.6, 7.7)))
    if fill:
        return union(minus(p.rect_solid(*page, r=s), lines), back)
    return union(p.rect(*page, r=s), back, lines)


def _small_folder(y0):
    return [(12.4, y0), (HI, y0), (HI, y0 + 5.6), (17.2, y0 + 5.6), (16.0, y0 + 7.2), (12.4, y0 + 7.2)]


def folder_tree(p, fill=False):
    """A trunk on the left feeding two small folders: a folder hierarchy."""
    s = p.radius_small
    shape = p.solid if fill else p.frame
    folders = union(*(shape(_small_folder(y0), corners={0: s, 1: s, 2: s, 3: s, 4: s, 5: s}) for y0 in (13.4, 3.2)))
    trunk = union(p.line([(3.6, HI), (3.6, 6.8), (12.4, 6.8)], corners={1: p.radius}), p.bar((3.6, 17.0), (12.4, 17.0), cut="p"))
    return union(folders, trunk)


def clipboard_list(p, fill=False):
    """A clipboard with a list: dots and lines."""
    s = p.radius_small
    board = p.line([(8.4, 19.4), (4.6, 19.4), (4.6, LO), (19.4, LO), (19.4, 19.4), (15.6, 19.4)],
                   corners={1: p.radius, 2: p.radius, 3: p.radius, 4: p.radius})
    clip_ = (p.rect_solid if fill else p.rect)(8.4, 17.6, 15.6, HI, r=s)
    rows = union(*(union(p.dot(8.6, y), p.bar((11.4, y), (15.8, y))) for y in (12.8, 7.6)))
    return union(board, clip_, rows)


BUSINESS_ICONS = [
    # products and places
    Icon("layers", layers, APP, "layers-3", fill=True, meaning="Layers / app suite", since=V6),
    Icon("dashboard", dashboard, NAV, "layout-dashboard", fill=True, meaning="Dashboard / overview", since=V6, note="Four tiles of two heights, staggered; unlike apps (an even grid)."),
    Icon("building", building, APP, "building-2", fill=True, meaning="Company / building", since=V6),
    Icon("hotel", hotel, APP, "hotel", fill=True, meaning="Hotel / lodging", since=V6),
    Icon("branch", branch, APP, "git-branch", fill=True, meaning="Branch / flow", since=V6),
    Icon("route", route, APP, "route", fill=True, meaning="Route", since=V6),
    Icon("target", target, WORK, "target", fill=True, meaning="Target", since=V6),
    Icon("megaphone", megaphone, APP, "megaphone", fill=True, meaning="Advertising / announcements (Ads)", since=V6),
    Icon("radio-tower", radio_tower, TALK, "radio-tower", meaning="Distribution channel / OTA", since=V6),
    Icon("sparkles", sparkles, APP, "sparkles", fill=True, meaning="AI / generate", since=V6),
    Icon("bot", bot, APP, "bot", fill=True, meaning="Virtual assistant / bot", since=V6),
    Icon("flask", flask, APP, "flask-conical", fill=True, meaning="Experiment", since=V6),
    Icon("scale", scale, WORK, "scale", fill=True, meaning="Legal / balance", since=V6),
    # money
    Icon("wallet", wallet, WORK, "wallet", fill=True, meaning="Wallet", since=V6),
    Icon("credit-card", credit_card, WORK, "credit-card", fill=True, meaning="Card / payment", since=V6),
    Icon("calculator", calculator, WORK, "calculator", fill=True, meaning="Accounting / calculator", since=V6, note="A 2 × 2 keypad: three columns of keys lose their gaps at Bold."),
    Icon("shopping-bag", shopping_bag, WORK, "shopping-bag", fill=True, meaning="Sales / sales channel", since=V6),
    Icon("trending-up", trending_up, WORK, "trending-up", meaning="Increase", since=V6),
    Icon("trending-down", trending_down, WORK, "trending-down", meaning="Decrease", since=V6),
    Icon("arrow-down-left", arrow_down_left, NAV, "arrow-down-left", meaning="Money in / receive", since=V6),
    # talk and mail
    Icon("phone", phone, TALK, "phone", fill=True, meaning="Call", since=V6),
    Icon("phone-incoming", phone_incoming, TALK, "phone-incoming", meaning="Incoming call", since=V6),
    Icon("phone-outgoing", phone_outgoing, TALK, "phone-outgoing", meaning="Outgoing call", since=V6),
    Icon("phone-off", phone_off, TALK, "phone-off", meaning="End / decline call", since=V6),
    Icon("smartphone", smartphone, TALK, "smartphone", fill=True, meaning="Mobile phone", since=V6),
    Icon("chat", chat, TALK, "message-circle", fill=True, meaning="Chat", since=V6),
    Icon("inbox", inbox, TALK, "inbox", fill=True, meaning="Inbox", since=V6),
    # window and status
    Icon("enlarge", enlarge, WINDOW, "maximize-2", meaning="Expand panel", since=V6, note="Two corners pushed out along the diagonal; unlike fullscreen (four corners)."),
    Icon("shrink", shrink, WINDOW, "minimize-2", meaning="Collapse panel", since=V6),
    Icon("alert", alert, STATUS, "circle-alert", fill=True, meaning="Needs attention", since=V6, note="info upside down: stroke above, dot below."),
    Icon("warehouse", warehouse, WORK, "warehouse", fill=True, meaning="Warehouse", since=V6, note="Pitched roof and roller door; unlike archive (storage box) and trash."),
    Icon("cart", cart, WORK, "shopping-cart", fill=True, meaning="Purchasing / shopping cart", since=V6),
    Icon("send", send, TALK, "send", fill=True, meaning="Send", since=V6),
    Icon("contact", contact, WORK, "contact-round", fill=True, meaning="Contacts / customers (CRM)", since=V6),
    Icon("store", store, WORK, "store", fill=True, meaning="Store / point of sale", since=V6),
    Icon("truck", truck, WORK, "truck", meaning="Delivery / shipping", since=V6),
    Icon("factory", factory, WORK, "factory", fill=True, meaning="Manufacturing", since=V6),
    Icon("banknote", banknote, WORK, "banknote", fill=True, meaning="Cash / income and expenses", since=V6, note="Drop the two side dots when a heavy stroke would make them touch."),
    Icon("newspaper", newspaper, APP, "newspaper", fill=True, meaning="News / articles", since=V6),
    Icon("folder-tree", folder_tree, APP, "folder-tree", fill=True, meaning="Tree / categories", since=V6),
    Icon("clipboard-list", clipboard_list, WORK, "clipboard-list", fill=True, meaning="Task list / stock count", since=V6),
]
