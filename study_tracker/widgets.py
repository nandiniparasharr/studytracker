"""Reusable UI pieces shared by the dashboard, start and timer pages."""

import calendar
import tkinter as tk
from datetime import date
from tkinter import simpledialog

import storage
import theme


class RoundedCard(tk.Frame):
    """A flat 'card' panel with rounded corners, drawn on a canvas.

    Put content inside `.body` (a plain tk.Frame) - it behaves like any
    other container.
    """

    def __init__(self, parent, bg=theme.CARD, radius=14, **kwargs):
        try:
            parent_bg = parent.cget("bg")
        except tk.TclError:
            parent_bg = theme.BG
        super().__init__(parent, bg=parent_bg, **kwargs)
        self._radius = radius
        self._bg = bg

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=parent_bg)
        self.canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window(2, 2, window=self.body, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 8 or h < 8:
            return
        self.canvas.delete("card_bg")
        self._draw_rounded_rect(1, 1, w - 1, h - 1, self._radius, fill=self._bg, outline="", tags="card_bg")
        self.canvas.tag_lower("card_bg")
        self.canvas.coords(self._window, 2, 2)
        self.canvas.itemconfig(self._window, width=w - 4, height=h - 4)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)


class NavButton(tk.Frame):
    """A clickable sidebar entry with an accent bar when active."""

    def __init__(self, parent, text, icon, command, active=False):
        super().__init__(parent, bg=theme.NAVY_DARK, cursor="hand2")
        self.command = command
        self.active = active

        self.accent = tk.Frame(self, width=4, bg=theme.ORANGE if active else theme.NAVY_DARK)
        self.accent.pack(side="left", fill="y")

        self.label = tk.Label(
            self, text=f"  {icon}   {text}",
            bg=theme.NAVY if active else theme.NAVY_DARK,
            fg="white" if active else "#c7d0e0",
            font=(theme.FONT_FAMILY, 11), anchor="w", padx=10, pady=13,
        )
        self.label.pack(side="left", fill="both", expand=True)

        for widget in (self, self.label):
            widget.bind("<Button-1>", lambda e: self.command())
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def set_active(self, active):
        self.active = active
        self.accent.config(bg=theme.ORANGE if active else theme.NAVY_DARK)
        self.label.config(
            bg=theme.NAVY if active else theme.NAVY_DARK,
            fg="white" if active else "#c7d0e0",
        )

    def _on_enter(self, _event):
        if not self.active:
            self.label.config(bg=theme.NAVY_LIGHT)

    def _on_leave(self, _event):
        if not self.active:
            self.label.config(bg=theme.NAVY_DARK)


class MiniCalendar(tk.Frame):
    """A month grid; days are shaded by how much study time was logged."""

    def __init__(self, parent, bg=theme.CARD, on_day_click=None):
        super().__init__(parent, bg=bg)
        self.bg = bg
        self.on_day_click = on_day_click
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.day_totals = {}

        header = tk.Frame(self, bg=bg)
        header.pack(fill="x")
        tk.Button(header, text="<", command=self._prev_month, bd=0, bg=bg, fg=theme.TEXT_MUTED,
                  activebackground=bg, cursor="hand2", font=(theme.FONT_FAMILY, 10, "bold")).pack(side="left")
        self.title_label = tk.Label(header, text="", bg=bg, fg=theme.TEXT_DARK,
                                     font=(theme.FONT_FAMILY, 11, "bold"))
        self.title_label.pack(side="left", expand=True)
        tk.Button(header, text=">", command=self._next_month, bd=0, bg=bg, fg=theme.TEXT_MUTED,
                  activebackground=bg, cursor="hand2", font=(theme.FONT_FAMILY, 10, "bold")).pack(side="right")

        self.grid_frame = tk.Frame(self, bg=bg)
        self.grid_frame.pack(fill="both", expand=True, pady=(10, 0))

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
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.title_label.config(text=f"{calendar.month_name[self.month]} {self.year}")

        for col, label in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            tk.Label(self.grid_frame, text=label, bg=self.bg, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 8, "bold"), width=3).grid(row=0, column=col, pady=(0, 4))

        weeks = calendar.monthcalendar(self.year, self.month)
        today_str = date.today().isoformat()
        for row, week in enumerate(weeks, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    continue
                day_str = date(self.year, self.month, day).isoformat()
                seconds = self.day_totals.get(day_str, 0)
                bg_color = self._intensity_color(seconds)
                is_today = day_str == today_str
                cell = tk.Label(
                    self.grid_frame, text=str(day), width=3, height=1,
                    bg=bg_color, fg="white" if seconds > 0 else theme.TEXT_DARK,
                    font=(theme.FONT_FAMILY, 9, "bold" if is_today else "normal"),
                    relief="solid" if is_today else "flat", bd=1 if is_today else 0,
                    highlightbackground=theme.ORANGE, cursor="hand2",
                )
                cell.grid(row=row, column=col, padx=2, pady=2)
                cell.bind("<Button-1>", lambda _e, d=day_str: self.on_day_click and self.on_day_click(d))

    @staticmethod
    def _intensity_color(seconds):
        if seconds <= 0:
            return theme.BG
        hours = seconds / 3600
        if hours < 1:
            return "#fde4b0"
        if hours < 2:
            return "#fbc76b"
        if hours < 4:
            return theme.ORANGE
        return theme.ORANGE_DARK


class SubjectPicker(tk.Frame):
    """Optional subject dropdown used to color-code a session.

    Never required: leaving it on "No subject" logs the session as
    "Unspecified" in a neutral color.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=theme.CARD)
        self.subjects = storage.load_subjects()
        self.colors = {s["name"]: s["color"] for s in self.subjects}
        self.selected = tk.StringVar(value="No subject")

        tk.Label(self, text="Subject (optional)", bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w")

        row = tk.Frame(self, bg=theme.CARD)
        row.pack(pady=(4, 0))

        self.swatch = tk.Frame(row, bg=theme.BORDER, width=14, height=14)
        self.swatch.pack(side="left", padx=(0, 6))

        names = ["No subject"] + [s["name"] for s in self.subjects]
        self.menu = tk.OptionMenu(row, self.selected, *names, command=self._on_change)
        self.menu.config(bg=theme.CARD, fg=theme.TEXT_DARK, bd=1, relief="solid",
                          font=(theme.FONT_FAMILY, 10), highlightthickness=0, padx=8)
        self.menu.pack(side="left")

        tk.Button(row, text="+ New", command=self._add_subject, bd=0, bg=theme.CARD,
                  fg=theme.ORANGE_DARK, font=(theme.FONT_FAMILY, 9, "bold"),
                  activebackground=theme.CARD, cursor="hand2").pack(side="left", padx=(8, 0))

    def _on_change(self, value):
        self.swatch.config(bg=self.colors.get(value, theme.BORDER))

    def _add_subject(self):
        name = simpledialog.askstring("New Subject", "Subject name:", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.colors:
            self._select(name)
            return
        color = storage.next_color(self.subjects)
        storage.add_subject(name, color)
        self.subjects = storage.load_subjects()
        self.colors[name] = color
        self.menu["menu"].add_command(label=name, command=lambda v=name: self._select(v))
        self._select(name)

    def _select(self, name):
        self.selected.set(name)
        self._on_change(name)

    def get_selection(self):
        name = self.selected.get()
        if name == "No subject":
            return "Unspecified", storage.UNSPECIFIED_COLOR
        return name, self.colors.get(name, storage.UNSPECIFIED_COLOR)

    def lock(self):
        self.menu.config(state="disabled")

    def unlock(self):
        self.menu.config(state="normal")
