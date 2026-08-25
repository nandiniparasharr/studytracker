"""Reusable UI pieces shared across the app pages."""

import calendar as calmod
import tkinter as tk
from datetime import date, timedelta

import icons
import storage
import theme


def round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """Draw a rounded rectangle on any canvas."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def fmt_hm(seconds, short=False):
    seconds = int(seconds)
    h, m = seconds // 3600, (seconds % 3600) // 60
    if short:
        return f"{h}h {m:02d}m" if h else f"{m}m"
    return f"{h}h {m:02d}m"


class RoundedCard(tk.Frame):
    """A white card with rounded corners and a hairline border."""

    def __init__(self, parent, bg=theme.CARD, radius=16, border=theme.BORDER,
                 autosize=True, **kwargs):
        try:
            parent_bg = parent.cget("bg")
        except tk.TclError:
            parent_bg = theme.BG
        super().__init__(parent, bg=parent_bg, **kwargs)
        self._radius = radius
        self._bg = bg
        self._border = border
        self._autosize = autosize

        # A bare Canvas requests a large natural size; pin it to 1x1 so the
        # card only ever takes the space its layout gives it.
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=parent_bg, width=1, height=1)
        self.canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window(2, 2, window=self.body, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)

    def sync_height(self):
        """Grow the card to fit its content.

        Grid cells with a minsize stretch the card on their own, but inside a
        scrolling column nothing stretches it - and the body sits in a canvas
        window, so while the canvas is 1px tall the body is clipped to 1px too.
        Pages call this after (re)building their content.
        """
        if not self._autosize:
            return
        try:
            self.update_idletasks()
            needed = self.body.winfo_reqheight() + 4
            if needed > 4 and int(self.canvas.cget("height")) != needed:
                self.canvas.config(height=needed)
        except (tk.TclError, ValueError):
            pass

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 8 or h < 8:
            return
        self.canvas.delete("card_bg")
        round_rect(self.canvas, 1, 1, w - 1, h - 1, self._radius,
                   fill=self._bg, outline=self._border, width=1, tags="card_bg")
        self.canvas.tag_lower("card_bg")
        self.canvas.coords(self._window, 2, 2)
        self.canvas.itemconfig(self._window, width=w - 4, height=h - 4)


class NavButton(tk.Canvas):
    """Sidebar entry: icon + label, with a rounded pill when active."""

    HEIGHT = 44

    def __init__(self, parent, text, icon_name, command, width=184):
        super().__init__(parent, height=self.HEIGHT, width=width,
                         bg=theme.SIDEBAR, highlightthickness=0, bd=0, cursor="hand2")
        self.text = text
        self.icon_name = icon_name
        self.command = command
        self.active = False
        self.hovered = False
        self._px_w = width
        self.bind("<Button-1>", lambda _e: self.command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_configure)
        self._render()

    def _on_configure(self, event):
        if event.width != self._px_w:
            self._px_w = event.width
            self._render()

    def set_active(self, active):
        if active != self.active:
            self.active = active
            self._render()

    def _on_enter(self, _e):
        self.hovered = True
        self._render()

    def _on_leave(self, _e):
        self.hovered = False
        self._render()

    def _render(self):
        self.delete("all")
        w, h = self._px_w, self.HEIGHT
        if self.active:
            round_rect(self, 0, 2, w, h - 2, 11, fill=theme.SIDEBAR_ACTIVE, outline="")
            fg = theme.SIDEBAR_TEXT_ACTIVE
        elif self.hovered:
            round_rect(self, 0, 2, w, h - 2, 11, fill=theme.SIDEBAR_HOVER, outline="")
            fg = theme.SIDEBAR_TEXT_ACTIVE
        else:
            fg = theme.SIDEBAR_TEXT

        icons.draw(self, self.icon_name, 16, (h - 18) / 2, 18, fg)
        self.create_text(48, h / 2, text=self.text, anchor="w", fill=fg,
                         font=(theme.FONT_FAMILY, 11, "bold" if self.active else "normal"))


class StatCard(RoundedCard):
    """Icon bubble + label + big value + delta line."""

    def __init__(self, parent, icon_name, label, value, delta=None):
        super().__init__(parent, radius=16)
        wrap = tk.Frame(self.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=18, pady=16)

        top = tk.Frame(wrap, bg=theme.CARD)
        top.pack(fill="x", anchor="w")

        bubble = tk.Canvas(top, width=44, height=44, bg=theme.CARD, highlightthickness=0)
        bubble.create_oval(0, 0, 43, 43, fill=theme.ACCENT_SOFT, outline="")
        icons.draw(bubble, icon_name, 12, 12, 20, theme.ACCENT)
        bubble.pack(side="left")

        right = tk.Frame(top, bg=theme.CARD)
        right.pack(side="left", padx=(12, 0), anchor="n")
        tk.Label(right, text=label, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
        self.value_label = tk.Label(right, text=value, bg=theme.CARD, fg=theme.TEXT,
                                     font=(theme.FONT_FAMILY, 19, "bold"))
        self.value_label.pack(anchor="w", pady=(1, 0))

        self.delta_frame = tk.Frame(wrap, bg=theme.CARD)
        self.delta_frame.pack(anchor="w", pady=(10, 0))
        if delta:
            self._render_delta(delta)

    def _render_delta(self, delta):
        arrow = tk.Canvas(self.delta_frame, width=12, height=12, bg=theme.CARD, highlightthickness=0)
        up = not delta.startswith("-")
        color = theme.POSITIVE if up else theme.DANGER
        if up:
            arrow.create_polygon(6, 2, 11, 9, 1, 9, fill=color, outline="")
        else:
            arrow.create_polygon(6, 10, 11, 3, 1, 3, fill=color, outline="")
        arrow.pack(side="left", padx=(0, 5))
        tk.Label(self.delta_frame, text=delta.lstrip("-"), bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(side="left")


class BarChart(tk.Canvas):
    """Weekly hours as rounded vertical bars with y-axis gridlines."""

    def __init__(self, parent, bg=theme.CARD):
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0, width=1, height=1)
        self._bg = bg
        self.values = [0] * 7
        self.labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.bind("<Configure>", lambda _e: self.render())

    def set_values(self, values, labels=None):
        self.values = values
        if labels:
            self.labels = labels
        self.render()

    def render(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 40 or h < 40:
            return

        pad_l, pad_r, pad_b, pad_t = 40, 8, 26, 10
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_b - pad_t
        if plot_w <= 0 or plot_h <= 0:
            return

        hours = [v / 3600 for v in self.values]
        top_hours = max(2, ((max(hours) if hours else 0) + 1.999) // 2 * 2)
        steps = int(top_hours // 2) + 1

        for i in range(steps):
            hv = i * 2
            yy = pad_t + plot_h - (hv / top_hours) * plot_h
            self.create_line(pad_l, yy, w - pad_r, yy, fill=theme.BORDER)
            self.create_text(pad_l - 10, yy, text=f"{int(hv)}h", anchor="e",
                             fill=theme.TEXT_FAINT, font=(theme.FONT_FAMILY, 8))

        slot = plot_w / len(hours)
        bar_w = min(26, slot * 0.42)
        for i, hv in enumerate(hours):
            cx = pad_l + slot * (i + 0.5)
            bh = (hv / top_hours) * plot_h
            base = pad_t + plot_h
            if bh > 1:
                round_rect(self, cx - bar_w / 2, base - bh, cx + bar_w / 2, base,
                           min(5, bar_w / 2), fill=theme.ACCENT, outline="")
            self.create_text(cx, h - pad_b + 13, text=self.labels[i], fill=theme.TEXT_MUTED,
                             font=(theme.FONT_FAMILY, 9))


class DonutChart(tk.Canvas):
    """Subject split as a donut with the total in the middle."""

    def __init__(self, parent, bg=theme.CARD, size=170):
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0, width=size, height=size)
        self._bg = bg
        self.size = size
        self.slices = []

    def set_slices(self, slices):
        """slices: list of (label, seconds, color)."""
        self.slices = slices
        self.render()

    def render(self):
        self.delete("all")
        s = self.size
        pad, thickness = 6, 24
        total = sum(sec for _, sec, _ in self.slices)

        if total <= 0:
            self.create_oval(pad, pad, s - pad, s - pad, outline=theme.TRACK, width=thickness)
        else:
            start = 90.0
            for _, sec, color in self.slices:
                extent = -360.0 * (sec / total)
                if abs(extent) < 0.01:
                    continue
                # A full circle drawn as an arc renders as nothing; use an oval.
                if abs(extent) >= 359.99:
                    self.create_oval(pad + thickness / 2, pad + thickness / 2,
                                     s - pad - thickness / 2, s - pad - thickness / 2,
                                     outline=color, width=thickness)
                else:
                    self.create_arc(pad + thickness / 2, pad + thickness / 2,
                                    s - pad - thickness / 2, s - pad - thickness / 2,
                                    start=start, extent=extent, style="arc",
                                    outline=color, width=thickness)
                start += extent

        self.create_text(s / 2, s / 2 - 7, text=fmt_hm(total), fill=theme.TEXT,
                         font=(theme.FONT_FAMILY, 12, "bold"))
        self.create_text(s / 2, s / 2 + 11, text="Total", fill=theme.TEXT_MUTED,
                         font=(theme.FONT_FAMILY, 8))


class ProgressBar(tk.Canvas):
    def __init__(self, parent, bg=theme.CARD, height=9):
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0, height=height, width=1)
        self._px_h = height
        self.ratio = 0.0
        self.bind("<Configure>", lambda _e: self.render())

    def set_ratio(self, ratio):
        self.ratio = max(0.0, min(1.0, ratio))
        self.render()

    def render(self):
        self.delete("all")
        w, h = self.winfo_width(), self._px_h
        if w < 4:
            return
        round_rect(self, 0, 0, w, h, h / 2, fill=theme.TRACK, outline="")
        if self.ratio > 0:
            round_rect(self, 0, 0, max(h, w * self.ratio), h, h / 2, fill=theme.ACCENT, outline="")


class StudyCalendar(tk.Frame):
    """Month grid: a filled circle for today, a colored dot under any day
    with logged study time (darker = more hours), plus an intensity legend.
    """

    CELL_H = 46
    HEADER_H = 26

    def __init__(self, parent, bg=theme.CARD, on_day_click=None):
        super().__init__(parent, bg=bg)
        self.bg = bg
        self.on_day_click = on_day_click
        self.selected_day = None
        today = date.today()
        self.year, self.month = today.year, today.month
        self.day_totals = {}

        self.header = tk.Frame(self, bg=bg)
        self.header.pack(fill="x")
        self.title_label = tk.Label(self.header, text="Study Calendar", bg=bg, fg=theme.TEXT,
                                     font=(theme.FONT_FAMILY, 13, "bold"))
        self.title_label.pack(side="left")

        nav = tk.Frame(self.header, bg=bg)
        nav.pack(side="right")
        self.month_label = tk.Label(nav, text="", bg=bg, fg=theme.TEXT,
                                     font=(theme.FONT_FAMILY, 10))
        self.month_label.pack(side="left", padx=(0, 10))
        for glyph, handler in (("‹", self._prev_month), ("›", self._next_month)):
            b = tk.Label(nav, text=glyph, bg=bg, fg=theme.TEXT_MUTED, cursor="hand2",
                         font=(theme.FONT_FAMILY, 13), padx=7)
            b.pack(side="left")
            b.bind("<Button-1>", lambda _e, hh=handler: hh())
            b.bind("<Enter>", lambda _e, w=b: w.config(fg=theme.ACCENT))
            b.bind("<Leave>", lambda _e, w=b: w.config(fg=theme.TEXT_MUTED))

        self.grid_canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=1, height=1)
        self.grid_canvas.pack(fill="both", expand=True, pady=(14, 0))
        self.grid_canvas.bind("<Configure>", lambda _e: self.render())
        self.grid_canvas.bind("<Button-1>", self._on_click)

        self.legend = tk.Frame(self, bg=bg)
        self.legend.pack(fill="x", pady=(10, 0))
        self._build_legend()

        self._hit_boxes = []

    def _build_legend(self):
        strip = tk.Frame(self.legend, bg=self.bg)
        strip.pack()
        for label, color in theme.CAL_LEGEND:
            item = tk.Frame(strip, bg=self.bg)
            item.pack(side="left", padx=8)
            dot = tk.Canvas(item, width=10, height=10, bg=self.bg, highlightthickness=0)
            if color is None:
                dot.create_oval(1, 1, 9, 9, outline=theme.TEXT_FAINT, width=1)
            else:
                dot.create_oval(1, 1, 9, 9, fill=color, outline="")
            dot.pack(side="left", padx=(0, 5))
            tk.Label(item, text=label, bg=self.bg, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 8)).pack(side="left")

    def _prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month, self.year = 12, self.year - 1
        self.render()

    def _next_month(self):
        self.month += 1
        if self.month == 13:
            self.month, self.year = 1, self.year + 1
        self.render()

    def set_data(self, day_totals):
        self.day_totals = day_totals
        self.render()

    def render(self):
        c = self.grid_canvas
        c.delete("all")
        self._hit_boxes = []
        self.month_label.config(text=f"{calmod.month_name[self.month]} {self.year}")

        w = c.winfo_width()
        if w < 60:
            return
        col_w = w / 7
        today_str = date.today().isoformat()

        # Weekday header, then a rule under it - the airy, ruled look of a
        # native calendar rather than a dense grid of boxes.
        for i, name in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            c.create_text(col_w * (i + 0.5), self.HEADER_H / 2, text=name,
                          fill=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9))
        c.create_line(0, self.HEADER_H, w, self.HEADER_H, fill=theme.BORDER)

        first = date(self.year, self.month, 1)
        start = first - timedelta(days=first.weekday())
        weeks = self._weeks_needed(first)
        top = self.HEADER_H

        for week in range(weeks):
            row_top = top + week * self.CELL_H
            if week:
                c.create_line(0, row_top, w, row_top, fill=theme.BORDER)
            for col in range(7):
                day = start + timedelta(days=week * 7 + col)
                in_month = day.month == self.month
                day_str = day.isoformat()
                cx = col_w * (col + 0.5)
                cy = row_top + self.CELL_H / 2
                seconds = self.day_totals.get(day_str, 0)
                is_today = day_str == today_str
                is_selected = day_str == self.selected_day

                if is_selected:
                    c.create_oval(cx - 17, cy - 17, cx + 17, cy + 17,
                                  fill=theme.ACCENT_LIGHT, outline="")
                    fg = "white"
                elif is_today:
                    c.create_oval(cx - 17, cy - 17, cx + 17, cy + 17,
                                  fill=theme.ACCENT, outline="")
                    fg = "white"
                elif not in_month:
                    fg = theme.TEXT_FAINT
                else:
                    fg = theme.TEXT

                weight = "bold" if (is_today or is_selected) else "normal"
                c.create_text(cx, cy - 3, text=str(day.day), fill=fg,
                              font=(theme.FONT_FAMILY, 12, weight))

                if seconds > 0 and not (is_today or is_selected):
                    c.create_oval(cx - 2.5, cy + 12, cx + 2.5, cy + 17,
                                  fill=self.intensity_color(seconds), outline="")

                self._hit_boxes.append((cx - col_w / 2, row_top,
                                        cx + col_w / 2, row_top + self.CELL_H, day_str))

        needed = top + weeks * self.CELL_H + 2
        if int(c.cget("height")) != needed:
            c.config(height=needed)

    def _weeks_needed(self, first_of_month):
        """5 or 6 rows, so short months don't leave a trailing empty week."""
        days = calmod.monthrange(first_of_month.year, first_of_month.month)[1]
        return (first_of_month.weekday() + days + 6) // 7

    def _on_click(self, event):
        for x1, y1, x2, y2, day_str in self._hit_boxes:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.selected_day = None if self.selected_day == day_str else day_str
                self.render()
                if self.on_day_click:
                    self.on_day_click(self.selected_day)
                return

    @staticmethod
    def intensity_color(seconds):
        hours = seconds / 3600
        if hours < 1:
            return theme.CAL_LOW
        if hours < 2:
            return theme.CAL_MED
        if hours < 3:
            return theme.CAL_HIGH
        return theme.CAL_MAX


class ScrollFrame(tk.Frame):
    """Vertically scrollable container. Put content in `.inner`."""

    def __init__(self, parent, bg=theme.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=1, height=1)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                       width=10, troughcolor=bg, bd=0, relief="flat",
                                       activebackground=theme.TEXT_FAINT, bg=theme.BORDER)
        self.canvas.configure(yscrollcommand=self._on_scroll_set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel, add="+")

    def _on_scroll_set(self, first, last):
        # Only show the scrollbar when content actually overflows.
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.set(first, last)

    def _on_inner_configure(self, _e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._window, width=event.width)

    def _on_mousewheel(self, event):
        if not self.winfo_ismapped():
            return
        try:
            first, last = self.canvas.yview()
        except tk.TclError:
            return
        if first <= 0.0 and last >= 1.0:
            return
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta * 2, "units")


class StyledPopup(tk.Toplevel):
    """A themed dropdown panel.

    tk.Menu draws with the OS's native look, which sits badly against the
    rest of the app, so menus are drawn here instead: one canvas holding a
    rounded card, colored dots and hover highlights.

    `items` is a list of dicts:
        {"label": str, "command": callable, "color": hex|None,
         "kind": "normal"|"accent"|"danger"}
    or {"sep": True} for a divider.
    """

    ROW_H = 38
    SEP_H = 9
    PAD = 6
    RADIUS = 12
    TRANSPARENT_KEY = "#FF00FE"

    MIN_W = 168
    MAX_W = 330

    def __init__(self, parent, items, anchor=None, width=None, align="left"):
        super().__init__(parent)
        self.items = list(items)
        self._hover = None
        self._rows = []
        self._width = width or self._auto_width()

        self.overrideredirect(True)
        try:
            self.transient(parent.winfo_toplevel())
        except tk.TclError:
            pass

        # On Windows a key color renders as truly transparent, so the card's
        # rounded corners have nothing boxy behind them. Elsewhere fall back
        # to the page background, which is near-invisible at this radius.
        bg = theme.BG
        try:
            self.attributes("-transparentcolor", self.TRANSPARENT_KEY)
            bg = self.TRANSPARENT_KEY
        except tk.TclError:
            pass
        self.configure(bg=bg)

        height = self.PAD * 2 + sum(
            self.SEP_H if it.get("sep") else self.ROW_H for it in self.items)
        self._height = height

        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Leave>", self._on_leave)

        self.bind("<Escape>", lambda _e: self.dismiss())
        self.bind("<Button-1>", self._maybe_dismiss)

        self._place(anchor, align)
        self._render()

        self.after(10, self._take_grab)

    def _auto_width(self):
        """Widen to fit the longest label, within bounds."""
        try:
            import tkinter.font as tkfont
            font = tkfont.Font(family=theme.FONT_FAMILY, size=10)
            widest = max((font.measure(it["label"]) for it in self.items
                          if not it.get("sep")), default=0)
        except (tk.TclError, ImportError):
            widest = max((len(it.get("label", "")) * 7 for it in self.items), default=0)
        # dot + text + room for the tick on the right
        return int(max(self.MIN_W, min(self.MAX_W, widest + 78)))

    def _fit(self, text, max_px):
        """Trim a label that still doesn't fit, with an ellipsis."""
        try:
            import tkinter.font as tkfont
            font = tkfont.Font(family=theme.FONT_FAMILY, size=10)
        except (tk.TclError, ImportError):
            return text
        if font.measure(text) <= max_px:
            return text
        ell = "..."
        while text and font.measure(text + ell) > max_px:
            text = text[:-1]
        return text.rstrip() + ell

    # ------------------------------------------------------------ placement
    def _place(self, anchor, align):
        if anchor is not None:
            try:
                x = anchor.winfo_rootx()
                y = anchor.winfo_rooty() + anchor.winfo_height() + 4
                if align == "right":
                    x = anchor.winfo_rootx() + anchor.winfo_width() - self._width
            except tk.TclError:
                x = y = 100
        else:
            x, y = self.winfo_pointerxy()

        # keep the panel on screen
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(4, min(x, sw - self._width - 4))
        if y + self._height > sh - 4 and anchor is not None:
            try:
                y = anchor.winfo_rooty() - self._height - 4
            except tk.TclError:
                pass
        y = max(4, min(y, sh - self._height - 4))
        self.geometry(f"{self._width}x{self._height}+{int(x)}+{int(y)}")

    def _take_grab(self):
        try:
            self.grab_set()
            self.focus_set()
        except tk.TclError:
            pass

    # -------------------------------------------------------------- drawing
    def _render(self):
        c = self.canvas
        c.delete("all")
        w, h = self._width, self._height
        round_rect(c, 1, 1, w - 1, h - 1, self.RADIUS,
                   fill=theme.CARD, outline=theme.BORDER, width=1)

        self._rows = []
        y = self.PAD
        for idx, item in enumerate(self.items):
            if item.get("sep"):
                c.create_line(self.PAD + 8, y + self.SEP_H / 2,
                              w - self.PAD - 8, y + self.SEP_H / 2, fill=theme.BORDER)
                y += self.SEP_H
                continue

            hovered = self._hover == idx
            if hovered:
                round_rect(c, self.PAD, y, w - self.PAD, y + self.ROW_H, 9,
                           fill=theme.ACCENT_SOFT, outline="")

            text_x = self.PAD + 14
            color = item.get("color")
            if color is not None:
                cy = y + self.ROW_H / 2
                c.create_oval(text_x, cy - 5, text_x + 10, cy + 5, fill=color, outline="")
                text_x += 18
            elif item.get("swatch"):
                cy = y + self.ROW_H / 2
                c.create_oval(text_x, cy - 5, text_x + 10, cy + 5,
                              outline=theme.TEXT_FAINT, width=1)
                text_x += 18

            kind = item.get("kind", "normal")
            if kind == "danger":
                fg = theme.DANGER
            elif kind == "accent":
                fg = theme.ACCENT
            else:
                fg = theme.ACCENT if hovered else theme.TEXT
            weight = "bold" if kind == "accent" else "normal"

            tick_room = 22 if item.get("checked") else 6
            label = self._fit(item["label"], w - text_x - self.PAD - tick_room)
            c.create_text(text_x, y + self.ROW_H / 2, text=label, anchor="w",
                          fill=fg, font=(theme.FONT_FAMILY, 10, weight))

            if item.get("checked"):
                # drawn rather than a "✓" glyph, which not every font has
                tx, ty = w - self.PAD - 20, y + self.ROW_H / 2
                c.create_line(tx, ty, tx + 4, ty + 4, tx + 11, ty - 5,
                              fill=theme.ACCENT, width=2,
                              capstyle="round", joinstyle="round")

            self._rows.append((y, y + self.ROW_H, idx))
            y += self.ROW_H

    # ------------------------------------------------------------ behaviour
    def _row_at(self, y):
        for top, bottom, idx in self._rows:
            if top <= y <= bottom:
                return idx
        return None

    def _on_motion(self, event):
        idx = self._row_at(event.y)
        if idx != self._hover:
            self._hover = idx
            self.canvas.config(cursor="hand2" if idx is not None else "")
            self._render()

    def _on_leave(self, _event):
        if self._hover is not None:
            self._hover = None
            self._render()

    def _on_click(self, event):
        idx = self._row_at(event.y)
        if idx is None:
            return
        command = self.items[idx].get("command")
        self.dismiss()
        if command:
            command()

    def _maybe_dismiss(self, event):
        # With the grab held, clicks elsewhere in the app arrive here with
        # coordinates outside the panel - that's the "click away" gesture.
        if not (0 <= event.x <= self._width and 0 <= event.y <= self._height):
            self.dismiss()

    def dismiss(self):
        try:
            self.grab_release()
        except tk.TclError:
            pass
        try:
            self.destroy()
        except tk.TclError:
            pass


class PillButton(tk.Canvas):
    """Rounded button used for primary/secondary actions."""

    def __init__(self, parent, text, command, kind="primary", width=150, height=42, bg=theme.CARD):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.text = text
        self.command = command
        self.kind = kind
        self._px_w, self._px_h = width, height
        self._enabled = True
        self.hovered = False
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.render()

    def _on_click(self, _e):
        if self._enabled:
            self.command()

    def _on_enter(self, _e):
        self.hovered = True
        self.render()

    def _on_leave(self, _e):
        self.hovered = False
        self.render()

    def set_text(self, text):
        self.text = text
        self.render()

    def set_enabled(self, enabled):
        self._enabled = enabled
        self.config(cursor="hand2" if enabled else "arrow")
        self.render()

    def set_kind(self, kind):
        self.kind = kind
        self.render()

    def render(self):
        self.delete("all")
        w, h = self._px_w, self._px_h
        if not self._enabled:
            fill, fg, outline = theme.TRACK, theme.TEXT_FAINT, ""
        elif self.kind == "primary":
            fill = theme.ACCENT_LIGHT if self.hovered else theme.ACCENT
            fg, outline = "white", ""
        else:
            fill = theme.ACCENT_SOFT if self.hovered else theme.CARD
            fg, outline = theme.ACCENT, theme.BORDER
        round_rect(self, 1, 1, w - 1, h - 1, (h - 2) / 2, fill=fill,
                   outline=outline, width=1 if outline else 0)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg,
                         font=(theme.FONT_FAMILY, 11, "bold"))


class KebabButton(tk.Canvas):
    """Three-dot row-action button; opens a menu of (label, callback)."""

    def __init__(self, parent, items, bg=theme.CARD, size=28):
        super().__init__(parent, width=size, height=size, bg=bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.items = items
        self._size = size
        self._bg = bg
        self.hovered = False
        self.bind("<Button-1>", self._open)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.render()

    def _on_enter(self, _e):
        self.hovered = True
        self.render()

    def _on_leave(self, _e):
        self.hovered = False
        self.render()

    def render(self):
        self.delete("all")
        s = self._size
        if self.hovered:
            round_rect(self, 1, 1, s - 1, s - 1, 8, fill=theme.ACCENT_SOFT, outline="")
        color = theme.ACCENT if self.hovered else theme.TEXT_MUTED
        for i in range(3):
            cy = s / 2 - 6 + i * 6
            self.create_oval(s / 2 - 1.6, cy - 1.6, s / 2 + 1.6, cy + 1.6,
                             fill=color, outline="")

    def _open(self, _event=None):
        popup_items = []
        for label, callback in self.items:
            if label == "-":
                popup_items.append({"sep": True})
            else:
                popup_items.append({
                    "label": label,
                    "command": callback,
                    "kind": "danger" if label.lower() == "delete" else "normal",
                })
        StyledPopup(self, popup_items, anchor=self, align="right")


class ColorGrid(tk.Frame):
    """Swatch picker; `.get()` returns the chosen color."""

    def __init__(self, parent, colors, selected=None, bg=theme.CARD, per_row=8):
        super().__init__(parent, bg=bg)
        self.colors = list(colors)
        self.bg = bg
        self.selected = selected or self.colors[0]
        self._swatches = {}
        for i, color in enumerate(self.colors):
            sw = tk.Canvas(self, width=34, height=34, bg=bg,
                           highlightthickness=0, cursor="hand2")
            sw.grid(row=i // per_row, column=i % per_row, padx=3, pady=3)
            sw.bind("<Button-1>", lambda _e, cc=color: self.select(cc))
            self._swatches[color] = sw
        self._paint()

    def select(self, color):
        self.selected = color
        self._paint()

    def get(self):
        return self.selected

    def _paint(self):
        for color, sw in self._swatches.items():
            sw.delete("all")
            if color == self.selected:
                round_rect(sw, 1, 1, 33, 33, 11, fill="", outline=theme.ACCENT, width=2)
                round_rect(sw, 5, 5, 29, 29, 8, fill=color, outline="")
            else:
                round_rect(sw, 3, 3, 31, 31, 10, fill=color, outline="")


class Modal(tk.Toplevel):
    """Small themed modal. Subclasses build into `.body` and set `.result`."""

    def __init__(self, parent, title, width=420, height=300):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=theme.CARD)
        self.resizable(False, False)
        try:
            self.transient(parent.winfo_toplevel())
        except tk.TclError:
            pass

        self.body = tk.Frame(self, bg=theme.CARD)
        self.body.pack(fill="both", expand=True, padx=24, pady=20)

        self.buttons = tk.Frame(self, bg=theme.CARD)
        self.buttons.pack(fill="x", padx=24, pady=(0, 20))

        self._width, self._height = width, height
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", lambda _e: self.cancel())

    def add_buttons(self, save_text="Save"):
        PillButton(self.buttons, save_text, self.save, kind="primary",
                    width=120, height=38, bg=theme.CARD).pack(side="right")
        PillButton(self.buttons, "Cancel", self.cancel, kind="ghost",
                    width=110, height=38, bg=theme.CARD).pack(side="right", padx=(0, 8))

    def center_on_parent(self):
        self.update_idletasks()
        w = max(self._width, self.winfo_reqwidth())
        h = max(self._height, self.winfo_reqheight())
        try:
            p = self.master.winfo_toplevel()
            x = p.winfo_rootx() + (p.winfo_width() - w) // 2
            y = p.winfo_rooty() + (p.winfo_height() - h) // 3
        except tk.TclError:
            x = y = 200
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def show(self):
        self.center_on_parent()
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.wait_window()
        return self.result

    def save(self):
        raise NotImplementedError

    def cancel(self):
        self.result = None
        self.destroy()


class SubjectDialog(Modal):
    """Create or edit a subject: name + color."""

    def __init__(self, parent, name="", color=None, title="New Subject"):
        super().__init__(parent, title, width=430, height=300)

        tk.Label(self.body, text="Subject name", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")
        self.name_var = tk.StringVar(value=name)
        entry = tk.Entry(self.body, textvariable=self.name_var, font=(theme.FONT_FAMILY, 11),
                         bg=theme.BG, fg=theme.TEXT, relief="flat", insertbackground=theme.TEXT)
        entry.pack(fill="x", ipady=8, ipadx=8, pady=(8, 0))
        entry.focus_set()
        entry.bind("<Return>", lambda _e: self.save())

        tk.Label(self.body, text="Color", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w", pady=(18, 0))
        tk.Label(self.body, text="Used to color-code this subject on the dashboard.",
                 bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(2, 8))

        self.grid_picker = ColorGrid(self.body, storage.DEFAULT_PALETTE,
                                      selected=color or storage.DEFAULT_PALETTE[0],
                                      per_row=6)
        self.grid_picker.pack(anchor="w")

        self.error = tk.Label(self.body, text="", bg=theme.CARD, fg=theme.DANGER,
                               font=(theme.FONT_FAMILY, 9))
        self.error.pack(anchor="w", pady=(10, 0))

        self.add_buttons()

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            self.error.config(text="Please enter a name.")
            return
        self.result = {"name": name, "color": self.grid_picker.get()}
        self.destroy()


class SessionDialog(Modal):
    """Edit a logged session: subject and length."""

    def __init__(self, parent, session, subjects):
        super().__init__(parent, "Edit Session", width=430, height=320)
        self.subjects = subjects
        self.colors = {s["name"]: s["color"] for s in subjects}

        tk.Label(self.body, text="Subject", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")
        self.subject_var = tk.StringVar(value=session.get("subject", "Unspecified"))
        options = ["Unspecified"] + [s["name"] for s in subjects]
        if self.subject_var.get() not in options:
            options.append(self.subject_var.get())
        menu = tk.OptionMenu(self.body, self.subject_var, *options)
        menu.config(bg=theme.CARD, fg=theme.TEXT, relief="solid", bd=1,
                    font=(theme.FONT_FAMILY, 10), highlightthickness=0,
                    activebackground=theme.ACCENT_SOFT, anchor="w", padx=10)
        menu.pack(fill="x", pady=(8, 0))

        tk.Label(self.body, text="Length", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w", pady=(18, 0))

        secs = int(session.get("seconds", 0))
        row = tk.Frame(self.body, bg=theme.CARD)
        row.pack(anchor="w", pady=(8, 0))
        self.hours_var = tk.StringVar(value=str(secs // 3600))
        self.mins_var = tk.StringVar(value=str((secs % 3600) // 60))
        for var, label, limit in ((self.hours_var, "hours", 99), (self.mins_var, "minutes", 59)):
            tk.Spinbox(row, from_=0, to=limit, textvariable=var, width=4,
                       font=(theme.FONT_FAMILY, 11), justify="center",
                       relief="flat", bg=theme.BG).pack(side="left", ipady=5)
            tk.Label(row, text=label, bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 10)).pack(side="left", padx=(6, 16))

        tk.Label(self.body, text=f"Logged on {session.get('date', '')}", bg=theme.CARD,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(16, 0))

        self.error = tk.Label(self.body, text="", bg=theme.CARD, fg=theme.DANGER,
                               font=(theme.FONT_FAMILY, 9))
        self.error.pack(anchor="w", pady=(8, 0))

        self.add_buttons()

    def save(self):
        try:
            hours = int(self.hours_var.get() or 0)
            minutes = int(self.mins_var.get() or 0)
        except ValueError:
            self.error.config(text="Length must be a number.")
            return
        total = hours * 3600 + minutes * 60
        if total <= 0:
            self.error.config(text="Length must be more than zero.")
            return
        name = self.subject_var.get()
        self.result = {
            "subject": name,
            "color": self.colors.get(name, storage.UNSPECIFIED_COLOR),
            "seconds": total,
        }
        self.destroy()


class SubjectPicker(tk.Frame):
    """Optional subject chooser used to color-code a session.

    Never required: leaving it on "No subject" logs the session as
    "Unspecified" in a neutral color.
    """

    def __init__(self, parent, bg=theme.CARD):
        super().__init__(parent, bg=bg)
        self.bg = bg
        self.subjects = storage.load_subjects()
        self.colors = {s["name"]: s["color"] for s in self.subjects}
        self.selected = tk.StringVar(value="No subject")
        self._locked = False

        tk.Label(self, text="SUBJECT (OPTIONAL)", bg=bg, fg=theme.TEXT_FAINT,
                 font=(theme.FONT_FAMILY, 8, "bold")).pack()

        row = tk.Frame(self, bg=bg)
        row.pack(pady=(8, 0))

        self.chip = tk.Canvas(row, width=210, height=38, bg=bg, highlightthickness=0, cursor="hand2")
        self.chip.pack(side="left")
        self.chip.bind("<Button-1>", self._open_menu)

        add = tk.Canvas(row, width=38, height=38, bg=bg, highlightthickness=0, cursor="hand2")
        round_rect(add, 1, 1, 37, 37, 12, fill=theme.ACCENT_SOFT, outline="")
        add.create_text(19, 19, text="+", fill=theme.ACCENT, font=(theme.FONT_FAMILY, 15, "bold"))
        add.pack(side="left", padx=(8, 0))
        add.bind("<Button-1>", lambda _e: self._add_subject())

        self._render_chip()

    def _render_chip(self):
        name = self.selected.get()
        color = self.colors.get(name)
        self.chip.delete("all")
        round_rect(self.chip, 1, 1, 209, 37, 12, fill=theme.CARD,
                   outline=theme.BORDER, width=1)
        if color:
            self.chip.create_oval(14, 15, 24, 25, fill=color, outline="")
            text_x = 32
        else:
            self.chip.create_oval(14, 15, 24, 25, outline=theme.TEXT_FAINT, width=1)
            text_x = 32
        fg = theme.TEXT_FAINT if self._locked else theme.TEXT
        self.chip.create_text(text_x, 19, text=name, anchor="w", fill=fg,
                              font=(theme.FONT_FAMILY, 10))
        self.chip.create_text(192, 19, text="▾", fill=theme.TEXT_MUTED,
                              font=(theme.FONT_FAMILY, 9))

    def _open_menu(self, _event=None):
        if self._locked:
            return
        current = self.selected.get()
        items = [{
            "label": "No subject",
            "swatch": True,
            "checked": current == "No subject",
            "command": lambda: self._select("No subject"),
        }]
        for s in self.subjects:
            items.append({
                "label": s["name"],
                "color": s["color"],
                "checked": current == s["name"],
                "command": lambda n=s["name"]: self._select(n),
            })
        items.append({"sep": True})
        items.append({"label": "New subject...", "kind": "accent",
                      "command": self._add_subject})
        StyledPopup(self, items, anchor=self.chip)

    def _add_subject(self):
        if self._locked:
            return
        result = SubjectDialog(self, color=storage.next_color(self.subjects)).show()
        if not result:
            return
        name = result["name"]
        if name not in self.colors:
            storage.add_subject(name, result["color"])
            self.subjects = storage.load_subjects()
            self.colors[name] = result["color"]
        self._select(name)

    def _select(self, name):
        self.selected.set(name)
        self._render_chip()

    def refresh_subjects(self):
        self.subjects = storage.load_subjects()
        self.colors = {s["name"]: s["color"] for s in self.subjects}
        if self.selected.get() not in self.colors and self.selected.get() != "No subject":
            self.selected.set("No subject")
        self._render_chip()

    def get_selection(self):
        name = self.selected.get()
        if name == "No subject":
            return "Unspecified", storage.UNSPECIFIED_COLOR
        return name, self.colors.get(name, storage.UNSPECIFIED_COLOR)

    def lock(self):
        self._locked = True
        self._render_chip()

    def unlock(self):
        self._locked = False
        self._render_chip()
