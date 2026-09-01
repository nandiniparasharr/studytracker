"""Dashboard: weekly overview, calendar of logs, subject split and goal."""

import getpass
import tkinter as tk
from datetime import date, datetime, timedelta

import aa
import icons
import storage
import theme
from widgets import (BarChart, DonutChart, PillButton, ProgressBar, RoundedCard,
                     StatCard, StudyCalendar, draw_disc, fmt_hm, round_rect)

FOOTER_QUOTE = "Dreams don't work unless you do."


def greeting_for(hour):
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def display_name():
    name = storage.load_settings().get("display_name", "").strip()
    if name:
        return name
    try:
        return getpass.getuser().split(".")[0].title()
    except Exception:
        return "there"


class DashboardPage(tk.Frame):
    # Vertical budget for "fits on one screen with no scrolling".
    STATS_H = 108          # stat card row (measured from StatCard's content)
    MID_MIN_H = 300        # chart + calendar row
    BOTTOM_MIN_H = 232     # subjects + recent + goal row
    CHROME_H = 150         # header + footer + the gaps between rows
    MIN_H = STATS_H + MID_MIN_H + BOTTOM_MIN_H + CHROME_H

    def __init__(self, parent, on_goto=None):
        super().__init__(parent, bg=theme.BG)
        self.on_goto = on_goto
        self.week_offset = 0
        self.selected_day = None
        self._sessions = []
        self._build()

    # ------------------------------------------------------------- layout
    def _build(self):
        # The dashboard is a fixed set of panels, so it fills the window and
        # lets the two card rows absorb whatever height is going, rather than
        # scrolling. Every row below has a minsize; the window's own minsize
        # is set from their sum so nothing can be squashed out of view.
        root = tk.Frame(self, bg=theme.BG)
        root.pack(fill="both", expand=True)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=3, minsize=self.MID_MIN_H)
        root.grid_rowconfigure(3, weight=2, minsize=self.BOTTOM_MIN_H)
        pad = 26

        header = tk.Frame(root, bg=theme.BG)
        header.grid(row=0, column=0, sticky="ew", padx=pad, pady=(16, 12))

        left = tk.Frame(header, bg=theme.BG)
        left.pack(side="left")
        self.greeting_label = tk.Label(left, text="", bg=theme.BG, fg=theme.TEXT,
                                        font=(theme.FONT_FAMILY, 22, "bold"))
        self.greeting_label.pack(anchor="w")
        tk.Label(left, text="Here's your study overview", bg=theme.BG, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(anchor="w", pady=(2, 0))

        self.range_pill = tk.Canvas(header, width=290, height=42, bg=theme.BG,
                                     highlightthickness=0, cursor="hand2")
        self.range_pill.pack(side="right")
        self.range_pill.bind("<Button-1>", self._on_range_click)

        stats = tk.Frame(root, bg=theme.BG)
        stats.grid(row=1, column=0, sticky="ew", padx=pad)
        self.stat_holders = []
        for i in range(4):
            holder = tk.Frame(stats, bg=theme.BG)
            holder.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            stats.grid_columnconfigure(i, weight=1, uniform="stat")
            self.stat_holders.append(holder)
        stats.grid_rowconfigure(0, minsize=self.STATS_H)

        mid = tk.Frame(root, bg=theme.BG)
        mid.grid(row=2, column=0, sticky="nsew", padx=pad, pady=(12, 0))
        mid.grid_columnconfigure(0, weight=5, uniform="mid")
        mid.grid_columnconfigure(1, weight=4, uniform="mid")
        mid.grid_rowconfigure(0, weight=1)

        chart_card = RoundedCard(mid)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        chart_wrap = tk.Frame(chart_card.body, bg=theme.CARD)
        chart_wrap.pack(fill="both", expand=True, padx=20, pady=16)
        tk.Label(chart_wrap, text="Study Time This Week", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(anchor="w")
        self.bar_chart = BarChart(chart_wrap)
        self.bar_chart.pack(fill="both", expand=True, pady=(10, 0))

        cal_card = RoundedCard(mid)
        cal_card.grid(row=0, column=1, sticky="nsew")
        self.calendar = StudyCalendar(cal_card.body, on_day_click=self._on_day_click)
        self.calendar.pack(fill="both", expand=True, padx=20, pady=16)

        bottom = tk.Frame(root, bg=theme.BG)
        bottom.grid(row=3, column=0, sticky="nsew", padx=pad, pady=(12, 0))
        for i, weight in enumerate((4, 4, 4)):
            bottom.grid_columnconfigure(i, weight=weight, uniform="bot")
        bottom.grid_rowconfigure(0, weight=1)

        self.subjects_card = RoundedCard(bottom)
        self.subjects_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.recent_card = RoundedCard(bottom)
        self.recent_card.grid(row=0, column=1, sticky="nsew", padx=(0, 12))

        self.goal_card = RoundedCard(bottom)
        self.goal_card.grid(row=0, column=2, sticky="nsew")

        footer = tk.Frame(root, bg=theme.BG)
        footer.grid(row=4, column=0, sticky="ew", pady=(10, 12))
        strip = tk.Frame(footer, bg=theme.BG)
        strip.pack()
        tk.Label(strip, text=FOOTER_QUOTE, bg=theme.BG, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(side="left")
        heart = tk.Canvas(strip, width=14, height=14, bg=theme.BG, highlightthickness=0)
        heart.ref = aa.wedge(14, theme.DANGER, theme.BG,
                             [(.50, .28), (.62, .12), (.82, .12), (.95, .28), (.95, .46),
                              (.50, .93), (.05, .46), (.05, .28), (.18, .12), (.38, .12)])
        if heart.ref is not None:
            heart.create_image(0, 0, image=heart.ref, anchor="nw")
        else:
            heart.create_oval(1, 2, 8, 9, fill=theme.DANGER, outline="")
            heart.create_oval(6, 2, 13, 9, fill=theme.DANGER, outline="")
            heart.create_polygon(1.5, 6, 12.5, 6, 7, 13, fill=theme.DANGER, outline="")
        heart.pack(side="left", padx=(6, 0))

    # -------------------------------------------------------------- data
    def refresh(self):
        self._sessions = storage.load_sessions()
        anchor = date.today() + timedelta(weeks=self.week_offset)
        start, end = storage.week_bounds(anchor)

        week = storage.sessions_between(self._sessions, start, end)
        prev_start, prev_end = storage.week_bounds(anchor - timedelta(weeks=1))
        prev_week = storage.sessions_between(self._sessions, prev_start, prev_end)

        self.greeting_label.config(text=f"{greeting_for(datetime.now().hour)}, {display_name()}")
        self._render_range_pill(start, end)
        self._render_stats(week, prev_week)
        self._render_chart(week, start)

        self.calendar.set_data(storage.day_totals(self._sessions))
        self._render_subjects(week)
        self._render_recent()
        self._render_goal(week)

    def _render_range_pill(self, start, end):
        c = self.range_pill
        c.delete("all")
        w, h = 290, 42
        round_rect(c, 1, 1, w - 1, h - 1, 12, fill=theme.CARD, outline=theme.BORDER, width=1)
        icons.draw(c, "calendar", 14, 13, 18, theme.TEXT_MUTED)
        # %-d is not portable (Windows strftime rejects it), so strip the
        # leading zero manually instead.
        label = (f"{start.strftime('%b %d').replace(' 0', ' ')} – "
                 f"{end.strftime('%b %d, %Y').replace(' 0', ' ')}")
        c.create_text(42, h / 2, text=label, anchor="w", fill=theme.TEXT,
                      font=(theme.FONT_FAMILY, 10))
        c.create_line(w - 74, 9, w - 74, h - 9, fill=theme.BORDER)
        c.create_text(w - 56, h / 2, text="‹", fill=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 13))
        c.create_text(w - 24, h / 2, text="›", fill=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 13))

    def _on_range_click(self, event):
        if event.x > 266:
            if self.week_offset < 0:
                self.week_offset += 1
                self.refresh()
        elif event.x > 234:
            self.week_offset -= 1
            self.refresh()

    def _render_stats(self, week, prev_week):
        today_str = date.today().isoformat()
        today_secs = sum(s["seconds"] for s in storage.counted(self._sessions)
                         if s["date"] == today_str)
        y_str = (date.today() - timedelta(days=1)).isoformat()
        yest_secs = sum(s["seconds"] for s in storage.counted(self._sessions)
                        if s["date"] == y_str)

        # Blocks flagged "not study time" stay out of every figure here.
        counted_week = storage.counted(week)
        counted_prev = storage.counted(prev_week)
        week_secs = storage.total_seconds(week)
        prev_secs = storage.total_seconds(prev_week)
        avg = week_secs / len(counted_week) if counted_week else 0
        prev_avg = prev_secs / len(counted_prev) if counted_prev else 0

        cards = [
            ("alarm", "Today", fmt_hm(today_secs), self._pct_delta(today_secs, yest_secs, "vs yesterday")),
            ("calendar", "This Week", fmt_hm(week_secs), self._pct_delta(week_secs, prev_secs, "vs last week")),
            ("people", "Sessions", str(len(counted_week)),
             self._count_delta(len(counted_week), len(counted_prev), "vs last week")),
            ("clock", "Avg. Session", fmt_hm(avg), self._abs_delta(avg, prev_avg, "vs last week")),
        ]

        for holder, (icon, label, value, delta) in zip(self.stat_holders, cards):
            for child in holder.winfo_children():
                child.destroy()
            StatCard(holder, icon, label, value, delta).pack(fill="both", expand=True)

    @staticmethod
    def _pct_delta(current, previous, suffix):
        if not previous:
            return f"{fmt_hm(current)} {suffix}" if current else None
        pct = (current - previous) / previous * 100
        sign = "" if pct >= 0 else "-"
        return f"{sign}{abs(pct):.0f}% {suffix}"

    @staticmethod
    def _count_delta(current, previous, suffix):
        diff = current - previous
        if diff == 0:
            return f"same {suffix}"
        return f"{'' if diff > 0 else '-'}{abs(diff)} {suffix}"

    @staticmethod
    def _abs_delta(current, previous, suffix):
        diff = current - previous
        if abs(diff) < 60:
            return f"same {suffix}"
        return f"{'' if diff > 0 else '-'}{fmt_hm(abs(diff))} {suffix}"

    def _render_chart(self, week, start):
        totals = storage.day_totals(week)
        values = [totals.get((start + timedelta(days=i)).isoformat(), 0) for i in range(7)]
        self.bar_chart.set_values(values)

    def _render_subjects(self, week):
        body = self.subjects_card.body
        for child in body.winfo_children():
            child.destroy()
        wrap = tk.Frame(body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(wrap, text="Subjects Breakdown", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(anchor="w")

        totals = storage.subject_totals(week)
        ranked = sorted(totals.items(), key=lambda kv: -kv[1]["seconds"])
        total_secs = sum(v["seconds"] for v in totals.values())

        row = tk.Frame(wrap, bg=theme.CARD)
        row.pack(fill="both", expand=True, pady=(12, 0))

        donut = DonutChart(row, size=150)
        donut.pack(side="left")
        donut.set_slices([(name, data["seconds"], data["color"]) for name, data in ranked])

        legend_holder = tk.Frame(row, bg=theme.CARD)
        legend_holder.pack(side="left", fill="both", expand=True, padx=(14, 0))
        legend = tk.Frame(legend_holder, bg=theme.CARD)
        legend.place(relx=0, rely=0.5, anchor="w", relwidth=1)

        if not ranked:
            tk.Label(legend, text="No sessions logged\nfor this week yet.", bg=theme.CARD,
                     fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10), justify="left").pack(anchor="w")
            return

        # Grid (not pack) so the name column absorbs the slack and the
        # duration/percent columns stay aligned instead of colliding.
        legend.grid_columnconfigure(1, weight=1)
        for r, (name, data) in enumerate(ranked[:6]):
            dot = tk.Canvas(legend, width=10, height=10, bg=theme.CARD, highlightthickness=0)
            dot.ref = draw_disc(dot, 5, 5, 9, data["color"], theme.CARD)
            dot.grid(row=r, column=0, padx=(0, 7), pady=3)
            tk.Label(legend, text=name, bg=theme.CARD, fg=theme.TEXT,
                     font=(theme.FONT_FAMILY, 9), anchor="w").grid(row=r, column=1, sticky="w")
            tk.Label(legend, text=fmt_hm(data["seconds"]), bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9), anchor="e").grid(row=r, column=2, sticky="e", padx=(8, 0))
            pct = data["seconds"] / total_secs * 100 if total_secs else 0
            tk.Label(legend, text=f"{pct:.0f}%", bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9), width=4, anchor="e").grid(row=r, column=3, sticky="e")

    def _render_recent(self):
        body = self.recent_card.body
        for child in body.winfo_children():
            child.destroy()
        wrap = tk.Frame(body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)

        head = tk.Frame(wrap, bg=theme.CARD)
        head.pack(fill="x")
        title = "Recent Sessions" if not self.selected_day else "Sessions"
        tk.Label(head, text=title, bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(side="left")
        if self.on_goto:
            btn = PillButton(head, "View All", lambda: self.on_goto("sessions"),
                              kind="ghost", width=78, height=28)
            btn.pack(side="right")

        if self.selected_day:
            shown = [s for s in self._sessions if s["date"] == self.selected_day]
            tk.Label(wrap, text=self._pretty_date(self.selected_day), bg=theme.CARD,
                     fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(4, 0))
        else:
            shown = self._sessions[-5:]
        shown = list(reversed(shown))

        if not shown:
            tk.Label(wrap, text="Nothing logged yet.\nHit Start or Timer to begin.", bg=theme.CARD,
                     fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10),
                     justify="left").pack(anchor="w", pady=(14, 0))
            return

        for s in shown[:5]:
            item = tk.Frame(wrap, bg=theme.CARD)
            item.pack(fill="x", pady=5)
            dot = tk.Canvas(item, width=10, height=10, bg=theme.CARD, highlightthickness=0)
            dot.ref = draw_disc(dot, 5, 5, 9, s["color"], theme.CARD)
            dot.pack(side="left", padx=(0, 7))
            tk.Label(item, text=s["subject"], bg=theme.CARD, fg=theme.TEXT,
                     font=(theme.FONT_FAMILY, 9), anchor="w", width=11).pack(side="left")
            tk.Label(item, text=self._relative_day(s["date"]), bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9), anchor="w").pack(side="left")
            tk.Label(item, text=fmt_hm(s["seconds"]), bg=theme.CARD, fg=theme.TEXT,
                     font=(theme.FONT_FAMILY, 9, "bold")).pack(side="right")

    @staticmethod
    def _relative_day(day_str):
        today = date.today()
        d = date.fromisoformat(day_str)
        if d == today:
            return "Today"
        if d == today - timedelta(days=1):
            return "Yesterday"
        return d.strftime("%b %d").replace(" 0", " ")

    @staticmethod
    def _pretty_date(day_str):
        d = date.fromisoformat(day_str)
        return d.strftime("%A, %b %d, %Y").replace(" 0", " ")

    def _render_goal(self, week):
        body = self.goal_card.body
        for child in body.winfo_children():
            child.destroy()
        wrap = tk.Frame(body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)

        head = tk.Frame(wrap, bg=theme.CARD)
        head.pack(fill="x")
        tk.Label(head, text="Weekly Goal", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(side="left")
        if self.on_goto:
            PillButton(head, "Edit", lambda: self.on_goto("goals"),
                        kind="ghost", width=60, height=28).pack(side="right")

        goal_hours = storage.load_settings().get("weekly_goal_hours", 20)
        done = storage.total_seconds(week)
        target = goal_hours * 3600
        ratio = (done / target) if target else 0

        value_row = tk.Frame(wrap, bg=theme.CARD)
        value_row.pack(anchor="w", pady=(16, 0))
        tk.Label(value_row, text=fmt_hm(done), bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 22, "bold")).pack(side="left")
        tk.Label(value_row, text=f" / {goal_hours}h", bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 13)).pack(side="left", pady=(6, 0))

        tk.Label(wrap, text=f"{min(ratio, 9.99) * 100:.0f}% of your weekly goal", bg=theme.CARD,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(8, 0))

        bar_row = tk.Frame(wrap, bg=theme.CARD)
        bar_row.pack(fill="x", pady=(10, 0))
        bar = ProgressBar(bar_row)
        bar.pack(side="left", fill="x", expand=True)
        bar.set_ratio(ratio)

        trophy = tk.Canvas(bar_row, width=56, height=56, bg=theme.CARD, highlightthickness=0)
        trophy.ref = draw_disc(trophy, 28, 28, 56, theme.ACCENT_SOFT, theme.CARD)
        icons.draw(trophy, "trophy", 15, 15, 26, theme.ACCENT, bg=theme.ACCENT_SOFT)
        trophy.pack(side="right", padx=(14, 0))

        remaining = max(0, target - done)
        msg = f"{fmt_hm(remaining)} remaining" if remaining else "Goal reached - nice work!"
        tk.Label(wrap, text=msg, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(10, 0))

    def _on_day_click(self, day_str):
        self.selected_day = day_str
        self._render_recent()
