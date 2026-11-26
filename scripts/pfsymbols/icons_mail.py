"""Porto Faifo Symbols recipes: mail.

Same pen, grid and rules as ``icons.py``.
"""

from __future__ import annotations

from .icons import Icon, mail
from .icons_desktop import CORNER, _badge, _corner
from .icons_system import _arrow_up
from .icons_photo import _pencil
from .kit import box, minus, mirrored, turned, union

V9 = "0.9.0"
MAIL = "Mail"


# ------------------------------------------------------------------- reply
def _reply(p, tip_x=3.6, s=6.0):
    """A chevron pointing back and a tail that turns down: answer."""
    y, c_x, r = 12.2, 14.6, 5.4
    head = p.line([(tip_x + s, y + s), (tip_x, y), (tip_x + s, y - s)])
    tail = union(p.bar((tip_x, y), (c_x, y), cut=("p", "p")), p.arc(c_x, y - r, r, keep=box(x0=c_x, y0=y - r)),
                 p.bar((c_x + r, y - r), (c_x + r, 4.2), cut=("p", "h")))
    return union(head, tail)


def mail_reply(p, fill=False):
    return _reply(p)


def mail_reply_all(p, fill=False):
    """Reply with a second chevron behind it: answer everyone."""
    main = _reply(p, tip_x=9.0, s=5.0)
    behind = p.line([(8.8, 17.2), (3.8, 12.2), (8.8, 7.2)])
    return union(main, minus(behind, p.stroked(p.w + 2 * max(1.0, 0.45 * p.w)).line([(14.0, 17.2), (9.0, 12.2), (14.0, 7.2)])))


def mail_forward(p, fill=False):
    return mirrored(mail_reply(p))


# --------------------------------------------------------------- paperclip
def attachment(p, fill=False):
    """A paperclip at 45°: two bends, the free end inside."""
    left, inner, right = 7.6, 11.5, 15.4
    bottom_c, top_c = ((left + right) / 2, 7.4), ((inner + right) / 2, 16.6)
    rb, rt = (right - left) / 2, (right - inner) / 2
    clip_ = union(
        p.bar((left, 15.0), (left, bottom_c[1]), cut=("p", "p")),
        p.arc(*bottom_c, rb, keep=box(y1=bottom_c[1])),
        p.bar((right, bottom_c[1]), (right, top_c[1]), cut=("p", "p")),
        p.arc(*top_c, rt, keep=box(y0=top_c[1])),
        p.bar((inner, top_c[1]), (inner, 9.6), cut=("p", "p")),
    )
    return turned(clip_, -40)


# -------------------------------------------------------------------- flag
FLAG = [(5.4, 20.2), (19.8, 20.2), (16.0, 15.8), (19.8, 11.4), (5.4, 11.4)]


def flag(p, fill=False):
    """A swallowtail flag on a pole: marked.  Not a bookmark (a ribbon that
    hangs) or a pin (a head on a needle)."""
    s = p.radius_small
    cloth = (p.solid if fill else p.frame)(FLAG, corners={0: 0, 1: s, 2: 0.6, 3: s, 4: 0})
    return union(cloth, p.bar((5.4, 20.6), (5.4, 2.9), cut="h"))


# ----------------------------------------------------------- envelope + sign
def _sign_alert(p, x=17.6):
    """"!" drawn with the pen, a stroke over a dot: the corner sign for spam."""
    return union(p.bar((x, 11.2), (x, 6.6), cut="h"), p.dot(x, 3.6))


def _sign_ok(p, c=CORNER):
    return p.line([(c[0] - 3.0, c[1] + 0.4), (c[0] - 0.9, c[1] - 1.7), (c[0] + 3.0, c[1] + 2.2)])


def mail_junk(p, fill=False):
    return _corner(p, mail(p, fill), _sign_alert)


def mail_not_junk(p, fill=False):
    return _corner(p, mail(p, fill), _sign_ok)


def mail_unread(p, fill=False):
    """The envelope with a dot on its top right: not read yet."""
    return _badge(p, mail(p, fill), lambda q: q.disc(17.8, 17.4, 2.6))


def mail_outbox(p, fill=False):
    """The envelope with an arrow going up out of its corner: waiting to
    leave.  Not ``inbox`` (a tray) or ``upload`` (an arrow into a tray)."""
    return _corner(p, mail(p, fill), _arrow_up(c=(17.6, 6.6), s=2.8, length=7.4))


def mail_draft(p, fill=False):
    """The envelope with a pencil over its corner: a mail being written."""
    return _badge(p, mail(p, fill), lambda q: _pencil(q, tip=(11.0, 2.9), length=11.4, hw=2.1))


MAIL_ICONS = [
    Icon("mail-reply", mail_reply, MAIL, "reply", "mail-reply-sender", "spec", meaning="Reply", since=V9,
         note="A return arrow with a tail curving down; unlike undo (a hook back onto itself)."),
    Icon("mail-reply-all", mail_reply_all, MAIL, "reply-all", "mail-reply-all", "spec", meaning="Reply all", since=V9,
         note="One more chevron behind, cut back by one gap."),
    Icon("mail-forward", mail_forward, MAIL, "forward", "mail-forward", "spec", meaning="Forward", since=V9),
    Icon("attachment", attachment, MAIL, "paperclip", "mail-attachment", "spec", "status", meaning="Attachment", since=V9),
    Icon("flag", flag, MAIL, "flag", "mail-mark-important", "spec", fill=True, meaning="Flag", since=V9,
         note="A swallowtail flag on a pole; unlike bookmark (hanging ribbon) and pin (pushpin)."),
    Icon("mail-junk", mail_junk, MAIL, "mail-warning", "mail-mark-junk", "spec", fill=True, meaning="Junk mail", since=V9),
    Icon("mail-not-junk", mail_not_junk, MAIL, "mail-check", "mail-mark-notjunk", "spec", fill=True, meaning="Not junk", since=V9),
    Icon("mail-unread", mail_unread, MAIL, "mail-dot", "mail-mark-unread", "spec", fill=True, meaning="Mark as unread", since=V9,
         note="mail-unread (a state) stays the mail glyph; this is the action of marking."),
    Icon("mail-outbox", mail_outbox, MAIL, "", "mail-folder-outbox", "spec", "places", fill=True, meaning="Outbox", since=V9),
    Icon("mail-draft", mail_draft, MAIL, "", "mail-folder-drafts", "kde", "places", fill=True, meaning="Draft", since=V9),
]
