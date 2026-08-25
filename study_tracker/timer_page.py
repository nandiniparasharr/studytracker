"""'Timer' section: a countdown timer for focused study blocks."""

import tkinter as tk
from datetime import datetime

import storage
import theme
from widgets import (MinutesDialog, PillButton, RoundedCard, SubjectPicker,
                     ToggleSwitch, round_rect)

MIN_SECONDS_TO_SAVE = 5
TICK_MS = 250
DEFAULT_MINUTES = 25
PRESETS = [15, 25, 45, 60]


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
        self.minutes = DEFAULT_MINUTES
        self._preset_chips = {}
        self._build()

    def _build(self):
        pad = 26
        head = tk.Frame(self, bg=theme.BG)
        head.pack(fill="x", padx=pad, pady=(24, 18))
        tk.Label(head, text="Timer", bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT_FAMILY, 25, "bold")).pack(anchor="w")
        tk.Label(head, text="Set a block and focus until it ends", bg=theme.BG,
                 fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 11)).pack(anchor="w", pady=(4, 0))

        card = RoundedCard(self)
        card.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body = tk.Frame(card.body, bg=theme.CARD)
        body.place(relx=0.5, rely=0.5, anchor="center")

        self.subject_picker = SubjectPicker(body)
        self.subject_picker.pack(pady=(0, 20))

        chips = tk.Frame(body, bg=theme.CARD)
        chips.pack(pady=(0, 14))
        for m in PRESETS:
            chip = tk.Canvas(chips, width=62, height=34, bg=theme.CARD,
                             highlightthickness=0, cursor="hand2")
            chip.pack(side="left", padx=4)
            chip.bind("<Button-1>", lambda _e, mm=m: self.set_minutes(mm))
            self._preset_chips[m] = chip

        self.custom_chip = tk.Canvas(chips, width=84, height=34, bg=theme.CARD,
                                      highlightthickness=0, cursor="hand2")
        self.custom_chip.pack(side="left", padx=4)
        self.custom_chip.bind("<Button-1>", lambda _e: self._pick_custom())

        self.counts_toggle = ToggleSwitch(body, "Count as study time", value=True, width=210)
        self.counts_toggle.pack(pady=(0, 16))

        self.time_label = tk.Label(body, text=f"{DEFAULT_MINUTES:02d}:00", bg=theme.CARD,
                                    fg=theme.TEXT, font=(theme.FONT_FAMILY, 58, "bold"))
        self.time_label.pack()

        self.status_label = tk.Label(body, text="Ready when you are.", bg=theme.CARD,
                                      fg=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 10))
        self.status_label.pack(pady=(6, 22))

        btns = tk.Frame(body, bg=theme.CARD)
        btns.pack()
        self.start_btn = PillButton(btns, "Start", self.toggle, kind="primary", width=140)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = PillButton(btns, "Stop & Save", self.stop_and_save, kind="ghost", width=140)
        self.stop_btn.pack(side="left", padx=5)
        self.stop_btn.set_enabled(False)
        self.reset_btn = PillButton(btns, "Reset", self.reset, kind="ghost", width=110)
        self.reset_btn.pack(side="left", padx=5)

        self._render_chips()

    def on_show(self):
        self.subject_picker.refresh_subjects()

    def _render_chips(self):
        idle = not self.running and self.remaining <= 0
        for m, chip in self._preset_chips.items():
            chip.delete("all")
            active = (m == self.minutes) and idle
            self._draw_chip(chip, 62, f"{m}m", active, idle)

        # The custom chip shows the chosen length once it isn't a preset.
        self.custom_chip.delete("all")
        is_custom = self.minutes not in PRESETS
        label = self._chip_label(self.minutes) if is_custom else "Custom"
        self._draw_chip(self.custom_chip, 84, label, is_custom and idle, idle)

    @staticmethod
    def _chip_label(minutes):
        if minutes >= 60:
            h, m = divmod(minutes, 60)
            return f"{h}h {m}m" if m else f"{h}h"
        return f"{minutes}m"

    @staticmethod
    def _draw_chip(chip, width, label, active, idle):
        fill = theme.ACCENT if active else theme.CARD
        outline = "" if active else theme.BORDER
        if active:
            fg = "white"
        elif idle:
            fg = theme.TEXT_MUTED
        else:
            fg = theme.TEXT_FAINT
        round_rect(chip, 1, 1, width - 1, 33, 11, fill=fill, outline=outline,
                   width=1 if outline else 0)
        chip.create_text(width / 2, 17, text=label, fill=fg,
                         font=(theme.FONT_FAMILY, 10, "bold"))

    def _pick_custom(self):
        if self.running or self.remaining > 0:
            return
        result = MinutesDialog(self, minutes=self.minutes).show()
        if result:
            self.set_minutes(result["minutes"])

    def set_minutes(self, minutes):
        if self.running or self.remaining > 0:
            return
        self.minutes = minutes
        self.time_label.config(text=self._fmt(minutes * 60))
        self._render_chips()

    def toggle(self):
        if not self.running:
            if self.remaining <= 0:
                self.total_seconds = self.minutes * 60
                self.remaining = self.total_seconds
                self.start_time = datetime.now()
            self.running = True
            self._tick_mark = datetime.now()
            self.start_btn.set_text("Pause")
            self.stop_btn.set_enabled(True)
            self.status_label.config(
                text="Focus mode - timer running." if self.counts_toggle.get()
                else "Timer running - this block will not count as study time.")
            self.subject_picker.lock()
            self.counts_toggle.set_enabled(False)
            self._render_chips()
            self._tick()
        else:
            self._sync_remaining()
            self.running = False
            self.start_btn.set_text("Resume")
            self.status_label.config(text="Paused.")
            self._cancel_tick()

    def _sync_remaining(self):
        now = datetime.now()
        self.remaining = max(0.0, self.remaining - (now - self._tick_mark).total_seconds())
        self._tick_mark = now

    def _tick(self):
        if not self.running:
            return
        self._sync_remaining()
        text = self._fmt(self.remaining)
        if text != self.time_label.cget("text"):
            self.time_label.config(text=text)
        if self.remaining <= 0:
            self._finish()
            return
        self._after_id = self.after(TICK_MS, self._tick)

    def _finish(self):
        self.running = False
        self._cancel_tick()
        counted = self.counts_toggle.get()
        self._save_if_worth_it(self.total_seconds)
        self._beep()
        self.reset()
        self.status_label.config(
            text="Block complete - saved to your log." if counted
            else "Block complete - logged, but not counted as study time.")

    def stop_and_save(self):
        if self.running:
            self._sync_remaining()
            self.running = False
            self._cancel_tick()
        studied = self.total_seconds - self.remaining
        counted = self.counts_toggle.get()
        saved = self._save_if_worth_it(studied)
        self.reset()
        if not saved:
            self.status_label.config(text="Too short to save.")
        else:
            self.status_label.config(
                text="Saved to your log." if counted
                else "Logged, but not counted as study time.")

    def _save_if_worth_it(self, studied_seconds):
        if studied_seconds >= MIN_SECONDS_TO_SAVE and self.start_time:
            subject, color = self.subject_picker.get_selection()
            storage.save_session(subject, color, studied_seconds, self.start_time,
                                 datetime.now(), "timer", counts=self.counts_toggle.get())
            if self.on_session_saved:
                self.on_session_saved()
            return True
        return False

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
        self.time_label.config(text=self._fmt(self.minutes * 60))
        self.start_btn.set_text("Start")
        self.stop_btn.set_enabled(False)
        self.status_label.config(text="Ready when you are.")
        self.subject_picker.unlock()
        self.counts_toggle.set_enabled(True)
        self._render_chips()

    @staticmethod
    def _fmt(seconds):
        seconds = int(round(seconds))
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
