"""Sessions, Subjects, Reports, Goals and Settings sections."""

import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, simpledialog

import icons
import storage
import theme
from widgets import (BarChart, KebabButton, PillButton, ProgressBar, RoundedCard,
                     ScrollFrame, SessionDialog, SubjectDialog, fmt_hm, round_rect)


class _Page(tk.Frame):
    """Shared page chrome: title, subtitle and a scrolling body."""

    title = ""
    subtitle = ""

    def __init__(self, parent, on_changed=None):
        super().__init__(parent, bg=theme.BG)
        self.on_changed = on_changed
        scroller = ScrollFrame(self, bg=theme.BG)
        scroller.pack(fill="both", expand=True)
        self.root = scroller.inner

        head = tk.Frame(self.root, bg=theme.BG)
        head.pack(fill="x", padx=26, pady=(24, 18))
        tk.Label(head, text=self.title, bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 25, "bold")).pack(anchor="w")
        if self.subtitle:
            tk.Label(head, text=self.subtitle, bg=theme.BG, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 11)).pack(anchor="w", pady=(4, 0))

        self.content = tk.Frame(self.root, bg=theme.BG)
        self.content.pack(fill="both", expand=True, padx=26, pady=(0, 26))

    def _clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _sync_cards(self, parent=None):
        """Let every card grow to fit what was just rendered into it."""
        for child in (parent or self.content).winfo_children():
            if isinstance(child, RoundedCard):
                child.sync_height()
            else:
                self._sync_cards(child)

    def _notify(self):
        if self.on_changed:
            self.on_changed()


class SessionsPage(_Page):
    title = "Sessions"
    subtitle = "Every study block you've logged"

    def on_show(self):
        self.refresh()

    def refresh(self):
        self._clear()
        sessions = list(reversed(storage.load_sessions()))

        card = RoundedCard(self.content)
        card.pack(fill="both", expand=True)
        wrap = tk.Frame(card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)

        if not sessions:
            tk.Label(wrap, text="No sessions yet. Start the stopwatch or a timer block.",
                     bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            self._sync_cards()
            return

        header = tk.Frame(wrap, bg=theme.CARD)
        header.pack(fill="x", pady=(0, 8))
        for text, width, side in (("SUBJECT", 16, "left"), ("DATE", 14, "left"),
                                   ("TIME", 18, "left"), ("MODE", 20, "left")):
            tk.Label(header, text=text, bg=theme.CARD, fg=theme.TEXT_FAINT, width=width,
                     anchor="w", font=(theme.FONT_FAMILY, 8, "bold")).pack(side=side)
        tk.Label(header, text="LENGTH", bg=theme.CARD, fg=theme.TEXT_FAINT,
                 font=(theme.FONT_FAMILY, 8, "bold")).pack(side="right", padx=(0, 44))

        tk.Frame(wrap, bg=theme.BORDER, height=1).pack(fill="x")

        for s in sessions[:200]:
            self._row(wrap, s)
        self._sync_cards()

    def _row(self, parent, session):
        row = tk.Frame(parent, bg=theme.CARD)
        row.pack(fill="x", pady=6)

        subject = tk.Frame(row, bg=theme.CARD, width=16)
        subject.pack(side="left")
        dot = tk.Canvas(subject, width=10, height=10, bg=theme.CARD, highlightthickness=0)
        dot.create_oval(1, 1, 9, 9, fill=session["color"], outline="")
        dot.pack(side="left", padx=(0, 7))
        tk.Label(subject, text=session["subject"], bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 10), anchor="w", width=13).pack(side="left")

        d = date.fromisoformat(session["date"])
        tk.Label(row, text=d.strftime("%b %d, %Y").replace(" 0", " "), bg=theme.CARD,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10), width=14,
                 anchor="w").pack(side="left")

        started = storage.parse_time(session["started_at"])
        ended = storage.parse_time(session["ended_at"])
        span = (f"{started.strftime('%I:%M %p').lstrip('0')} - {ended.strftime('%I:%M %p').lstrip('0')}"
                if started and ended else "-")
        tk.Label(row, text=span, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10), width=18, anchor="w").pack(side="left")

        mode = session.get("kind", "").title()
        if not storage.counts_toward_study(session):
            mode += "  ·  not counted"
        tk.Label(row, text=mode, bg=theme.CARD,
                 fg=theme.TEXT_MUTED if storage.counts_toward_study(session) else theme.TEXT_FAINT,
                 font=(theme.FONT_FAMILY, 10), width=20, anchor="w").pack(side="left")

        KebabButton(row, [
            ("Edit", lambda s=session: self._edit(s)),
            ("-", None),
            ("Delete", lambda sid=session["id"]: self._delete(sid)),
        ]).pack(side="right")
        tk.Label(row, text=fmt_hm(session["seconds"]), bg=theme.CARD,
                 fg=theme.TEXT if storage.counts_toward_study(session) else theme.TEXT_FAINT,
                 font=(theme.FONT_FAMILY, 10, "bold")).pack(side="right", padx=(0, 16))

    def _edit(self, session):
        result = SessionDialog(self, session, storage.load_subjects()).show()
        if result:
            storage.update_session(session["id"], **result)
            self.refresh()
            self._notify()

    def _delete(self, session_id):
        if messagebox.askyesno("Delete session", "Delete this session from your log?", parent=self):
            storage.delete_session(session_id)
            self.refresh()
            self._notify()


class SubjectsPage(_Page):
    title = "Subjects"
    subtitle = "Optional labels that color-code your sessions"

    def on_show(self):
        self.refresh()

    def refresh(self):
        self._clear()
        subjects = storage.load_subjects()
        totals = storage.subject_totals(storage.load_sessions())

        card = RoundedCard(self.content)
        card.pack(fill="both", expand=True)
        wrap = tk.Frame(card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)

        head = tk.Frame(wrap, bg=theme.CARD)
        head.pack(fill="x", pady=(0, 12))
        tk.Label(head, text="Your Subjects", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(side="left")
        PillButton(head, "+ Add Subject", self._add, kind="primary",
                    width=146, height=32).pack(side="right")

        tk.Label(wrap, text="Subjects are never required - you can always start a session without one.",
                 bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(0, 12))

        if not subjects:
            tk.Label(wrap, text="No subjects yet.", bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            self._sync_cards()
            return

        for s in subjects:
            row = tk.Frame(wrap, bg=theme.CARD)
            row.pack(fill="x", pady=6)

            swatch = tk.Canvas(row, width=26, height=26, bg=theme.CARD,
                                highlightthickness=0, cursor="hand2")
            round_rect(swatch, 1, 1, 25, 25, 8, fill=s["color"], outline="")
            swatch.pack(side="left", padx=(0, 10))
            swatch.bind("<Button-1>", lambda _e, sub=dict(s): self._edit(sub))

            tk.Label(row, text=s["name"], bg=theme.CARD, fg=theme.TEXT,
                     font=(theme.FONT_FAMILY, 11), anchor="w", width=20).pack(side="left")

            logged = totals.get(s["name"], {}).get("seconds", 0)
            tk.Label(row, text=f"{fmt_hm(logged)} logged", bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9)).pack(side="left")

            KebabButton(row, [
                ("Edit", lambda sub=dict(s): self._edit(sub)),
                ("-", None),
                ("Delete", lambda n=s["name"]: self._delete(n)),
            ]).pack(side="right")
        self._sync_cards()

    def _add(self):
        subjects = storage.load_subjects()
        result = SubjectDialog(self, color=storage.next_color(subjects)).show()
        if not result:
            return
        if any(s["name"].lower() == result["name"].lower() for s in subjects):
            messagebox.showinfo("Subject exists", f"'{result['name']}' is already on your list.",
                                parent=self)
            return
        storage.add_subject(result["name"], result["color"])
        self.refresh()
        self._notify()

    def _edit(self, subject):
        result = SubjectDialog(self, name=subject["name"], color=subject["color"],
                                title="Edit Subject").show()
        if not result:
            return
        if not storage.edit_subject(subject["name"], result["name"], result["color"]):
            messagebox.showinfo("Subject exists", f"'{result['name']}' is already on your list.",
                                parent=self)
            return
        self.refresh()
        self._notify()

    def _delete(self, name):
        if messagebox.askyesno(
            "Delete subject",
            f"Remove '{name}'?\n\nSessions already logged under it keep their label.",
            parent=self,
        ):
            storage.delete_subject(name)
            self.refresh()
            self._notify()


class ReportsPage(_Page):
    title = "Reports"
    subtitle = "How your study time trends over time"

    def on_show(self):
        self.refresh()

    def refresh(self):
        self._clear()
        sessions = storage.load_sessions()

        top = tk.Frame(self.content, bg=theme.BG)
        top.pack(fill="x")
        for i in range(3):
            top.grid_columnconfigure(i, weight=1, uniform="rep")
        top.grid_rowconfigure(0, minsize=104)

        today = date.today()
        this_week = storage.sessions_between(sessions, *storage.week_bounds(today))
        last_week = storage.sessions_between(sessions, *storage.week_bounds(today - timedelta(weeks=1)))
        month_sessions = [s for s in sessions if s["date"][:7] == today.isoformat()[:7]]

        cards = [
            ("This Week", fmt_hm(storage.total_seconds(this_week))),
            ("Last Week", fmt_hm(storage.total_seconds(last_week))),
            ("This Month", fmt_hm(storage.total_seconds(month_sessions))),
        ]
        for i, (label, value) in enumerate(cards):
            card = RoundedCard(top)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            inner = tk.Frame(card.body, bg=theme.CARD)
            inner.pack(fill="both", expand=True, padx=20, pady=16)
            tk.Label(inner, text=label, bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            tk.Label(inner, text=value, bg=theme.CARD, fg=theme.TEXT,
                     font=(theme.FONT_FAMILY, 20, "bold")).pack(anchor="w", pady=(4, 0))

        chart_card = RoundedCard(self.content)
        chart_card.pack(fill="both", expand=True, pady=(16, 0))
        wrap = tk.Frame(chart_card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(wrap, text="Last 8 Weeks", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(anchor="w")

        chart = BarChart(wrap)
        chart.config(height=240)
        chart.pack(fill="both", expand=True, pady=(12, 0))

        values, labels = [], []
        for back in range(7, -1, -1):
            start, end = storage.week_bounds(today - timedelta(weeks=back))
            values.append(storage.total_seconds(storage.sessions_between(sessions, start, end)))
            labels.append(start.strftime("%b %d").replace(" 0", " "))
        chart.set_values(values, labels)

        subj_card = RoundedCard(self.content)
        subj_card.pack(fill="x", pady=(16, 0))
        sw = tk.Frame(subj_card.body, bg=theme.CARD)
        sw.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(sw, text="All-Time by Subject", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(anchor="w", pady=(0, 10))

        totals = storage.subject_totals(sessions)
        if not totals:
            tk.Label(sw, text="Nothing logged yet.", bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
            self._sync_cards()
            return

        peak = max(v["seconds"] for v in totals.values())
        for name, data in sorted(totals.items(), key=lambda kv: -kv[1]["seconds"]):
            row = tk.Frame(sw, bg=theme.CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=name, bg=theme.CARD, fg=theme.TEXT, width=16, anchor="w",
                     font=(theme.FONT_FAMILY, 10)).pack(side="left")
            track = tk.Frame(row, bg=theme.TRACK, height=8)
            track.pack(side="left", fill="x", expand=True, padx=10)
            tk.Frame(track, bg=data["color"], height=8).place(
                relx=0, rely=0, relwidth=max(data["seconds"] / peak, 0.02), relheight=1)
            tk.Label(row, text=fmt_hm(data["seconds"]), bg=theme.CARD, fg=theme.TEXT_MUTED,
                     font=(theme.FONT_FAMILY, 9), width=9, anchor="e").pack(side="left")
        self._sync_cards()


class GoalsPage(_Page):
    title = "Goals"
    subtitle = "Set the weekly target you're working towards"

    def on_show(self):
        self.refresh()

    def refresh(self):
        self._clear()
        settings = storage.load_settings()
        goal_hours = settings.get("weekly_goal_hours", 20)
        sessions = storage.load_sessions()
        week = storage.sessions_between(sessions, *storage.week_bounds())
        done = storage.total_seconds(week)
        target = goal_hours * 3600
        ratio = done / target if target else 0

        card = RoundedCard(self.content)
        card.pack(fill="x")
        wrap = tk.Frame(card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=24, pady=22)

        tk.Label(wrap, text="Weekly Goal", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(anchor="w")

        row = tk.Frame(wrap, bg=theme.CARD)
        row.pack(anchor="w", pady=(16, 0))
        tk.Label(row, text=fmt_hm(done), bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 26, "bold")).pack(side="left")
        tk.Label(row, text=f" / {goal_hours}h this week", bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 13)).pack(side="left", pady=(8, 0))

        bar = ProgressBar(wrap, height=11)
        bar.pack(fill="x", pady=(14, 0))
        bar.set_ratio(ratio)

        remaining = max(0, target - done)
        msg = f"{fmt_hm(remaining)} remaining this week" if remaining else "Goal reached - nice work!"
        tk.Label(wrap, text=msg, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(anchor="w", pady=(10, 0))

        tk.Frame(wrap, bg=theme.BORDER, height=1).pack(fill="x", pady=18)

        tk.Label(wrap, text="Target hours per week", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")

        picker = tk.Frame(wrap, bg=theme.CARD)
        picker.pack(anchor="w", pady=(12, 0))
        for hours in (5, 10, 15, 20, 25, 30, 40):
            chip = tk.Canvas(picker, width=56, height=36, bg=theme.CARD,
                             highlightthickness=0, cursor="hand2")
            active = hours == goal_hours
            round_rect(chip, 1, 1, 55, 35, 11,
                       fill=theme.ACCENT if active else theme.CARD,
                       outline="" if active else theme.BORDER, width=0 if active else 1)
            chip.create_text(28, 18, text=f"{hours}h", fill="white" if active else theme.TEXT_MUTED,
                             font=(theme.FONT_FAMILY, 10, "bold"))
            chip.pack(side="left", padx=(0, 8))
            chip.bind("<Button-1>", lambda _e, h=hours: self._set_goal(h))

        PillButton(wrap, "Custom…", self._custom_goal, kind="ghost",
                    width=110, height=34).pack(anchor="w", pady=(14, 0))

        streak = storage.current_streak(sessions)
        streak_card = RoundedCard(self.content)
        streak_card.pack(fill="x", pady=(16, 0))
        sw = tk.Frame(streak_card.body, bg=theme.CARD)
        sw.pack(fill="both", expand=True, padx=24, pady=20)
        flame = tk.Canvas(sw, width=40, height=40, bg=theme.CARD, highlightthickness=0)
        flame.create_oval(0, 0, 39, 39, fill=theme.ACCENT_SOFT, outline="")
        icons.draw(flame, "flame", 11, 10, 18, theme.ACCENT)
        flame.pack(side="left", padx=(0, 14))
        text = tk.Frame(sw, bg=theme.CARD)
        text.pack(side="left")
        tk.Label(text, text="Current Streak", bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(anchor="w")
        tk.Label(text, text=f"{streak} day{'s' if streak != 1 else ''}", bg=theme.CARD,
                 fg=theme.TEXT, font=(theme.FONT_FAMILY, 17, "bold")).pack(anchor="w")
        self._sync_cards()

    def _set_goal(self, hours):
        settings = storage.load_settings()
        settings["weekly_goal_hours"] = hours
        storage.save_settings(settings)
        self.refresh()
        self._notify()

    def _custom_goal(self):
        hours = simpledialog.askinteger("Weekly goal", "Target hours per week:",
                                         parent=self, minvalue=1, maxvalue=168)
        if hours:
            self._set_goal(hours)


class SettingsPage(_Page):
    title = "Settings"
    subtitle = "Preferences and your local data"

    def on_show(self):
        self.refresh()

    def refresh(self):
        self._clear()
        settings = storage.load_settings()

        card = RoundedCard(self.content)
        card.pack(fill="x")
        wrap = tk.Frame(card.body, bg=theme.CARD)
        wrap.pack(fill="both", expand=True, padx=24, pady=22)

        tk.Label(wrap, text="Display name", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")
        tk.Label(wrap, text="Shown in the dashboard greeting.", bg=theme.CARD,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(2, 8))

        name_row = tk.Frame(wrap, bg=theme.CARD)
        name_row.pack(anchor="w")
        self.name_var = tk.StringVar(value=settings.get("display_name", ""))
        entry = tk.Entry(name_row, textvariable=self.name_var, font=(theme.FONT_FAMILY, 11),
                         bg=theme.BG, fg=theme.TEXT, relief="flat", width=24,
                         insertbackground=theme.TEXT)
        entry.pack(side="left", ipady=7, ipadx=8)
        PillButton(name_row, "Save", self._save_name, kind="primary",
                    width=88, height=34).pack(side="left", padx=(10, 0))

        tk.Frame(wrap, bg=theme.BORDER, height=1).pack(fill="x", pady=20)

        tk.Label(wrap, text="Where your data lives", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")
        tk.Label(wrap, text=storage.DATA_DIR, bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9), wraplength=560,
                 justify="left").pack(anchor="w", pady=(4, 0))
        tk.Label(wrap, text="Plain JSON files on this computer. Nothing is uploaded anywhere.",
                 bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(6, 0))

        tk.Frame(wrap, bg=theme.BORDER, height=1).pack(fill="x", pady=20)

        sessions = storage.load_sessions()
        tk.Label(wrap, text="Your log", bg=theme.CARD, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")
        tk.Label(wrap,
                 text=f"{len(storage.counted(sessions))} study sessions · "
                      f"{fmt_hm(storage.total_seconds(sessions))} tracked in total",
                 bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(4, 10))
        PillButton(wrap, "Clear all sessions", self._clear_sessions, kind="ghost",
                    width=160, height=34).pack(anchor="w")
        self._sync_cards()

    def _save_name(self):
        settings = storage.load_settings()
        settings["display_name"] = self.name_var.get().strip()
        storage.save_settings(settings)
        self._notify()
        messagebox.showinfo("Settings", "Display name saved.", parent=self)

    def _clear_sessions(self):
        if messagebox.askyesno(
            "Clear all sessions",
            "Delete every logged session permanently?\n\nThis cannot be undone.",
            parent=self,
        ):
            storage._save_json(storage.SESSIONS_FILE, [])
            self.refresh()
            self._notify()
