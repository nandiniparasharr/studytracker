"""Anti-aliased shapes for the Tk canvas.

Tk's canvas draws ovals, arcs and polygons with hard binary edges - no
anti-aliasing - so every curve in the app comes out stair-stepped. (Text is
fine: that goes through the font renderer.)

This module rasterises the curved shapes with Pillow at 4x and downsamples,
which gives real smooth edges, and hands back a tk.PhotoImage the canvas can
place with create_image.

Pillow is optional. If it isn't installed, `available()` returns False and
callers fall back to the plain canvas primitives - the app looks like it did
before rather than failing.

Shapes are cached by their arguments, so repeated draws (and redraws on
resize) cost nothing. The cache also keeps a reference to every PhotoImage,
which Tk requires - an image that goes out of scope is blanked.
"""

import math

try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL = True
except ImportError:  # pragma: no cover - depends on the machine
    _PIL = False

SS = 4              # supersample factor
_CACHE = {}
_CACHE_LIMIT = 400


def available():
    return _PIL


def clear_cache():
    _CACHE.clear()


# Tk accepts colour names as well as hex, and widget backgrounds come back
# in whatever form they were set.
_NAMED = {
    "white": (255, 255, 255), "black": (0, 0, 0),
    "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255),
    "grey": (128, 128, 128), "gray": (128, 128, 128),
    "": None,
}


def _rgb(color):
    """RGB tuple for a Tk colour, or None if it can't be parsed here."""
    if not color:
        return None
    color = str(color).strip()
    if color.startswith("#"):
        h = color[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            return None
        try:
            return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    return _NAMED.get(color.lower())


def _finish(img, size):
    """Downsample the supersampled render and wrap it for Tk."""
    if img.size != size:
        img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def _cached(key, build):
    if key in _CACHE:
        return _CACHE[key]
    if len(_CACHE) >= _CACHE_LIMIT:
        _CACHE.clear()
    image = build()
    _CACHE[key] = image
    return image


def disc(size, color, bg):
    """A filled circle, `size` px across, composited onto `bg`."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    size = max(1, int(round(size)))

    def build():
        img = Image.new("RGB", (size * SS, size * SS), _rgb(bg))
        ImageDraw.Draw(img).ellipse((0, 0, size * SS - 1, size * SS - 1), fill=_rgb(color))
        return _finish(img, (size, size))

    return _cached(("disc", size, color, bg), build)


def ring(size, color, bg, width=1.0):
    """A circle outline, `size` px across."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    size = max(1, int(round(size)))

    def build():
        img = Image.new("RGB", (size * SS, size * SS), _rgb(bg))
        inset = SS / 2
        ImageDraw.Draw(img).ellipse(
            (inset, inset, size * SS - 1 - inset, size * SS - 1 - inset),
            outline=_rgb(color), width=max(1, int(round(width * SS))))
        return _finish(img, (size, size))

    return _cached(("ring", size, color, bg, round(width, 2)), build)


def corners(radius, fill, bg, outline=None, width=1.0):
    """The four corner tiles of a rounded rectangle.

    Returns {"nw","ne","sw","se"} of radius x radius images. The straight
    edges and interior of a rounded rect need no anti-aliasing, so callers
    draw those with ordinary canvas rectangles and only paste these corners -
    which keeps the cost independent of how big the card is.
    """
    if not _PIL or _rgb(fill) is None or _rgb(bg) is None:
        return None
    if outline and _rgb(outline) is None:
        outline = None
    radius = max(1, int(round(radius)))

    def build():
        d = radius * 2
        img = Image.new("RGB", (d * SS, d * SS), _rgb(bg))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, d * SS - 1, d * SS - 1), fill=_rgb(fill))
        if outline:
            inset = width * SS / 2
            draw.ellipse((inset, inset, d * SS - 1 - inset, d * SS - 1 - inset),
                         outline=_rgb(outline), width=max(1, int(round(width * SS))))
        small = img.resize((d, d), Image.LANCZOS)
        return {
            "nw": ImageTk.PhotoImage(small.crop((0, 0, radius, radius))),
            "ne": ImageTk.PhotoImage(small.crop((radius, 0, d, radius))),
            "sw": ImageTk.PhotoImage(small.crop((0, radius, radius, d))),
            "se": ImageTk.PhotoImage(small.crop((radius, radius, d, d))),
        }

    return _cached(("corners", radius, fill, bg, outline, round(width, 2)), build)


def donut(size, thickness, slices, bg, track=None):
    """A donut chart. `slices` is a sequence of (fraction, color).

    Drawn as one image so the ring edges and the boundaries between slices
    are all anti-aliased.
    """
    if not _PIL or _rgb(bg) is None:
        return None
    if any(_rgb(c) is None for _, c in slices):
        return None
    size = max(8, int(round(size)))
    key = ("donut", size, round(thickness, 2), tuple((round(f, 6), c) for f, c in slices),
           bg, track)

    def build():
        px = size * SS
        img = Image.new("RGB", (px, px), _rgb(bg))
        draw = ImageDraw.Draw(img)
        pad = SS
        box = (pad, pad, px - 1 - pad, px - 1 - pad)

        total = sum(f for f, _ in slices)
        if total <= 0:
            if track:
                draw.ellipse(box, outline=_rgb(track), width=int(thickness * SS))
        else:
            # Start at 12 o'clock and run clockwise.
            start = -90.0
            for frac, color in slices:
                extent = 360.0 * (frac / total)
                if extent <= 0:
                    continue
                if extent >= 359.999:
                    draw.ellipse(box, outline=_rgb(color), width=int(thickness * SS))
                else:
                    # A hair of overlap hides seams between neighbouring arcs.
                    draw.arc(box, start - 0.35, start + extent + 0.35,
                             fill=_rgb(color), width=int(thickness * SS))
                start += extent

        return _finish(img, (size, size))

    return _cached(key, build)


def pill(width, height, color, bg, outline=None, outline_width=1.0):
    """A fully rounded bar - used for progress fills and small switches."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    if outline and _rgb(outline) is None:
        outline = None
    width = max(1, int(round(width)))
    height = max(1, int(round(height)))

    def build():
        w, h = width * SS, height * SS
        img = Image.new("RGB", (w, h), _rgb(bg))
        draw = ImageDraw.Draw(img)
        r = h / 2
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=_rgb(color))
        if outline:
            inset = outline_width * SS / 2
            draw.rounded_rectangle((inset, inset, w - 1 - inset, h - 1 - inset),
                                   radius=max(1, r - inset), outline=_rgb(outline),
                                   width=max(1, int(round(outline_width * SS))))
        return _finish(img, (width, height))

    return _cached(("pill", width, height, color, bg, outline, round(outline_width, 2)), build)


def wedge(size, color, bg, points):
    """An arbitrary anti-aliased polygon in a size x size box (0..1 coords)."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    size = max(1, int(round(size)))
    key = ("wedge", size, color, bg, tuple(points))

    def build():
        img = Image.new("RGB", (size * SS, size * SS), _rgb(bg))
        scaled = [(x * size * SS, y * size * SS) for x, y in points]
        ImageDraw.Draw(img).polygon(scaled, fill=_rgb(color))
        return _finish(img, (size, size))

    return _cached(key, build)


def line_icon(size, bg, strokes, color, width=1.6):
    """Anti-aliased line art: `strokes` is a list of point-lists in 0..1."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    size = max(1, int(round(size)))
    key = ("icon", size, bg, color, round(width, 2),
           tuple(tuple(p) for s in strokes for p in s), len(strokes))

    def build():
        img = Image.new("RGB", (size * SS, size * SS), _rgb(bg))
        draw = ImageDraw.Draw(img)
        w = max(1, int(round(width * SS)))
        for pts in strokes:
            scaled = [(x * size * SS, y * size * SS) for x, y in pts]
            if len(scaled) >= 2:
                draw.line(scaled, fill=_rgb(color), width=w, joint="curve")
                # round the caps, which draw.line leaves square
                for cx, cy in (scaled[0], scaled[-1]):
                    r = w / 2
                    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_rgb(color))
        return _finish(img, (size, size))

    return _cached(key, build)


def arc_ring(size, bg, color, width, start, extent):
    """A single anti-aliased arc - used by the circular icons."""
    if not _PIL or _rgb(color) is None or _rgb(bg) is None:
        return None
    size = max(1, int(round(size)))
    key = ("arcring", size, bg, color, round(width, 2), round(start, 2), round(extent, 2))

    def build():
        px = size * SS
        img = Image.new("RGB", (px, px), _rgb(bg))
        inset = width * SS / 2
        ImageDraw.Draw(img).arc((inset, inset, px - 1 - inset, px - 1 - inset),
                                start, start + extent, fill=_rgb(color),
                                width=max(1, int(round(width * SS))))
        return _finish(img, (size, size))

    return _cached(key, build)
