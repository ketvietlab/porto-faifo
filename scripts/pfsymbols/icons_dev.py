"""Porto Faifo Symbols recipes: developer tools: panes, keys, agent states and Git.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import FILE, HI, LO, R, Icon, file, panel_right
from .icons_system import _head
from .kit import BIG, box, minus, mirrored, turned, union

V10 = "0.10.0"
KP = "Developer tools"


# ------------------------------------------------------------------ panes
def panel_left(p, fill=False):
    """``panel-right`` mirrored: the pane on the left (the sidebar)."""
    return mirrored(panel_right(p, fill))


def panel_right_close(p, fill=False):
    """The window with its right pane and a chevron pushing it shut."""
    return union(panel_right(p), p.line([(7.6, 15.4), (11.0, 12.0), (7.6, 8.6)]))


def panels_top_left(p, fill=False):
    """A window with a top bar and a left pane under it: the full layout."""
    x0, y0, x1, y1, bar, side = LO, 3.9, HI, 20.1, 15.2, 8.8
    return union(p.rect(x0, y0, x1, y1), p.bar((x0, bar), (x1, bar), cut="p"), p.bar((side, bar), (side, y0), cut="p"))


# ------------------------------------------------------------------ keys
def chevron_up_down(p, fill=False):
    """Two chevrons back to back: a menu that opens either way (a select)."""
    return union(p.line([(7.4, 14.4), (12.0, 19.0), (16.6, 14.4)]), p.line([(7.4, 9.6), (12.0, 5.0), (16.6, 9.6)]))


def enter(p, fill=False):
    """The Enter key: down from the top right, a turn, out to the left."""
    y = 9.0
    return union(p.line([(19.4, 19.6), (19.4, y), (4.6, y)], cut=("h", "p"), corners={1: 3.6}),
                 p.line([(9.8, y + 5.2), (4.6, y), (9.8, y - 5.2)]))


def slash(p, fill=False):
    """The / key, cut level like the slash of ``code``."""
    return p.bar((16.4, 20.2), (7.6, 3.8), cut="h")


def command(p, fill=False):
    """The ⌘ key: a square whose four corners loop out in three-quarter rings."""
    a, b, r = 6.6, 17.4, 2.8
    lines = union(p.bar((a + r, a), (a + r, b), cut="p"), p.bar((b - r, a), (b - r, b), cut="p"),
                  p.bar((a, a + r), (b, a + r), cut="p"), p.bar((a, b - r), (b, b - r), cut="p"))
    loops = []
    for cx, cy in ((a, a), (a, b), (b, a), (b, b)):
        inner = box(cx, cy, BIG, BIG) if (cx, cy) == (a, a) else box(cx, -BIG, BIG, cy) if (cx, cy) == (a, b) \
            else box(-BIG, cy, cx, BIG) if (cx, cy) == (b, a) else box(-BIG, -BIG, cx, cy)
        loops.append(p.arc(cx, cy, r, keep=minus(box(), inner)))
    return union(lines, *loops)


# ------------------------------------------------------------------ agents
def chats(p, fill=False):
    """Two square bubbles, one behind the other: conversations between
    agents.  ``chat`` is one round bubble."""
    s = p.radius_small
    front = [(LO, 7.4), (6.8, 11.2), (15.2, 11.2), (15.2, HI), (LO, HI)]
    back = [(18.0, 15.2), (HI, 15.2), (HI, LO), (16.8, 6.8), (9.8, 6.8), (9.8, 8.4)]
    bubble = (p.solid if fill else p.frame)(front, corners={0: 0.6, 1: 0, 2: s, 3: s, 4: s})
    return union(bubble, p.line(back, cut=("p", "h"), corners={1: s, 2: 0.6, 3: 0, 4: s}))


def compose(p, fill=False):
    """A sheet open at the top right and a pencil writing into it: a new
    conversation.  ``edit`` is the pencil alone."""
    r = p.radius
    sheet = p.line([(11.4, 20.2), (3.8, 20.2), (3.8, 3.8), (20.2, 3.8), (20.2, 11.4)], corners={1: r, 2: r, 3: r})
    tip, hw, n = (9.4, 9.4), 2.2, (-0.7071, 0.7071)
    u = (0.7071, 0.7071)
    at = lambda q, d, t: (q[0] + d[0] * t, q[1] + d[1] * t)  # noqa: E731
    b, e = at(tip, u, 3.4), at(tip, u, 13.4)
    pts = [tip, at(b, n, -hw), at(e, n, -hw), at(e, n, hw), at(b, n, hw)]
    corners = {0: 0.5, 1: 0, 2: p.radius_small, 3: p.radius_small, 4: 0}
    pencil = (p.solid if fill else p.frame)(pts, corners=corners)
    return union(sheet, pencil)


def pause_circle(p, fill=False):
    """Paused or held: the two bars of ``pause`` in the status ring."""
    bars = union(p.bar((9.8, 8.4), (9.8, 15.6), cut="h"), p.bar((14.2, 8.4), (14.2, 15.6), cut="h"))
    if fill:
        return minus(p.disc(12, 12, R), bars)
    return union(p.ring(12, 12, R), bars)


def stop_circle(p, fill=False):
    """Stop the turn: a small square in the status ring."""
    square = p.rect_solid(9.2, 9.2, 14.8, 14.8, r=p.radius_small)
    if fill:
        return minus(p.disc(12, 12, R), square)
    return union(p.ring(12, 12, R), square)


def loading(p, fill=False):
    """Running: three quarters of the status ring, the open quarter at the
    top right, spun by the app.  Its ends are cut on the grid."""
    return p.arc(12, 12, R, keep=minus(box(), box(12, 12, BIG, BIG)))


# ------------------------------------------------------------------ files and Git
def folder_open(p, fill=False):
    """The folder with its front tipped forward: the open folder."""
    s = p.radius_small
    back = p.line([(18.4, 11.6), (18.4, 16.2), (12.4, 16.2), (10.4, 18.8), (LO, 18.8), (LO, 4.4)],
                  cut=("p", "h"), corners={1: s, 2: s, 3: s, 4: p.radius})
    front = [(LO, 4.4), (17.6, 4.4), (HI, 11.6), (6.8, 11.6)]
    return union(back, (p.solid if fill else p.frame)(front, corners={0: p.radius, 1: s, 2: s, 3: s}))


def file_code(p, fill=False):
    """The sheet with the chevrons of ``code`` on it: source code."""
    marks = union(p.line([(10.6, 13.0), (8.0, 10.2), (10.6, 7.4)]), p.line([(13.4, 13.0), (16.0, 10.2), (13.4, 7.4)]))
    if fill:
        return minus(file(p, True), marks)
    return union(file(p), marks)


GIT_R = 2.4  # commit ring; a smaller ring and head keep compare open at 16 px


def _git_end(p, ring, shaft, tip, d):
    return union(p.ring(*ring, GIT_R), p.line(shaft, cut=("p", "p"), corners={1: 3.0}), _head(p, tip, d, s=2.6))


def compare(p, fill=False):
    """Two commits, each sending an arrow round to the other: compare the
    changes (Source Control).  Turned 180° it is the same drawing."""
    half = _git_end(p, (6.0, 17.6), [(6.0, 17.6 - GIT_R), (6.0, 6.4), (12.6, 6.4)], (12.6, 6.4), (1.0, 0.0))
    return union(half, turned(half, 180))


def pull_request(p, fill=False):
    """The branch line on the left; on the right a commit whose line turns
    back towards it with an arrow: a request to merge."""
    left = union(p.ring(6.0, 17.6, GIT_R), p.bar((6.0, 17.6 - GIT_R), (6.0, LO), cut=("p", "h")))
    right = _git_end(p, (18.0, 6.4), [(18.0, 6.4 + GIT_R), (18.0, 17.6), (11.4, 17.6)], (11.4, 17.6), (-1.0, 0.0))
    return union(left, right)


def map_(p, fill=False):
    """A folded map in three panels, the folds standing on the zigzag."""
    s = p.radius_small
    pts = [(3.4, 3.2), (9.0, 5.6), (15.0, 3.2), (20.6, 5.6), (20.6, 20.8), (15.0, 18.4), (9.0, 20.8), (3.4, 18.4)]
    out = (p.solid if fill else p.frame)(pts, corners={i: s for i in range(len(pts))})
    folds = union(p.bar((9.0, 5.6), (9.0, 20.8), cut="p"), p.bar((15.0, 3.2), (15.0, 18.4), cut="p"))
    return minus(out, folds) if fill else union(out, folds)


# ------------------------------------------------------------------ account and status
def log_in(p, fill=False):
    """``log-out`` turned round: the door on the right, the arrow going in."""
    door = p.line([(13.4, 20.2), (20.1, 20.2), (20.1, 3.8), (13.4, 3.8)], corners={1: p.radius, 2: p.radius})
    arrow = union(p.bar((3.9, 12), (15.2, 12), cut=("v", "p")), p.line([(10.6, 16.6), (15.2, 12), (10.6, 7.4)]))
    return union(door, arrow)


def circle(p, fill=False):
    """The status ring alone (idle, unknown); filled, a status lamp."""
    return (p.disc if fill else p.ring)(12, 12, R)


def dot(p, fill=False):
    """One status dot, 4.4 across (Lucide's r 1 under a 2-unit stroke)."""
    return p.disc(12, 12, 2.2)


DEV_ICONS = [
    Icon("panel-left", panel_left, KP, "panel-left", fill=True, meaning="Toggle the left pane (sidebar)", since=V10,
         note="panel-right mirrored."),
    Icon("panel-right-close", panel_right_close, KP, "panel-right-close", meaning="Close the right pane", since=V10),
    Icon("panels-top-left", panels_top_left, KP, "panels-top-left", meaning="Layout: top bar and left pane", since=V10),
    Icon("chevron-up-down", chevron_up_down, KP, "chevrons-up-down", meaning="Choose from a menu (select)", since=V10,
         note="Two chevrons back to back; unlike sort (two arrows)."),
    Icon("enter", enter, KP, "corner-down-left", meaning="Enter key", since=V10),
    Icon("slash", slash, KP, "slash", meaning="Slash key (quick commands)", since=V10),
    Icon("command", command, KP, "command", meaning="⌘ key (keyboard shortcuts)", since=V10),
    Icon("chats", chats, KP, "messages-square", fill=True, meaning="Conversations between agents", since=V10,
         note="Two overlapping square bubbles; chat is one round bubble."),
    Icon("compose", compose, KP, "square-pen", fill=True, meaning="New conversation", since=V10,
         note="A sheet with an open corner and a pen; edit is the pen alone."),
    Icon("pause-circle", pause_circle, KP, "pause-circle", fill=True, meaning="Pending or on hold", since=V10),
    Icon("stop-circle", stop_circle, KP, "circle-stop", fill=True, meaning="Stop the turn", since=V10,
         note="A square inside a status ring; stop is the square alone."),
    Icon("loading", loading, KP, "loader-circle", "process-working", "spec", "status", meaning="Running (rotated by the app)", since=V10,
         note="Three quarters of a status ring; the app spins it about 12,12."),
    Icon("folder-open", folder_open, KP, "folder-open", "folder-open", "spec", "status", fill=True, meaning="Open folder", since=V10),
    Icon("file-code", file_code, KP, "file-code", "text-x-script", "spec", "mimetypes", fill=True, meaning="Source code file", since=V10),
    Icon("compare", compare, KP, "git-compare-arrows", meaning="Compare changes (source control)", since=V10),
    Icon("pull-request", pull_request, KP, "git-pull-request", meaning="Pull request", since=V10),
    Icon("map", map_, KP, "map", fill=True, meaning="Map", since=V10, note="Unlike map-pin (a single place)."),
    Icon("log-in", log_in, KP, "log-in", meaning="Log in", since=V10, note="log-out turned around."),
    Icon("circle", circle, KP, "circle", fill=True, meaning="Status: ring (idle); filled is the status light", since=V10),
    Icon("dot", dot, KP, "dot", meaning="Status: a single dot", since=V10),
]
