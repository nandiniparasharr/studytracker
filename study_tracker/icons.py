"""Small line icons drawn directly on a tk.Canvas.

Vector primitives instead of emoji/font glyphs so the icons stay crisp at
any DPI and look identical on every machine.

Each painter receives (canvas, x, y, size, color) and draws inside the
square box whose top-left corner is (x, y).
"""

import tkinter as tk


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


PAINTERS = {
    "dashboard": dashboard, "play": play, "clock": clock, "alarm": alarm,
    "calendar": calendar, "sessions": sessions, "tag": tag, "reports": reports,
    "goals": goals, "settings": settings, "book": book, "people": people,
    "trophy": trophy, "flame": flame,
}


def draw(canvas, name, x, y, size, color):
    painter = PAINTERS.get(name)
    if painter:
        painter(canvas, x, y, size, color)


def icon_canvas(parent, name, size, color, bg):
    """A standalone canvas containing just one icon."""
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0, bd=0)
    draw(c, name, 0, 0, size, color)
    return c
