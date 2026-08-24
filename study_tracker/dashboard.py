"""Dashboard: recent hours, subject color-coding, and a calendar of logs."""

import tkinter as tk
from datetime import date, timedelta

import storage
import theme
from widgets import MiniCalendar, RoundedCard


class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self._build()

    def _build(self):
        pad = 20

        tk.Label(self, text="Dashboard", bg=theme.BG, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 18, "bold")).pack(anchor="w", padx=pad, pady=(pad, 12))

        stats_row = tk.Frame(self, bg=theme.BG)
        stats_row.pack(fill="x", padx=pad)
        self.stat_cards = {}
        for i, key in enumerate(["today", "week", "sessions", "top_subject"]):
            card = RoundedCard(stats_row, bg=theme.CARD, radius=14)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            stats_row.grid_columnconfigure(i, weight=1)
            self.stat_cards[key] = card

        mid_row = tk.Frame(self, bg=theme.BG)
        mid_row.pack(fill="both", expand=True, padx=pad, pady=pad)
        mid_row.grid_columnconfigure(0, weight=3)
        mid_row.grid_columnconfigure(1, weight=2)
        mid_row.grid_rowconfigure(0, weight=1)
        mid_row.grid_rowconfigure(1, weight=1)

        self.subjects_card = RoundedCard(mid_row, bg=theme.CARD, radius=14)
        self.subjects_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        self.calendar_card = RoundedCard(mid_row, bg=theme.CARD, radius=14)
        self.calendar_card.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        self.calendar = MiniCalendar(self.calendar_card.body, bg=theme.CARD, on_day_click=self._show_day)
        self.calendar.pack(fill="both", expand=True, padx=14, pady=14)

        self.recent_card = RoundedCard(mid_row, bg=theme.CARD, radius=14)
        self.recent_card.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self._all_sessions = []

    def refresh(self):
        sessions = storage.load_sessions()
        self._all_sessions = sessions
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        today_secs = sum(s["seconds"] for s in sessions if s["date"] == today.isoformat())
        week_sessions = [s for s in sessions if date.fromisoformat(s["date"]) >= week_start]
        week_secs = sum(s["seconds"] for s in week_sessions)

        subject_totals = {}
        for s in week_sessions:
            entry = subject_totals.setdefault(s["subject"], {"seconds": 0, "color": s["color"]})
            entry["seconds"] += s["seconds"]
        top_subject = max(subject_totals.items(), key=lambda kv: kv[1]["seconds"])[0] if subject_totals else "-"

        self._render_stat("today", "Today", self._fmt_hours(today_secs), theme.ORANGE)
        self._render_stat("week", "This Week", self._fmt_hours(week_secs), theme.NAVY)
        self._render_stat("sessions", "Sessions (Week)", str(len(week_sessions)), theme.GREEN)
        self._render_stat("top_subject", "Top Subject", top_subject, theme.RED)

        self._render_subjects(subject_totals)

        day_totals = {}
        for s in sessions:
            day_totals[s["date"]] = day_totals.get(s["date"], 0) + s["seconds"]
        self.calendar.set_data(day_totals)

        self._render_recent(list(reversed(sessions[-8:])))

    @staticmethod
    def _fmt_hours(seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m"

    def _render_stat(self, key, label, value, accent):
        card = self.stat_cards[key]
        for w in card.body.winfo_children():
            w.destroy()
        tk.Frame(card.body, bg=accent, height=4).pack(fill="x", side="top")
        inner = tk.Frame(card.body, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=12)
        tk.Label(inner, text=label, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w")
        tk.Label(inner, text=value, bg=theme.CARD, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 16, "bold")).pack(anchor="w", pady=(4, 0))

    def _render_subjects(self, subject_totals):
        for w in self.subjects_card.body.winfo_children():
            w.destroy()
        wrap = tk.Frame(self.subjects_card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(wrap, text="Subjects This Week", bg=theme.CARD, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 12, "bold")).pack(anchor="w", pady=(0, 10))

        if not subject_totals:
            tk.Label(wrap, text="No sessions logged yet this week.", bg=theme.CARD,
                      fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            return

        max_secs = max(v["seconds"] for v in subject_totals.values())
        for name, data in sorted(subject_totals.items(), key=lambda kv: -kv[1]["seconds"]):
            row = tk.Frame(wrap, bg=theme.CARD)
            row.pack(fill="x", pady=4)
            tk.Frame(row, bg=data["color"], width=10, height=10).pack(side="left", padx=(0, 8))
            tk.Label(row, text=name, bg=theme.CARD, fg=theme.TEXT_DARK, font=(theme.FONT_FAMILY, 10),
                     width=14, anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg=theme.BG, height=10)
            bar_bg.pack(side="left", fill="x", expand=True, padx=8)
            ratio = max(data["seconds"] / max_secs, 0.03) if max_secs else 0.03
            tk.Frame(bar_bg, bg=data["color"], height=10).place(relx=0, rely=0, relwidth=ratio, relheight=1)
            tk.Label(row, text=self._fmt_hours(data["seconds"]), bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9)).pack(side="left", padx=(8, 0))

    def _render_recent(self, sessions):
        for w in self.recent_card.body.winfo_children():
            w.destroy()
        wrap = tk.Frame(self.recent_card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=16, pady=14)
        tk.Label(wrap, text="Recent Sessions", bg=theme.CARD, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 12, "bold")).pack(anchor="w", pady=(0, 10))

        if not sessions:
            tk.Label(wrap, text="Nothing logged yet - hit Start or Timer to begin.",
                      bg=theme.CARD, fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            return

        for s in sessions:
            row = tk.Frame(wrap, bg=theme.CARD)
            row.pack(fill="x", pady=3)
            tk.Frame(row, bg=s["color"], width=10, height=10).pack(side="left", padx=(0, 8))
            tk.Label(row, text=s["subject"], bg=theme.CARD, fg=theme.TEXT_DARK, font=(theme.FONT_FAMILY, 10),
                     width=14, anchor="w").pack(side="left")
            tk.Label(row, text=s["date"], bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9), width=11, anchor="w").pack(side="left")
            tk.Label(row, text=self._fmt_hours(s["seconds"]), bg=theme.CARD, fg=theme.TEXT_DARK,
                     font=(theme.FONT_FAMILY, 9, "bold")).pack(side="right")

    def _show_day(self, day_str):
        sessions = [s for s in self._all_sessions if s["date"] == day_str]
        self._render_recent(list(reversed(sessions)))
