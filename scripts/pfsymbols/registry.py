"""Every Porto Faifo Symbols icon, gathered from the recipe modules, with
aliases resolved to one canonical glyph.
"""

from __future__ import annotations

from .icons import ICONS as BASE
from .icons_business import BUSINESS_ICONS
from .icons_desktop import DESKTOP_ICONS
from .icons_system import GHOST_OPACITY, SYSTEM_ICONS
from .icons_photo import PHOTO_ICONS
from .icons_calendar import CALENDAR_ICONS
from .icons_mail import MAIL_ICONS
from .icons_notes import NOTES_ICONS
from .icons_web import WEB_ICONS
from .icons_dev import DEV_ICONS
from .icons_chat import CHAT_ICONS
from .icons_phone import PHONE_ICONS

ICONS = BASE + SYSTEM_ICONS + DESKTOP_ICONS + BUSINESS_ICONS + PHOTO_ICONS + WEB_ICONS + NOTES_ICONS + MAIL_ICONS + CALENDAR_ICONS + DEV_ICONS + PHONE_ICONS + CHAT_ICONS
BY_NAME = {i.name: i for i in ICONS}
ALIASES = {alias: icon.name for icon in ICONS for alias in icon.aliases}

assert len(BY_NAME) == len(ICONS), "duplicate icon name"
assert not set(ALIASES) & set(BY_NAME), "an alias shadows an icon"

__all__ = ["ALIASES", "BY_NAME", "GHOST_OPACITY", "ICONS"]
