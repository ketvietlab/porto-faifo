"""Porto Faifo Symbols recipes: chat controls.  Original geometry, not copied provider artwork.
"""

from .icons import Icon, R
from .kit import box, union


def smile(p, fill=False):
    eyes = union(p.dot(8.7, 14.6), p.dot(15.3, 14.6))
    mouth = p.arc(12, 10.5, 4.4, 3.3, keep=box(y1=10.5))
    return union(p.ring(12, 12, R), eyes, mouth)


def sticker(p, fill=False):
    # Blank adhesive sheet, peeled at bottom right; no face to confuse emoji.
    edge = [(3.9, 3.9), (13.2, 3.9), (20.1, 10.8), (20.1, 20.1), (3.9, 20.1)]
    sheet = p.frame(edge, corners={0: p.radius, 1: 0.6, 2: 0.6, 3: p.radius, 4: p.radius})
    fold = p.line([(13.2, 3.9), (13.2, 10.8), (20.1, 10.8)],
                  cut="p", corners={1: p.radius_small})
    return union(sheet, fold)


def qr_code(p, fill=False):
    # Three open finder squares remain legible at 14px; no tiny centre dots.
    finders = [p.rect(x, y, x + 6.6, y + 6.6, r=0.6)
               for x, y in ((3.4, 14.0), (14.0, 14.0), (3.4, 3.4))]
    data = p.line([(14.0, 3.4), (14.0, 7.0), (17.3, 7.0), (17.3, 10.0)], cut="g")
    corner = p.line([(17.8, 3.4), (20.6, 3.4), (20.6, 7.0)], cut="g")
    return union(*finders, data, corner)


def video_camera(p, fill=False):
    body = p.rect(3.1, 6.0, 14.5, 18.0)
    lens = p.frame([(14.5, 9.0), (20.9, 6.0), (20.9, 18.0), (14.5, 15.0)],
                   corners={0: 0, 1: 0.6, 2: 0.6, 3: 0})
    return union(body, lens)


CHAT_ICONS = [
    Icon("smile", smile, "Chat", "smile", meaning="Choose an emoji or reaction", since="0.12.0"),
    Icon("sticker", sticker, "Chat", "sticker", meaning="Choose a sticker", since="0.12.0",
         note="A label with a peeled corner; no smiley, to stay distinct from emoji."),
    Icon("qr-code", qr_code, "Chat", "qr-code", meaning="Connect with a QR code", since="0.12.0",
         note="An interface symbol with no QR data; do not use it in place of a real login code."),
    Icon("video-camera", video_camera, "Chat", "video", meaning="Video call", since="0.12.0",
         note="A video camera; unlike video, a media frame with a Play triangle."),
]
