"""'Timer' section: a countdown timer for focused study blocks."""

import tkinter as tk
from datetime import datetime

import storage
import theme
from widgets import RoundedCard, SubjectPicker

MIN_SECONDS_TO_SAVE = 5
TICK_MS = 500
DEFAULT_MINUTES = 25


class TimerPage(tk.Frame):
    def __init__(self, parent, on_session_saved=None):
        super().__init__(parent, bg=theme.BG)
        self.on_session_saved = on_session_saved
        self.running = False
        self.total_seconds = 0
        self.remaining = 0
        self.start_time = None
        self._tick_mark = None
        self._after_id = None
        self._build()

    def _build(self):
        pad = 20
        tk.Label(self, text="Timer", bg=theme.BG, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 18, "bold")).pack(anchor="w", padx=pad, pady=(pad, 12))

        card = RoundedCard(self, bg=theme.CARD, radius=18)
        card.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body = tk.Frame(card.body, bg=theme.CARD)
        body.place(relx=0.5, rely=0.5, anchor="center")

        self.subject_picker = SubjectPicker(body)
        self.subject_picker.pack(pady=(0, 16))

        set_row = tk.Frame(body, bg=theme.CARD)
        set_row.pack(pady=6)
        tk.Label(set_row, text="Minutes:", bg=theme.CARD, fg=theme.TEXT_MUTED,
                 font=(theme.FONT_FAMILY, 10)).pack(side="left", padx=(0, 6))
        self.minutes_var = tk.StringVar(value=str(DEFAULT_MINUTES))
        self.minutes_entry = tk.Spinbox(set_row, from_=1, to=300, textvariable=self.minutes_var,
                                         width=5, font=(theme.FONT_FAMILY, 10), justify="center")
        self.minutes_entry.pack(side="left")

        self.time_label = tk.Label(body, text=f"{DEFAULT_MINUTES:02d}:00", bg=theme.CARD, fg=theme.NAVY_DARK,
                                    font=(theme.FONT_FAMILY, 54, "bold"))
        self.time_label.pack(pady=16)

        btn_row = tk.Frame(body, bg=theme.CARD)
        btn_row.pack(pady=10)
        self.start_btn = tk.Button(btn_row, text="Start", command=self.toggle, width=11,
                                    bg=theme.ORANGE, fg="white", bd=0, font=(theme.FONT_FAMILY, 11, "bold"),
                                    activebackground=theme.ORANGE_DARK, activeforeground="white",
                                    cursor="hand2", pady=8)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = tk.Button(btn_row, text="Stop & Save", command=self.stop_and_save, width=11,
                                   bg=theme.BG, fg=theme.TEXT_DARK, bd=0, font=(theme.FONT_FAMILY, 11, "bold"),
                                   activebackground=theme.BORDER, cursor="hand2", pady=8, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        self.reset_btn = tk.Button(btn_row, text="Reset", command=self.reset, width=11,
                                    bg=theme.BG, fg=theme.TEXT_DARK, bd=0, font=(theme.FONT_FAMILY, 11, "bold"),
                                    activebackground=theme.BORDER, cursor="hand2", pady=8)
        self.reset_btn.pack(side="left", padx=5)

    def toggle(self):
        if not self.running:
            if self.remaining <= 0:
                try:
                    minutes = max(1, int(self.minutes_var.get()))
                except ValueError:
                    minutes = DEFAULT_MINUTES
                self.total_seconds = minutes * 60
                self.remaining = self.total_seconds
                self.start_time = datetime.now()
            self.running = True
            self._tick_mark = datetime.now()
            self.start_btn.config(text="Pause", bg=theme.NAVY)
            self.stop_btn.config(state="normal")
            self.minutes_entry.config(state="disabled")
            self.subject_picker.lock()
            self._tick()
        else:
            self._sync_remaining()
            self.running = False
            self.start_btn.config(text="Resume", bg=theme.ORANGE)
            self._cancel_tick()

    def _sync_remaining(self):
        now = datetime.now()
        passed = (now - self._tick_mark).total_seconds()
        self.remaining = max(0.0, self.remaining - passed)
        self._tick_mark = now

    def _tick(self):
        if not self.running:
            return
        self._sync_remaining()
        self.time_label.config(text=self._fmt(self.remaining))
        if self.remaining <= 0:
            self._finish()
            return
        self._after_id = self.after(TICK_MS, self._tick)

    def _finish(self):
        self.running = False
        self._cancel_tick()
        studied = self.total_seconds
        self._save_if_worth_it(studied)
        self._beep()
        self.reset()

    def stop_and_save(self):
        if self.running:
            self._sync_remaining()
            self.running = False
            self._cancel_tick()
        studied = self.total_seconds - self.remaining
        self._save_if_worth_it(studied)
        self.reset()

    def _save_if_worth_it(self, studied_seconds):
        if studied_seconds >= MIN_SECONDS_TO_SAVE and self.start_time:
            subject, color = self.subject_picker.get_selection()
            storage.save_session(subject, color, studied_seconds, self.start_time, datetime.now(), "timer")
            if self.on_session_saved:
                self.on_session_saved()

    @staticmethod
    def _beep():
        try:
            import winsound
            winsound.MessageBeep()
        except ImportError:
            pass

    def _cancel_tick(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def reset(self):
        self._cancel_tick()
        self.running = False
        self.total_seconds = 0
        self.remaining = 0
        self.start_time = None
        try:
            minutes = max(1, int(self.minutes_var.get()))
        except ValueError:
            minutes = DEFAULT_MINUTES
        self.time_label.config(text=f"{minutes:02d}:00")
        self.start_btn.config(text="Start", bg=theme.ORANGE)
        self.stop_btn.config(state="disabled")
        self.minutes_entry.config(state="normal")
        self.subject_picker.unlock()

    @staticmethod
    def _fmt(seconds):
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
