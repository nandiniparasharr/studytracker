"""Study Tracker - a lightweight local desktop app for logging study time.

Run directly with:  pythonw app.py   (or  python app.py)
See ../setup.bat to install a Desktop shortcut instead.
"""

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


class StudyTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=theme.BG)
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

        self.nav_buttons = {}
        self.pages = {}

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
        for nav_key, btn in self.nav_buttons.items():
            btn.set_active(nav_key == key)
        self.pages[key].tkraise()
        if key == "dashboard":
            self.pages["dashboard"].refresh()

    def _on_session_saved(self):
        self.pages["dashboard"].refresh()


if __name__ == "__main__":
    app = StudyTrackerApp()
    app.mainloop()
