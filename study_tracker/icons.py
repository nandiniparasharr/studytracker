"""Small line icons drawn directly on a tk.Canvas.

Vector primitives instead of emoji/font glyphs so the icons stay crisp at
any DPI and look identical on every machine.

Each painter receives (canvas, x, y, size, color) and draws inside the
square box whose top-left corner is (x, y).
"""

import tkinter as tk

import aa


def _line(c, x1, y1, x2, y2, color, w=1.6):
    c.create_line(x1, y1, x2, y2, fill=color, width=w, capstyle="round")


def _oval(c, x1, y1, x2, y2, color, w=1.6, fill=""):
    c.create_oval(x1, y1, x2, y2, outline=color, width=w, fill=fill)


def _rect(c, x1, y1, x2, y2, color, w=1.6, fill=""):
    c.create_rectangle(x1, y1, x2, y2, outline=color, width=w, fill=fill)


def dashboard(c, x, y, s, color):
    g = s * 0.38
    gap = s * 0.14
    _rect(c, x, y, x + g, y + g, color)
    _rect(c, x + g + gap, y, x + 2 * g + gap, y + g, color)
    _rect(c, x, y + g + gap, x + g, y + 2 * g + gap, color)
    _rect(c, x + g + gap, y + g + gap, x + 2 * g + gap, y + 2 * g + gap, color)


def play(c, x, y, s, color):
    c.create_polygon(x + s * 0.22, y + s * 0.12, x + s * 0.22, y + s * 0.88,
                     x + s * 0.85, y + s * 0.5,
                     outline=color, fill="", width=1.6, joinstyle="round")


def clock(c, x, y, s, color):
    _oval(c, x + s * 0.08, y + s * 0.08, x + s * 0.92, y + s * 0.92, color)
    cx, cy = x + s * 0.5, y + s * 0.5
    _line(c, cx, cy, cx, cy - s * 0.26, color)
    _line(c, cx, cy, cx + s * 0.2, cy + s * 0.1, color)


def alarm(c, x, y, s, color):
    _oval(c, x + s * 0.14, y + s * 0.2, x + s * 0.86, y + s * 0.92, color)
    cx, cy = x + s * 0.5, y + s * 0.56
    _line(c, cx, cy, cx, cy - s * 0.2, color)
    _line(c, cx, cy, cx + s * 0.16, cy + s * 0.08, color)
    _line(c, x + s * 0.1, y + s * 0.16, x + s * 0.28, y + s * 0.04, color)
    _line(c, x + s * 0.9, y + s * 0.16, x + s * 0.72, y + s * 0.04, color)


def calendar(c, x, y, s, color):
    _rect(c, x + s * 0.1, y + s * 0.18, x + s * 0.9, y + s * 0.92, color)
    _line(c, x + s * 0.1, y + s * 0.4, x + s * 0.9, y + s * 0.4, color)
    _line(c, x + s * 0.3, y + s * 0.08, x + s * 0.3, y + s * 0.26, color)
    _line(c, x + s * 0.7, y + s * 0.08, x + s * 0.7, y + s * 0.26, color)


def sessions(c, x, y, s, color):
    _rect(c, x + s * 0.12, y + s * 0.1, x + s * 0.88, y + s * 0.9, color)
    for i in range(3):
        yy = y + s * (0.3 + i * 0.2)
        _line(c, x + s * 0.28, yy, x + s * 0.72, yy, color, w=1.4)


def tag(c, x, y, s, color):
    c.create_polygon(x + s * 0.1, y + s * 0.5, x + s * 0.5, y + s * 0.1,
                     x + s * 0.9, y + s * 0.5, x + s * 0.5, y + s * 0.9,
                     outline=color, fill="", width=1.6, joinstyle="round")
    _oval(c, x + s * 0.42, y + s * 0.32, x + s * 0.56, y + s * 0.46, color, w=1.4)


def reports(c, x, y, s, color):
    base = y + s * 0.88
    for i, h in enumerate((0.34, 0.58, 0.44)):
        bx = x + s * (0.2 + i * 0.26)
        _line(c, bx, base, bx, base - s * h, color, w=2.4)


def goals(c, x, y, s, color):
    _oval(c, x + s * 0.08, y + s * 0.08, x + s * 0.92, y + s * 0.92, color)
    _oval(c, x + s * 0.3, y + s * 0.3, x + s * 0.7, y + s * 0.7, color, w=1.4)
    _oval(c, x + s * 0.45, y + s * 0.45, x + s * 0.55, y + s * 0.55, color, w=1.4, fill=color)


def settings(c, x, y, s, color):
    _oval(c, x + s * 0.32, y + s * 0.32, x + s * 0.68, y + s * 0.68, color)
    cx, cy = x + s * 0.5, y + s * 0.5
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (-0.7, -0.7), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7)):
        _line(c, cx + dx * s * 0.34, cy + dy * s * 0.34,
              cx + dx * s * 0.46, cy + dy * s * 0.46, color, w=1.6)


def book(c, x, y, s, color):
    _line(c, x + s * 0.5, y + s * 0.22, x + s * 0.5, y + s * 0.88, color, w=1.5)
    c.create_line(x + s * 0.5, y + s * 0.22, x + s * 0.16, y + s * 0.12,
                  x + s * 0.08, y + s * 0.16, x + s * 0.08, y + s * 0.8,
                  x + s * 0.16, y + s * 0.78, x + s * 0.5, y + s * 0.88,
                  fill=color, width=1.5, smooth=False, joinstyle="round")
    c.create_line(x + s * 0.5, y + s * 0.22, x + s * 0.84, y + s * 0.12,
                  x + s * 0.92, y + s * 0.16, x + s * 0.92, y + s * 0.8,
                  x + s * 0.84, y + s * 0.78, x + s * 0.5, y + s * 0.88,
                  fill=color, width=1.5, smooth=False, joinstyle="round")


def people(c, x, y, s, color):
    _oval(c, x + s * 0.3, y + s * 0.12, x + s * 0.58, y + s * 0.4, color)
    c.create_arc(x + s * 0.16, y + s * 0.46, x + s * 0.72, y + s * 1.02,
                 start=0, extent=180, style="arc", outline=color, width=1.6)
    _oval(c, x + s * 0.62, y + s * 0.2, x + s * 0.84, y + s * 0.42, color, w=1.3)
    c.create_arc(x + s * 0.56, y + s * 0.5, x + s * 0.96, y + s * 0.9,
                 start=0, extent=180, style="arc", outline=color, width=1.3)


def trophy(c, x, y, s, color):
    c.create_arc(x + s * 0.24, y + s * 0.1, x + s * 0.76, y + s * 0.62,
                 start=180, extent=180, style="arc", outline=color, width=1.8)
    _line(c, x + s * 0.24, y + s * 0.36, x + s * 0.24, y + s * 0.16, color)
    _line(c, x + s * 0.76, y + s * 0.36, x + s * 0.76, y + s * 0.16, color)
    _line(c, x + s * 0.24, y + s * 0.16, x + s * 0.76, y + s * 0.16, color)
    c.create_arc(x + s * 0.06, y + s * 0.16, x + s * 0.3, y + s * 0.44,
                 start=90, extent=180, style="arc", outline=color, width=1.5)
    c.create_arc(x + s * 0.7, y + s * 0.16, x + s * 0.94, y + s * 0.44,
                 start=270, extent=180, style="arc", outline=color, width=1.5)
    _line(c, x + s * 0.5, y + s * 0.6, x + s * 0.5, y + s * 0.76, color)
    _line(c, x + s * 0.32, y + s * 0.88, x + s * 0.68, y + s * 0.88, color, w=2)
    _line(c, x + s * 0.4, y + s * 0.76, x + s * 0.6, y + s * 0.76, color, w=2)


def flame(c, x, y, s, color):
    # smooth=False keeps the tip pointed - smoothing rounds it into a blob
    pts = [(0.50, 0.02), (0.70, 0.28), (0.62, 0.38), (0.82, 0.60),
           (0.72, 0.86), (0.50, 0.98), (0.28, 0.86), (0.18, 0.60),
           (0.38, 0.38), (0.34, 0.26)]
    coords = []
    for px, py in pts:
        coords.extend([x + s * px, y + s * py])
    c.create_polygon(coords, outline="", fill=color, smooth=False)


# Every icon described declaratively in 0..1 space, so one rasteriser can
# draw them all with anti-aliasing. The canvas painters above stay as the
# fallback for machines without Pillow.
#
# Ops: ("line", pts, w) polyline · ("poly", pts, w) closed outline
#      ("fill_poly", pts) · ("ellipse", box, w) · ("fill_ellipse", box)
#      ("arc", box, start, extent, w)      - w is a multiple of the stroke
OPS = {
    "dashboard": [
        ("poly", [(.02, .02), (.40, .02), (.40, .40), (.02, .40)], 1),
        ("poly", [(.54, .02), (.92, .02), (.92, .40), (.54, .40)], 1),
        ("poly", [(.02, .54), (.40, .54), (.40, .92), (.02, .92)], 1),
        ("poly", [(.54, .54), (.92, .54), (.92, .92), (.54, .92)], 1),
    ],
    "play": [("poly", [(.26, .12), (.26, .88), (.86, .50)], 1)],
    "clock": [
        ("ellipse", (.08, .08, .92, .92), 1),
        ("line", [(.50, .50), (.50, .26)], 1),
        ("line", [(.50, .50), (.68, .59)], 1),
    ],
    "alarm": [
        ("ellipse", (.14, .20, .86, .92), 1),
        ("line", [(.50, .56), (.50, .36)], 1),
        ("line", [(.50, .56), (.66, .64)], 1),
        ("line", [(.10, .16), (.28, .04)], 1),
        ("line", [(.90, .16), (.72, .04)], 1),
    ],
    "calendar": [
        ("poly", [(.10, .18), (.90, .18), (.90, .92), (.10, .92)], 1),
        ("line", [(.10, .40), (.90, .40)], 1),
        ("line", [(.30, .08), (.30, .26)], 1),
        ("line", [(.70, .08), (.70, .26)], 1),
    ],
    "sessions": [
        ("poly", [(.12, .10), (.88, .10), (.88, .90), (.12, .90)], 1),
        ("line", [(.28, .32), (.72, .32)], .85),
        ("line", [(.28, .50), (.72, .50)], .85),
        ("line", [(.28, .68), (.72, .68)], .85),
    ],
    "tag": [
        ("poly", [(.10, .50), (.50, .10), (.90, .50), (.50, .90)], 1),
        ("ellipse", (.42, .32, .58, .48), .85),
    ],
    "reports": [
        ("line", [(.20, .88), (.20, .54)], 1.5),
        ("line", [(.50, .88), (.50, .28)], 1.5),
        ("line", [(.80, .88), (.80, .44)], 1.5),
    ],
    "goals": [
        ("ellipse", (.08, .08, .92, .92), 1),
        ("ellipse", (.30, .30, .70, .70), .85),
        ("fill_ellipse", (.44, .44, .56, .56)),
    ],
    "settings": [
        ("ellipse", (.33, .33, .67, .67), 1),
        ("line", [(.50, .16), (.50, .03)], 1),
        ("line", [(.50, .84), (.50, .97)], 1),
        ("line", [(.16, .50), (.03, .50)], 1),
        ("line", [(.84, .50), (.97, .50)], 1),
        ("line", [(.26, .26), (.16, .16)], 1),
        ("line", [(.74, .74), (.84, .84)], 1),
        ("line", [(.26, .74), (.16, .84)], 1),
        ("line", [(.74, .26), (.84, .16)], 1),
    ],
    "book": [
        ("line", [(.50, .24), (.50, .88)], .9),
        ("line", [(.50, .24), (.16, .13), (.08, .17), (.08, .80),
                  (.16, .77), (.50, .88)], .9),
        ("line", [(.50, .24), (.84, .13), (.92, .17), (.92, .80),
                  (.84, .77), (.50, .88)], .9),
    ],
    "people": [
        ("ellipse", (.30, .12, .58, .40), 1),
        ("arc", (.16, .46, .72, 1.02), 180, 180, 1),
        ("ellipse", (.63, .21, .84, .42), .8),
        ("arc", (.57, .51, .96, .90), 180, 180, .8),
    ],
    "trophy": [
        ("arc", (.24, .10, .76, .62), 0, 180, 1.1),
        ("line", [(.24, .16), (.24, .36)], 1),
        ("line", [(.76, .16), (.76, .36)], 1),
        ("line", [(.24, .16), (.76, .16)], 1),
        ("arc", (.06, .16, .30, .44), 90, 180, .9),
        ("arc", (.70, .16, .94, .44), 270, 180, .9),
        ("line", [(.50, .60), (.50, .76)], 1),
        ("line", [(.40, .76), (.60, .76)], 1.2),
        ("line", [(.32, .88), (.68, .88)], 1.2),
    ],
    "flame": [
        ("fill_poly", [(.50, .02), (.70, .28), (.62, .38), (.82, .60),
                       (.72, .86), (.50, .98), (.28, .86), (.18, .60),
                       (.38, .38), (.34, .26)]),
    ],
}


PAINTERS = {
    "dashboard": dashboard, "play": play, "clock": clock, "alarm": alarm,
    "calendar": calendar, "sessions": sessions, "tag": tag, "reports": reports,
    "goals": goals, "settings": settings, "book": book, "people": people,
    "trophy": trophy, "flame": flame,
}


def draw(canvas, name, x, y, size, color, bg=None):
    """Draw icon `name` in a size x size box at (x, y).

    Uses the anti-aliased rasteriser when Pillow is available and the icon
    has vector strokes defined; otherwise falls back to canvas primitives,
    which is how every icon used to be drawn.
    """
    if bg is None:
        try:
            bg = str(canvas.cget("bg"))
        except tk.TclError:
            bg = None

    if bg and aa.available():
        img = _aa_image(name, size, color, bg)
        if img is not None:
            canvas.create_image(x, y, image=img, anchor="nw")
            # hold a reference; Tk blanks images that get collected
            keep = getattr(canvas, "_icon_refs", None)
            if keep is None:
                keep = canvas._icon_refs = []
            keep.append(img)
            return

    painter = PAINTERS.get(name)
    if painter:
        painter(canvas, x, y, size, color)


def _aa_image(name, size, color, bg):
    ops = OPS.get(name)
    if not ops:
        return None

    from PIL import Image, ImageDraw, ImageTk
    if aa._rgb(color) is None or aa._rgb(bg) is None:
        return None

    key = ("icon_ops", name, int(size), color, bg)
    if key in aa._CACHE:
        return aa._CACHE[key]

    ss = aa.SS
    px = max(1, int(size)) * ss
    img = Image.new("RGB", (px, px), aa._rgb(bg))
    draw = ImageDraw.Draw(img)
    rgb = aa._rgb(color)
    base = max(1.15, size * 0.085) * ss

    def pts(points):
        return [(x * px, y * px) for x, y in points]

    def box(b):
        return [b[0] * px, b[1] * px, b[2] * px - 1, b[3] * px - 1]

    for op in ops:
        kind = op[0]
        if kind == "line":
            w = max(1, int(round(base * op[2])))
            p = pts(op[1])
            draw.line(p, fill=rgb, width=w, joint="curve")
            for cx, cy in (p[0], p[-1]):          # round the caps
                r = w / 2
                draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb)
        elif kind == "poly":
            w = max(1, int(round(base * op[2])))
            p = pts(op[1]) + [pts(op[1])[0]]
            draw.line(p, fill=rgb, width=w, joint="curve")
        elif kind == "fill_poly":
            draw.polygon(pts(op[1]), fill=rgb)
        elif kind == "ellipse":
            draw.ellipse(box(op[1]), outline=rgb,
                         width=max(1, int(round(base * op[2]))))
        elif kind == "fill_ellipse":
            draw.ellipse(box(op[1]), fill=rgb)
        elif kind == "arc":
            draw.arc(box(op[1]), op[2], op[2] + op[3], fill=rgb,
                     width=max(1, int(round(base * op[4]))))

    out = ImageTk.PhotoImage(img.resize((int(size), int(size)), Image.LANCZOS))
    aa._CACHE[key] = out
    return out


def icon_canvas(parent, name, size, color, bg):
    """A standalone canvas containing just one icon."""
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    draw(c, name, 0, 0, size, color, bg=bg)
    return c
