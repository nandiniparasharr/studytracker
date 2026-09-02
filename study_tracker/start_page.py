"""'Start' section: a stopwatch that counts up while you study."""

import tkinter as tk
from datetime import datetime

import storage
import theme
from widgets import PillButton, RoundedCard, SubjectPicker

MIN_SECONDS_TO_SAVE = 5
TICK_MS = 250


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
        pad = 26
        head = tk.Frame(self, bg=theme.BG)
        head.pack(fill="x", padx=pad, pady=(24, 18))
        tk.Label(head, text="Start Studying", bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 25, "bold")).pack(anchor="w")
        tk.Label(head, text="The stopwatch runs until you stop it", bg=theme.BG,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 11)).pack(anchor="w", pady=(4, 0))

        card = RoundedCard(self)
        card.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body = tk.Frame(card.body, bg=theme.CARD)
        body.place(relx=0.5, rely=0.5, anchor="center")

        self.subject_picker = SubjectPicker(body)
        self.subject_picker.pack(pady=(0, 26))

        self.time_label = tk.Label(body, text="00:00:00", bg=theme.CARD, fg=theme.TEXT,
                                    font=(theme.FONT_FAMILY, 58, "bold"))
        self.time_label.pack()

        self.status_label = tk.Label(body, text="Ready when you are.", bg=theme.CARD,
                                      fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10))
        self.status_label.pack(pady=(6, 22))

        btns = tk.Frame(body, bg=theme.CARD)
        btns.pack()
        self.start_btn = PillButton(btns, "Start", self.toggle, kind="primary", width=150)
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = PillButton(btns, "Stop & Save", self.stop, kind="ghost", width=150)
        self.stop_btn.pack(side="left", padx=6)
        self.stop_btn.set_enabled(False)

    def on_show(self):
        self.subject_picker.refresh_subjects()

    def toggle(self):
        if not self.running:
            self.running = True
            if self.start_time is None:
                self.start_time = datetime.now()
            self._tick_mark = datetime.now()
            self.start_btn.set_text("Pause")
            self.stop_btn.set_enabled(True)
            self.status_label.config(text="Studying - stay with it.")
            self.subject_picker.lock()
            self._tick()
        else:
            self._sync_elapsed()
            self.running = False
            self.start_btn.set_text("Resume")
            self.status_label.config(text="Paused.")
            self._cancel_tick()

    def _sync_elapsed(self):
        now = datetime.now()
        self.elapsed += (now - self._tick_mark).total_seconds()
        self._tick_mark = now

    def _tick(self):
        if not self.running:
            return
        self._sync_elapsed()
        text = self._fmt(self.elapsed)
        if text != self.time_label.cget("text"):
            self.time_label.config(text=text)
        self._after_id = self.after(TICK_MS, self._tick)

    def stop(self):
        if self.running:
            self._sync_elapsed()
            self.running = False
            self._cancel_tick()

        if self.elapsed >= MIN_SECONDS_TO_SAVE:
            subject, color = self.subject_picker.get_selection()
            storage.save_session(subject, color, self.elapsed, self.start_time,
                                 datetime.now(), "stopwatch")
            if self.on_session_saved:
                self.on_session_saved()
            self.status_label.config(text="Saved to your log.")
        else:
            self.status_label.config(text="Too short to save.")

        self._reset()

    def _cancel_tick(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _reset(self):
        self.elapsed = 0.0
        self.start_time = None
        self.time_label.config(text="00:00:00")
        self.start_btn.set_text("Start")
        self.stop_btn.set_enabled(False)
        self.subject_picker.unlock()

    @staticmethod
    def _fmt(seconds):
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
