"""'Start' section: a stopwatch that counts up while you study."""

import tkinter as tk
from datetime import datetime

import storage
import theme
from widgets import RoundedCard, SubjectPicker

MIN_SECONDS_TO_SAVE = 5
TICK_MS = 500


class StartPage(tk.Frame):
    def __init__(self, parent, on_session_saved=None):
        super().__init__(parent, bg=theme.BG)
        self.on_session_saved = on_session_saved
        self.running = False
        self.elapsed = 0.0
        self.start_time = None
        self._tick_mark = None
        self._after_id = None
        self._build()

    def _build(self):
        pad = 20
        tk.Label(self, text="Start Studying", bg=theme.BG, fg=theme.TEXT_DARK,
                 font=(theme.FONT_FAMILY, 18, "bold")).pack(anchor="w", padx=pad, pady=(pad, 12))

        card = RoundedCard(self, bg=theme.CARD, radius=18)
        card.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body = tk.Frame(card.body, bg=theme.CARD)
        body.place(relx=0.5, rely=0.5, anchor="center")

        self.subject_picker = SubjectPicker(body)
        self.subject_picker.pack(pady=(0, 20))

        self.time_label = tk.Label(body, text="00:00:00", bg=theme.CARD, fg=theme.NAVY_DARK,
                                    font=(theme.FONT_FAMILY, 54, "bold"))
        self.time_label.pack(pady=10)

        self.hint_label = tk.Label(body, text="Pick a subject to color-code it, or just hit Start.",
                                    bg=theme.CARD, fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 9))
        self.hint_label.pack(pady=(0, 10))

        btn_row = tk.Frame(body, bg=theme.CARD)
        btn_row.pack(pady=10)
        self.start_btn = tk.Button(btn_row, text="Start", command=self.toggle, width=12,
                                    bg=theme.ORANGE, fg="white", bd=0, font=(theme.FONT_FAMILY, 11, "bold"),
                                    activebackground=theme.ORANGE_DARK, activeforeground="white",
                                    cursor="hand2", pady=8)
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = tk.Button(btn_row, text="Stop & Save", command=self.stop, width=12,
                                   bg=theme.BG, fg=theme.TEXT_DARK, bd=0, font=(theme.FONT_FAMILY, 11, "bold"),
                                   activebackground=theme.BORDER, cursor="hand2", pady=8, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

    def toggle(self):
        if not self.running:
            self.running = True
            if self.start_time is None:
                self.start_time = datetime.now()
            self._tick_mark = datetime.now()
            self.start_btn.config(text="Pause", bg=theme.NAVY)
            self.stop_btn.config(state="normal")
            self.subject_picker.lock()
            self._tick()
        else:
            self._sync_elapsed()
            self.running = False
            self.start_btn.config(text="Resume", bg=theme.ORANGE)
            self._cancel_tick()

    def _sync_elapsed(self):
        now = datetime.now()
        self.elapsed += (now - self._tick_mark).total_seconds()
        self._tick_mark = now

    def _tick(self):
        if not self.running:
            return
        self._sync_elapsed()
        self.time_label.config(text=self._fmt(self.elapsed))
        self._after_id = self.after(TICK_MS, self._tick)

    def stop(self):
        if self.running:
            self._sync_elapsed()
            self.running = False
            self._cancel_tick()

        if self.elapsed >= MIN_SECONDS_TO_SAVE:
            subject, color = self.subject_picker.get_selection()
            storage.save_session(subject, color, self.elapsed, self.start_time, datetime.now(), "stopwatch")
            if self.on_session_saved:
                self.on_session_saved()

        self._reset()

    def _cancel_tick(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _reset(self):
        self.elapsed = 0.0
        self.start_time = None
        self.time_label.config(text="00:00:00")
        self.start_btn.config(text="Start", bg=theme.ORANGE)
        self.stop_btn.config(state="disabled")
        self.subject_picker.unlock()

    @staticmethod
    def _fmt(seconds):
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
