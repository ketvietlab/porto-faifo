"""Porto Faifo Symbols recipes: telephony.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import LO, HI, Icon, user
from .icons_business import TALK, phone
from .icons_desktop import _corner, _sign_x
from .kit import minus, union

V12 = "0.12.0"
INPUT = "Input"
ACCOUNT = "Account and security"

# the key cap of keyboard: 13.2 tall, between the 5.4 and 18.6 lines
KEY_Y0, KEY_Y1 = 5.4, 18.6


def backspace(p, fill=False):
    """The erase key: a key cap with its left end drawn to a point, an
    ``x`` in it.  Not ``trash`` (delete a thing): this takes back the last
    character typed, as on a phone keypad."""
    cap = [(LO, 12.0), (8.4, KEY_Y1), (HI, KEY_Y1), (HI, KEY_Y0), (8.4, KEY_Y0)]
    corners = {0: p.radius_small, 1: p.radius_small, 2: p.radius, 3: p.radius, 4: p.radius_small}
    x = _sign_x((14.4, 12.0), 2.8)(p)
    if fill:
        return minus(p.solid(cap, corners=corners), x)
    return union(p.frame(cap, corners=corners), x)


def phone_missed(p, fill=False):
    """The handset with an ``x`` where phone-incoming and phone-outgoing put
    their arrow: a call that rang and was not picked up."""
    return union(phone(p, fill), _sign_x((17.9, 17.9), 2.4)(p))


def user_remove(p, fill=False):
    """``user`` with the ``x`` corner sign of history-clear and tab-close:
    remove an account."""
    return _corner(p, user(p, fill), _sign_x())


PHONE_ICONS = [
    Icon("backspace", backspace, INPUT, "delete", fill=True, meaning="Delete one character (number pad)", since=V12,
         note="Lucide calls this delete; in this set delete is an alias of trash (remove an item), a different meaning."),
    Icon("phone-missed", phone_missed, TALK, "phone-missed", meaning="Missed call", since=V12,
         note="The x sign at the top right, where phone-incoming / phone-outgoing have their arrow."),
    Icon("user-remove", user_remove, ACCOUNT, "user-round-x", meaning="Delete account / remove user", since=V12,
         note="The x sign at the bottom right, as in history-clear and tab-close."),
]
