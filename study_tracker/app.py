"""Study Tracker - a lightweight local desktop app for logging study time.

Run directly with:  pythonw app.py   (or  python app.py)
See ../setup.bat to install a Desktop shortcut instead.
"""

import sys
import tkinter as tk

import theme
from dashboard import DashboardPage
from start_page import StartPage
from timer_page import TimerPage
from widgets import NavButton

APP_TITLE = "Study Tracker"
NAV_ITEMS = [
    ("dashboard", "Dashboard", "▦"),
    ("start", "Start", "▶"),
    ("timer", "Timer", "⏱"),
]

FADE_STEPS = 5
FADE_DELAY_MS = 12
FADE_MIN_ALPHA = 0.6


def _enable_windows_dpi_awareness():
    """Without this, Windows treats the app as DPI-unaware and stretches
    the whole rendered window to match display scaling - which is what
    makes text, colors and edges look blurry (and costs real redraw
    performance) on any scaled display, i.e. almost every modern laptop.
    """
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


class StudyTrackerApp(tk.Tk):
    def __init__(self):
        _enable_windows_dpi_awareness()
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=theme.BG)
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

        self._supports_alpha = True
        try:
            self.attributes("-alpha", 1.0)
        except tk.TclError:
            self._supports_alpha = False

        self.nav_buttons = {}
        self.pages = {}
        self._active_key = None
        self._dashboard_dirty = True
        self._fade_token = 0

        self._build_sidebar()
        self._build_content()
        self.show_page("dashboard")

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=theme.NAVY_DARK, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=theme.NAVY_DARK)
        brand.pack(fill="x", pady=(28, 30), padx=20)
        tk.Label(brand, text="Study", bg=theme.NAVY_DARK, fg="white",
                 font=(theme.FONT_FAMILY, 16, "bold")).pack(anchor="w")
        tk.Label(brand, text="TRACKER", bg=theme.NAVY_DARK, fg=theme.ORANGE,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack(anchor="w")

        for key, label, icon in NAV_ITEMS:
            btn = NavButton(sidebar, label, icon, command=lambda k=key: self.show_page(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

    def _build_content(self):
        content = tk.Frame(self, bg=theme.BG)
        content.pack(side="left", fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.pages = {
            "dashboard": DashboardPage(content),
            "start": StartPage(content, on_session_saved=self._on_session_saved),
            "timer": TimerPage(content, on_session_saved=self._on_session_saved),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, key):
        if key == self._active_key:
            return
        self._active_key = key
        for nav_key, btn in self.nav_buttons.items():
            btn.set_active(nav_key == key)

        self._fade_token += 1
        token = self._fade_token

        if not self._supports_alpha:
            self._raise_page(key)
            return
        self._fade(key, 0, fading_out=True, token=token)

    def _raise_page(self, key):
        self.pages[key].tkraise()
        if key == "dashboard" and self._dashboard_dirty:
            self.pages["dashboard"].refresh()
            self._dashboard_dirty = False

    def _fade(self, key, step, fading_out, token):
        # A newer show_page() call superseded this animation - stop here and
        # let the newer chain own the alpha value (avoids overlapping fades
        # from rapid clicks fighting each other or leaving the window dim).
        if token != self._fade_token:
            return

        frac = step / FADE_STEPS
        alpha = (1.0 - (1 - FADE_MIN_ALPHA) * frac) if fading_out else (FADE_MIN_ALPHA + (1 - FADE_MIN_ALPHA) * frac)
        self._set_alpha(alpha)

        if step >= FADE_STEPS:
            if fading_out:
                self._raise_page(key)
                self.after(FADE_DELAY_MS, lambda: self._fade(key, 0, fading_out=False, token=token))
            else:
                self._set_alpha(1.0)
            return
        self.after(FADE_DELAY_MS, lambda: self._fade(key, step + 1, fading_out, token))

    def _set_alpha(self, value):
        try:
            self.attributes("-alpha", value)
        except tk.TclError:
            pass

    def _on_session_saved(self):
        self._dashboard_dirty = True
        if self._active_key == "dashboard":
            self.pages["dashboard"].refresh()
            self._dashboard_dirty = False


if __name__ == "__main__":
    app = StudyTrackerApp()
    app.mainloop()
