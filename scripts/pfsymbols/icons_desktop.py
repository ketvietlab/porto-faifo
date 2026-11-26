"""Porto Faifo Symbols recipes: desktop actions and states.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

import math

from pfsans.geometry import superellipse

from .icons import HI, LO, Icon, arrow_up, bell, file, folder, power, volume, window_maximize
from .icons_system import (
    _badged,
    _gap,
    _sign_locked,
    _sign_plus,
    _slash,
    globe,
    history,
    microphone,
    moon,
    restart,
    update,
)
from .kit import BIG, _without_crumbs, box, clip, minus, mirrored, region, turned, union

V5 = "0.5.0"
CORNER = (17.4, 7.0)


# ------------------------------------------------------------ corner signs
def _badge(p, base, sign):
    """``_badged`` without the slivers a knock can leave on a curve."""
    return _without_crumbs(_badged(p, base, sign), (0.5 * p.w) ** 2)


def _corner(p, base, sign):
    """A sign in the lower-right corner knocks the whole corner of the base
    out, from its heavier outline to the edge, so no wedge of the frame is
    left between its arms."""
    x0, _, _, y1 = sign(p.stroked(p.w + 2 * _gap(p))).bounds
    return _without_crumbs(union(minus(base, box(x0, -BIG, BIG, y1)), sign(p)), (0.5 * p.w) ** 2)


def _crossed(p, base):
    return _without_crumbs(_slash(p, base), (0.5 * p.w) ** 2)


def _sign_x(c=CORNER, s=2.4):
    return lambda p: union(p.bar((c[0] - s, c[1] - s), (c[0] + s, c[1] + s)), p.bar((c[0] - s, c[1] + s), (c[0] + s, c[1] - s)))


def _sign_dot(c=(17.8, 6.6), r=2.2):
    return lambda p: p.disc(*c, r)


def _sign_unlocked(p):
    """The corner lock with its shackle lifted off the left leg."""
    x, half, top, r = 18.5, 2.6, 9.4, 1.9
    body = p.rect_solid(x - half, LO, x + half, 6.6, r=p.radius_small)
    return union(body, p.arc(x, top, r, keep=box(y0=top)), p.bar((x + r, 6.6), (x + r, top), cut="p"))


def _sign_out(p):
    """Up and to the right, out of the frame: detach."""
    return union(p.bar((15.0, 4.4), (19.8, 9.2), cut=("h", "p")), p.line([(16.0, 9.2), (19.8, 9.2), (19.8, 5.4)]))


# ------------------------------------------------------------- navigation
def arrow_down(p, fill=False):
    return turned(arrow_up(p), 180)


def file_add(p, fill=False):
    return _corner(p, file(p), _sign_plus())


def share(p, fill=False):
    """Three nodes, one sending to two: never the upload tray."""
    r = 2.6
    a, b, c = (17.2, 18.0), (6.8, 12.0), (17.2, 6.0)

    def link(u, v):
        d = (v[0] - u[0], v[1] - u[1])
        n = math.hypot(*d)
        k = (d[0] / n, d[1] / n)
        return p.bar((u[0] + k[0] * r, u[1] + k[1] * r), (v[0] - k[0] * r, v[1] - k[1] * r), cut="p")

    return union(*(p.ring(*q, r) for q in (a, b, c)), link(b, a), link(b, c))


def _marquee(p):
    """A dashed selection frame: corners and one dash per side."""
    x0, y0, x1, y1 = 4.0, 4.0, 20.0, 20.0
    frame = p.rect(x0, y0, x1, y1, r=p.radius_small)
    g = 1.1 + p.h * 0.3
    cuts = []
    for t in (1 / 3, 2 / 3):
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        cuts += [box(x - g, -BIG, x + g, BIG), box(-BIG, y - g, BIG, y + g)]
    return minus(frame, union(*cuts))


def check_none(p, fill=False):
    return _marquee(p)


def check_invert(p, fill=False):
    return union(_marquee(p), p.rect_solid(8.2, 8.2, 12.0, 15.8, r=0))


def history_clear(p, fill=False):
    return _corner(p, history(p), _sign_x())


def clear_all(p, fill=False):
    lines = union(p.bar((LO, 18.4), (HI, 18.4)), p.bar((LO, 12.6), (HI, 12.6)), p.bar((LO, 6.8), (11.6, 6.8)))
    return _corner(p, lines, _sign_x())


def bell_dot(p, fill=False):
    """The freedesktop-style "new notification" glyph.  An unread count stays
    with the interface, on top of ``bell``."""
    return _badge(p, bell(p), _sign_dot((18.4, 17.8), 2.4))


# -------------------------------------------------------------- input, net
def keyboard_virtual(p, fill=False):
    """The keyboard on the screen: raised, with the hide chevron under it."""
    body = (LO, 9.6, HI, 20.6)
    keys = union(*(p.dot(x, 17.2) for x in (7.2, 12.0, 16.8)), p.bar((8.4, 13.2), (15.6, 13.2)))
    chevron = p.line([(9.0, 6.2), (12, 3.4), (15.0, 6.2)])
    return union(p.rect(*body), keys, chevron)


def keyboard_virtual_off(p, fill=False):
    return _crossed(p, keyboard_virtual(p))


_PLANE = [(12, 21.0), (13.8, 18.8), (13.8, 13.8), (20.8, 9.4), (20.8, 7.2), (13.8, 9.4), (13.8, 6.2), (16.4, 4.2),
          (16.4, 3.0), (12, 4.2), (7.6, 3.0), (7.6, 4.2), (10.2, 6.2), (10.2, 9.4), (3.2, 7.2), (3.2, 9.4), (10.2, 13.8),
          (10.2, 18.8)]


def airplane(p, fill=False):
    return (p.solid if fill else p.frame)(_PLANE, r=0.7)


def airplane_off(p, fill=False):
    return _crossed(p, airplane(p))


def vpn(p, fill=False):
    return _corner(p, globe(p), _sign_locked)


# ------------------------------------------------------------ updates, power
def update_available(p, fill=False):
    return _badge(p, update(p), _sign_dot())


def update_important(p, fill=False):
    """The solid update disc: weight, not a cramped "!" in the ring."""
    return update(p, True)


def restart_update(p, fill=False):
    return _badge(p, restart(p), _sign_dot())


def power_update(p, fill=False):
    return _badge(p, power(p), _sign_dot())


def power_save(p, fill=False):
    """A leaf: two arcs meeting at the tips, a midrib that runs on as the stem."""
    d, r = 5.2, 8.6
    c1, c2 = (12 + d, 12), (12 - d, 12)
    k = p.k.circle
    a1 = p.arc(*c1, r, keep=region(superellipse(*c2, r, r, k)))
    a2 = p.arc(*c2, r, keep=region(superellipse(*c1, r, r, k)))
    tip = math.sqrt(r * r - d * d)
    rib = p.bar((12, 12 - tip - 3.0), (12, 12 + tip * 0.45), cut="p")
    return turned(union(a1, a2, rib), -45)


_ZAP = [(13.6, 21.0), (5.2, 10.8), (11.0, 10.8), (9.8, 3.0), (18.8, 13.6), (12.8, 13.6)]


def power_performance(p, fill=False):
    """A full-height bolt: energy at its highest (the small bolt inside the
    battery means charging)."""
    return (p.solid if fill else p.frame)(_ZAP, r=0.8)


def moon_off(p, fill=False):
    """The moon turned to face the other way: the slash runs along the line
    between the horns of ``moon`` and would trim both to spikes, so here it
    crosses the bite and the body instead."""
    return _crossed(p, mirrored(moon(p)))


def microphone_active(p, fill=False):
    return microphone(p, True)


def audio_active(p, fill=False):
    return volume(p, True)


# ----------------------------------------------------------------- windows
def window_new(p, fill=False):
    return _corner(p, window_maximize(p), _sign_plus())


def fullscreen(p, fill=False):
    a, b, n = 3.4, 20.6, 6.0
    return union(
        p.line([(a, a + n), (a, a), (a + n, a)]), p.line([(b - n, a), (b, a), (b, a + n)]),
        p.line([(b, b - n), (b, b), (b - n, b)]), p.line([(a + n, b), (a, b), (a, b - n)]),
    )


def _tab(p, strip=14.4, split=11.0):
    """A window with its tab strip: the open tab runs into the page."""
    frame = p.rect(LO, 3.4, HI, 20.6, r=p.radius_small)
    return union(frame, p.bar((split, strip), (HI, strip), cut="p"), p.bar((split, strip), (split, 20.6), cut="p"))


def tab(p, fill=False):
    return _tab(p)


def tab_new(p, fill=False):
    return _corner(p, _tab(p), _sign_plus())


def tab_close(p, fill=False):
    return _corner(p, _tab(p), _sign_x())


def tab_detach(p, fill=False):
    return _corner(p, _tab(p), _sign_out)


def tab_close_other(p, fill=False):
    """The other tab is filled and the cross is cut out of it; a cross drawn
    in ink on that strip closes up into an hourglass from Medium."""
    split, strip, top = 11.0, 14.4, 20.6
    other = clip(p.rect_solid(LO, 3.4, HI, top, r=p.radius_small), box(split, strip))
    cx, cy, s = (split + HI) / 2, (strip + top) / 2, 1.8
    q = p.stroked(0.75 * p.w)
    x = union(q.bar((cx - s, cy - s), (cx + s, cy + s)), q.bar((cx - s, cy + s), (cx + s, cy - s)))
    return minus(union(_tab(p), other), x)


# ------------------------------------------------------------ files, lists
def folder_lock(p, fill=False):
    return _corner(p, folder(p), _sign_locked)


def folder_unlock(p, fill=False):
    return _corner(p, folder(p), _sign_unlocked)


def show_in_folder(p, fill=False):
    """An open folder: the front flap tilts away from the back."""
    rs = p.radius_small
    back = p.line([(17.8, 11.8), (17.8, 16.2), (12.4, 16.2), (10.4, 18.8), (LO, 18.8), (LO, 4.4)], corners={1: rs, 2: rs, 3: rs, 4: rs})
    flap = p.frame([(LO, 4.4), (17.2, 4.4), (21.0, 11.8), (6.6, 11.8)], r=rs)
    return union(back, flap)


_CLOUD = [((7.4, 9.6), 3.8), ((12.4, 12.2), 5.6), ((17.0, 9.6), 4.0)]
_CLOUD_BASE = 5.8


def _cloud_region(p, grow):
    parts = [region(superellipse(cx, cy, r + grow, r + grow, p.k.circle)) for (cx, cy), r in _CLOUD]
    return union(*parts, box(7.4, _CLOUD_BASE - grow, 17.0, 9.6))


def cloud(p, fill=False):
    outer = _cloud_region(p, p.h)
    return outer if fill else minus(outer, _cloud_region(p, -p.h))


def cloud_upload(p, fill=False):
    def arrow(q):
        return union(q.bar((12, 2.9), (12, 12.6), cut=("h", "p")), q.line([(9.0, 9.6), (12, 12.6), (15.0, 9.6)]))

    return union(minus(cloud(p), arrow(p.stroked(p.w + 2 * _gap(p)))), arrow(p))


def tag(p, fill=False):
    pts = [(3.4, 12.0), (8.8, 18.2), (20.6, 18.2), (20.6, 5.8), (8.8, 5.8)]
    rs = p.radius_small
    corners = {0: 1.0, 1: rs, 2: rs, 3: rs, 4: rs}
    if fill:
        return minus(p.solid(pts, corners=corners), p.stroked(1.6 * p.w).dot(9.6, 12))
    return union(p.frame(pts, corners=corners), p.dot(9.6, 12))


def sort_(p, fill=False):
    """Up and down side by side: sort, no direction chosen yet."""
    up = union(p.bar((7.6, 4.4), (7.6, 19.6), cut=("h", "p")), p.line([(4.2, 16.2), (7.6, 19.6), (11.0, 16.2)]))
    down = union(p.bar((16.4, 19.6), (16.4, 4.4), cut=("h", "p")), p.line([(13.0, 7.8), (16.4, 4.4), (19.8, 7.8)]))
    return union(up, down)


def group(p, fill=False):
    """A bracket holding three items together."""
    rs = p.radius_small
    bracket = p.line([(7.8, 19.6), (4.4, 19.6), (4.4, 4.4), (7.8, 4.4)], corners={1: rs, 2: rs})
    items = union(*(p.bar((10.8, y), (HI, y)) for y in (17.0, 12.0, 7.0)))
    return union(bracket, items)


def drag_handle(p, fill=False):
    return union(*(p.dot(x, y, big=True) for x in (9.0, 15.0) for y in (6.0, 12.0, 18.0)))


DESKTOP_ICONS = [
    Icon("arrow-down", arrow_down, "Navigation", "arrow-down", meaning="Down arrow", since=V5),
    Icon("file-add", file_add, "Documents", "file-plus", meaning="New document", since=V5),
    Icon("share", share, "Documents", "share-2", meaning="Share", since=V5),
    Icon("check-none", check_none, "Files · actions", "square-dashed", meaning="Deselect all", since=V5),
    Icon("check-invert", check_invert, "Files · actions", "", meaning="Invert selection", since=V5),
    Icon("history-clear", history_clear, "Files · actions", "", meaning="Clear history", since=V5),
    Icon("clear-all", clear_all, "Notifications", "list-x", meaning="Clear all", since=V5),
    Icon("bell-dot", bell_dot, "Notifications", "bell-dot", "", "", "status", meaning="New notification (dotted bell)", since=V5,
         note="Precomposed unread dot; counts stay with the interface, on top of bell."),
    Icon("keyboard-virtual", keyboard_virtual, "Input", "", "", "", "devices", meaning="Virtual keyboard on", since=V5),
    Icon("keyboard-virtual-off", keyboard_virtual_off, "Input", "", "", "", "devices", meaning="Virtual keyboard off", since=V5),
    Icon("airplane", airplane, "Network", "plane", "", "", "status", meaning="Airplane mode on", since=V5),
    Icon("airplane-off", airplane_off, "Network", "", "", "", "status", meaning="Airplane mode off", since=V5),
    Icon("vpn", vpn, "Network", "", "", "", "status", meaning="Virtual private network (VPN)", since=V5),
    Icon("update-available", update_available, "Apps", "", "", "", "status", meaning="Update available", since=V5),
    Icon("update-important", update_important, "Apps", "", "", "", "status", meaning="Important or security update available", since=V5,
         note="The solid disc of update; not a -fill variant for a selected state."),
    Icon("restart-update", restart_update, "Session and power", "", meaning="Update and restart", since=V5,
         note="The corner dot means \"update available\", as in update-available."),
    Icon("power-update", power_update, "Session and power", "", meaning="Update and shut down", since=V5),
    Icon("power-save", power_save, "Battery", "leaf", "", "", "status", meaning="Power saver mode", since=V5),
    Icon("power-performance", power_performance, "Battery", "zap", "", "", "status", meaning="High performance mode", since=V5,
         note="A large bolt; the small bolt inside a battery means charging."),
    Icon("moon-off", moon_off, "Display", "", "", "", "status", meaning="Night light off", since=V5),
    Icon("microphone-active", microphone_active, "Sound", "", "", "", "status", meaning="Microphone in use", since=V5),
    Icon("audio-active", audio_active, "Sound", "", "", "", "status", meaning="Audio is being recorded", since=V5),
    Icon("window-new", window_new, "Windows", "", meaning="New window", since=V5),
    Icon("fullscreen", fullscreen, "Windows", "maximize", meaning="Full screen", since=V5, note="Four corners; unlike window-maximize."),
    Icon("tab", tab, "Windows", "", meaning="Tab", since=V5),
    Icon("tab-new", tab_new, "Windows", "", meaning="New tab", since=V5),
    Icon("tab-close", tab_close, "Windows", "", meaning="Close tab", since=V5),
    Icon("tab-detach", tab_detach, "Windows", "", meaning="Move tab to a new window", since=V5),
    Icon("tab-close-other", tab_close_other, "Windows", "", meaning="Close other tabs", since=V5),
    Icon("folder-lock", folder_lock, "Files · extended", "folder-lock", "", "", "places", meaning="Encrypted folder, locked", since=V5),
    Icon("folder-unlock", folder_unlock, "Files · extended", "", "", "", "places", meaning="Encrypted folder, unlocked", since=V5),
    Icon("show-in-folder", show_in_folder, "Files · extended", "folder-open", meaning="Open containing folder", since=V5),
    Icon("cloud", cloud, "Files · extended", "cloud", "", "", "places", meaning="Cloud", since=V5),
    Icon("cloud-upload", cloud_upload, "Files · extended", "cloud-upload", meaning="Upload to cloud", since=V5),
    Icon("tag", tag, "Files · extended", "tag", fill=True, meaning="Tag", since=V5),
    Icon("sort", sort_, "Files · extended", "arrow-up-down", meaning="Sort (no direction chosen)", since=V5),
    Icon("group", group, "Files · extended", "", meaning="Group items", since=V5),
    Icon("drag-handle", drag_handle, "Navigation", "grip-vertical", meaning="Drag handle for reordering", since=V5),
]
