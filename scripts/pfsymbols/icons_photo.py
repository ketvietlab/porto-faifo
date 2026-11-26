"""Porto Faifo Symbols recipes: photo viewing and editing.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import HI, LO, Icon, _at, _u, edit, image
from .icons_business import _star
from .icons_desktop import _crossed
from .icons_system import _badged, _head, eye
from .kit import box, clip, minus, mirrored, turned, union

V8 = "0.8.0"
PHOTO = "Photos"
NAV = "Navigation"


# ------------------------------------------------------------------ rotate
def rotate_right(p, fill=False):
    """A picture with a quarter turn over its top right: rotate 90° clockwise."""
    c, r = (8.4, 9.4), 9.4
    picture = (p.rect_solid if fill else p.rect)(LO, 3.4, 12.4, 12.9, r=p.radius_small)
    turn = p.arc(*c, r, keep=box(x0=c[0], y0=c[1]))
    return union(picture, turn, _head(p, (c[0] + r, c[1]), (0.0, -1.0), s=2.6))


def rotate_left(p, fill=False):
    return mirrored(rotate_right(p, fill))


# -------------------------------------------------------------------- flip
def flip_horizontal(p, fill=False):
    """Two triangles pointing at a broken axis: mirror left to right.  The
    axis breaks where the tips are, so they keep a clear gap at Bold."""
    tri = [(3.4, 6.6), (9.4, 12.0), (3.4, 17.4)]
    shape = p.solid if fill else p.frame
    left = shape(tri, corners={0: p.radius_small, 1: p.radius_small, 2: p.radius_small})
    axis = union(p.bar((12, 20.6), (12, 16.2), cut="h"), p.bar((12, 7.8), (12, 3.4), cut="h"))
    return union(left, mirrored(left), axis)


def flip_vertical(p, fill=False):
    return turned(flip_horizontal(p, fill), 90)


# -------------------------------------------------------------- transforms
def crop(p, fill=False):
    """Two crop marks crossing: the kept frame between them."""
    return union(p.line([(6.6, 20.6), (6.6, 6.6), (20.6, 6.6)], cut=("h", "v")),
                 p.line([(3.4, 17.4), (17.4, 17.4), (17.4, 3.4)], cut=("v", "h")))


def resize(p, fill=False):
    """A small picture, the open frame it grows to and the arrow between."""
    s = p.radius_small
    small = (p.rect_solid if fill else p.rect)(LO, LO, 11.0, 11.0, r=s)
    frame = p.line([(LO, 14.8), (LO, HI), (HI, HI), (HI, LO), (14.8, LO)], cut="p", corners={1: s, 2: p.radius, 3: s})
    tip = 16.4
    arrow = union(p.bar((13.6, 13.6), (tip, tip), cut=("h", "p")), p.line([(tip - 4.0, tip), (tip, tip), (tip, tip - 4.0)]))
    return union(small, frame, arrow)


# -------------------------------------------------------------------- zoom
def zoom_fit(p, fill=False):
    """The picture inside the four corners of the view: fit to the window."""
    a, b, n = 3.4, 20.6, 5.4
    corners = union(
        p.line([(a, a + n), (a, a), (a + n, a)]), p.line([(b - n, a), (b, a), (b, a + n)]),
        p.line([(b, b - n), (b, b), (b - n, b)]), p.line([(a + n, b), (a, b), (a, b - n)]),
    )
    return union(corners, (p.rect_solid if fill else p.rect)(8.4, 8.6, 15.6, 15.4, r=p.radius_small))


def zoom_original(p, fill=False):
    """1:1, the actual pixels, drawn with the pen rather than set in type."""
    def one(x):
        return p.line([(x - 2.6, 17.2), (x, 19.8), (x, 4.2)], cut=("p", "h"), corners={1: 0.6})

    return union(one(7.4), one(19.0), p.dot(12.6, 8.6, big=True), p.dot(12.6, 15.0, big=True))


# -------------------------------------------------------------- navigation
def go_first(p, fill=False):
    """A stop bar and a chevron toward it: the first picture."""
    return union(p.bar((5.6, 18.6), (5.6, 5.4), cut="h"), p.line([(16.8, 18.6), (10.2, 12.0), (16.8, 5.4)]))


def go_last(p, fill=False):
    return mirrored(go_first(p, fill))


def sidetree(p, fill=False):
    """A window with a sidebar holding a two-level list: the folder tree."""
    s = p.radius_small
    window = p.rect(LO, 3.9, HI, 20.1, r=s)
    divider = p.bar((10.4, 20.1), (10.4, 3.9), cut="h")
    rows = union(p.bar((5.6, 15.8), (7.8, 15.8)), p.bar((6.8, 11.8), (7.8, 11.8)), p.bar((6.8, 7.8), (7.8, 7.8)))
    return union(window, divider, rows)


def navigator(p, fill=False):
    """The whole picture and the part on screen: the zoom navigator."""
    s = p.radius_small
    outer = p.rect(LO, 3.9, HI, 20.1, r=s)
    view = (p.rect_solid if fill else p.rect)(10.6, 8.6, 17.4, 15.4, r=s)
    return union(outer, view)


# ---------------------------------------------------------------- bookmark
RIBBON = [(5.8, 3.4), (5.8, 20.6), (18.2, 20.6), (18.2, 3.4), (12.0, 8.4)]


def _ribbon(p, fill):
    corners = {0: 0.6, 1: p.radius, 2: p.radius, 3: 0.6, 4: 0.8}
    return (p.solid if fill else p.frame)(RIBBON, corners=corners)


def bookmark(p, fill=False):
    return _ribbon(p, fill)


def bookmark_add(p, fill=False):
    c, s = (12.0, 15.0), 2.6
    plus_ = union(p.bar((c[0], c[1] - s), (c[0], c[1] + s)), p.bar((c[0] - s, c[1]), (c[0] + s, c[1])))
    if fill:
        return minus(_ribbon(p, True), p.stroked(p.w).bar((c[0], c[1] - s), (c[0], c[1] + s)),
                     p.stroked(p.w).bar((c[0] - s, c[1]), (c[0] + s, c[1])))
    return union(_ribbon(p, False), plus_)


# ------------------------------------------------------------------- edits
def _sparkle(p, c=(16.8, 7.4), big=3.6):
    """The corner sign for a fix the app makes for you."""
    pts = _star(c, big, 0)
    return p.solid(pts, corners={i: (0.4 if i % 2 == 0 else p.radius_small) for i in range(8)})


def _pencil(p, tip=(11.8, 3.4), length=10.8, hw=2.0):
    """A solid pencil at 45°, the corner sign for "edit"."""
    u, n = _u(45), _u(135)
    b, e = _at(tip, u, 3.4), _at(tip, u, length)
    pts = [tip, _at(b, n, -hw), _at(e, n, -hw), _at(e, n, hw), _at(b, n, hw)]
    return p.solid(pts, corners={0: 0.4, 1: 0, 2: p.radius_small, 3: p.radius_small, 4: 0})


def redeyes(p, fill=False):
    """An eye with the sparkle of a fix: red-eye removal."""
    return _badged(p, eye(p, fill), lambda q: _sparkle(q))


def restoration(p, fill=False):
    """A picture with the sparkle of a fix: restore or clean up a photo."""
    return _badged(p, image(p, fill), lambda q: _sparkle(q))


def edit_image(p, fill=False):
    """A picture with a pencil in its corner: edit the image."""
    return _badged(p, image(p, fill), lambda q: _pencil(q))


def edit_none(p, fill=False):
    """The pencil crossed out, the ``-off`` rule: no edit tool."""
    return _crossed(p, edit(p))


def contrast(p, fill=False):
    """A circle half dark, half light."""
    from .icons import R

    return union(p.ring(12, 12, R), clip(p.disc(12, 12, R), box(x1=12)))


PHOTO_ICONS = [
    Icon("rotate-left", rotate_left, PHOTO, "rotate-ccw-square", "object-rotate-left", "spec", fill=True,
         meaning="Rotate left 90°", since=V8, note="Unlike undo: a photo and a quarter turn."),
    Icon("rotate-right", rotate_right, PHOTO, "rotate-cw-square", "object-rotate-right", "spec", fill=True,
         meaning="Rotate right 90°", since=V8),
    Icon("flip-horizontal", flip_horizontal, PHOTO, "flip-horizontal-2", "object-flip-horizontal", "spec", fill=True,
         meaning="Flip horizontally", since=V8, note="The axis breaks at the two triangle tips so a gap remains at Bold."),
    Icon("flip-vertical", flip_vertical, PHOTO, "flip-vertical-2", "object-flip-vertical", "spec", fill=True,
         meaning="Flip vertically", since=V8),
    Icon("crop", crop, PHOTO, "crop", "transform-crop", "kde", meaning="Crop image", since=V8),
    Icon("resize", resize, PHOTO, "scaling", "transform-scale", "kde", fill=True, meaning="Resize image", since=V8),
    Icon("zoom-fit", zoom_fit, PHOTO, "scan", "zoom-fit-best", "spec", fill=True, meaning="Fit to frame", since=V8,
         note="Unlike fullscreen: a picture inside four corners."),
    Icon("zoom-original", zoom_original, PHOTO, "", "zoom-original", "spec", meaning="Actual size 1:1", since=V8),
    Icon("go-first", go_first, NAV, "chevron-first", "go-first", "spec", meaning="First (first image)", since=V8),
    Icon("go-last", go_last, NAV, "chevron-last", "go-last", "spec", meaning="Last (last image)", since=V8),
    Icon("sidetree", sidetree, PHOTO, "panel-left", "view-sidetree", "kde", meaning="Sidebar folder tree", since=V8),
    Icon("navigator", navigator, PHOTO, "", "image-navigator", "kde", fill=True, meaning="Navigator frame while zoomed", since=V8),
    Icon("bookmark", bookmark, PHOTO, "bookmark", fill=True, meaning="Bookmarks", since=V8),
    Icon("bookmark-add", bookmark_add, PHOTO, "bookmark-plus", "bookmark-new", "spec", fill=True, meaning="Add bookmark", since=V8),
    Icon("redeyes", redeyes, PHOTO, "", "redeyes", "kde", meaning="Red-eye removal", since=V8),
    Icon("restoration", restoration, PHOTO, "", "restoration", "kde", meaning="Retouch, clean up a photo", since=V8),
    Icon("contrast", contrast, PHOTO, "contrast", "contrast", "kde", meaning="Contrast", since=V8),
    Icon("edit-image", edit_image, PHOTO, "image-pen", "edit-image", "kde", meaning="Edit photo", since=V8),
    Icon("edit-none", edit_none, PHOTO, "pencil-off", "edit-none", "kde", meaning="No editing, deselect the tool", since=V8),
]
