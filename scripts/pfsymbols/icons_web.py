"""Porto Faifo Symbols recipes: web browser.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import Icon, lock
from .icons_desktop import _crossed
from .kit import union

V9 = "0.9.0"
WEB = "Browser"


def browser_private(p, fill=False):
    """A hat and dark glasses: browsing incognito.  Not ``eye-off``, which
    means hide or show; this is a window that keeps no history."""
    s = p.radius_small
    shape = p.solid if fill else p.frame
    crown = shape([(6.2, 13.4), (7.6, 19.8), (16.4, 19.8), (17.8, 13.4)], corners={0: 0, 1: s, 2: s, 3: 0})
    brim = p.bar((3.0, 13.4), (21.0, 13.4))
    lens = p.disc if fill else p.ring
    glasses = union(lens(7.6, 6.6, 3.1), lens(16.4, 6.6, 3.1), p.bar((10.7, 7.0), (13.3, 7.0), cut="v"))
    return union(crown, brim, glasses)


def site_not_secure(p, fill=False):
    """The padlock struck through: this page is not protected.  ``unlock``
    is the action of opening a lock and ``warning`` says nothing about the
    connection, so neither stands in for it."""
    return _crossed(p, lock(p, fill))


WEB_ICONS = [
    Icon("browser-private", browser_private, WEB, "hat-glasses", "view-private", "kde", fill=True,
         meaning="Private browsing (incognito)", since=V9, note="Unlike eye-off (show/hide): hat and glasses, a window that keeps no history."),
    Icon("site-not-secure", site_not_secure, WEB, "lock-open", "security-low", "kde", "status", fill=True,
         meaning="Insecure connection (HTTP)", since=V9, note="A padlock struck through, following the -off rule; unlike unlock (an action) and warning."),
]
