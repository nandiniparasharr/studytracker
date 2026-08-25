"""Study Tracker - a lightweight local desktop app for logging study time.

Run directly with:  pythonw app.py   (or  python app.py)
See ../setup.bat to install a Desktop shortcut instead.
"""

import sys
import tkinter as tk

import icons
import storage
import theme
from dashboard import DashboardPage
from pages import GoalsPage, ReportsPage, SessionsPage, SettingsPage, SubjectsPage
from start_page import StartPage
from timer_page import TimerPage
from widgets import NavButton, round_rect

APP_TITLE = "Study Tracker"
SIDEBAR_W = 236

NAV_ITEMS = [
    ("dashboard", "Dashboard", "dashboard"),
    ("start", "Start", "play"),
    ("timer", "Timer", "clock"),
    ("sessions", "Sessions", "sessions"),
    ("subjects", "Subjects", "tag"),
    ("reports", "Reports", "reports"),
]
NAV_FOOTER = [
    ("goals", "Goals", "goals"),
    ("settings", "Settings", "settings"),
]


def _enable_windows_dpi_awareness():
    """Without this, Windows treats the app as DPI-unaware and bitmap-stretches
    the whole window to match display scaling - which is what makes text and
    edges look blurry (and costs redraw performance) on any scaled display,
    i.e. almost every modern laptop.
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
        self.geometry("1360x900")
        self.minsize(1060, 680)
        self.configure(bg=theme.BG)
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

        self.nav_buttons = {}
        self.pages = {}
        self._active_key = None
        self._dashboard_dirty = True

        self._build_sidebar()
        self._build_content()
        self.show_page("dashboard")

    # ------------------------------------------------------------ sidebar
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=theme.SIDEBAR, width=SIDEBAR_W)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=theme.SIDEBAR)
        brand.pack(fill="x", padx=18, pady=(24, 22))
        logo_row = tk.Frame(brand, bg=theme.SIDEBAR)
        logo_row.pack(anchor="w")
        icons.icon_canvas(logo_row, "book", 24, theme.SIDEBAR_TEXT_ACTIVE,
                          theme.SIDEBAR).pack(side="left", padx=(0, 9))
        tk.Label(logo_row, text="Study Tracker", bg=theme.SIDEBAR, fg=theme.SIDEBAR_TEXT_ACTIVE,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(side="left")
        tk.Label(brand, text="Focus. Track. Grow.", bg=theme.SIDEBAR, fg=theme.SIDEBAR_MUTED,
                 font=(theme.FONT_FAMILY, 9)).pack(anchor="w", pady=(4, 0))

        nav = tk.Frame(sidebar, bg=theme.SIDEBAR)
        nav.pack(fill="x", padx=18)
        for key, label, icon_name in NAV_ITEMS:
            btn = NavButton(nav, label, icon_name, command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=1)
            self.nav_buttons[key] = btn

        tk.Frame(sidebar, bg=theme.SIDEBAR_DIVIDER, height=1).pack(fill="x", padx=26, pady=14)

        footer_nav = tk.Frame(sidebar, bg=theme.SIDEBAR)
        footer_nav.pack(fill="x", padx=18)
        for key, label, icon_name in NAV_FOOTER:
            btn = NavButton(footer_nav, label, icon_name, command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=1)
            self.nav_buttons[key] = btn

        self.streak_holder = tk.Frame(sidebar, bg=theme.SIDEBAR)
        self.streak_holder.pack(side="bottom", fill="x", padx=18, pady=20)
        self.streak_canvas = tk.Canvas(self.streak_holder, height=112, bg=theme.SIDEBAR,
                                        highlightthickness=0, bd=0, width=1)
        self.streak_canvas.pack(fill="x")
        self.streak_canvas.bind("<Configure>", lambda _e: self._render_streak())

    def _render_streak(self):
        c = self.streak_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 40:
            return
        h = 112
        round_rect(c, 0, 0, w, h, 14, fill=theme.SIDEBAR_ACTIVE, outline="")

        days = storage.current_streak(storage.load_sessions())
        icons.draw(c, "flame", 16, 16, 16, "#E8A85C")
        c.create_text(40, 24, text="Current Streak", anchor="w", fill=theme.SIDEBAR_TEXT,
                      font=(theme.FONT_FAMILY, 9))
        num = c.create_text(16, 58, text=str(days), anchor="w", fill="white",
                            font=(theme.FONT_FAMILY, 22, "bold"))
        num_right = c.bbox(num)[2]
        c.create_text(num_right + 7, 63, text="day" if days == 1 else "days", anchor="w",
                      fill=theme.SIDEBAR_TEXT, font=(theme.FONT_FAMILY, 10))
        c.create_text(16, 90, text="Keep it going!", anchor="w", fill=theme.SIDEBAR_MUTED,
                      font=(theme.FONT_FAMILY, 9))

    # ------------------------------------------------------------ content
    def _build_content(self):
        content = tk.Frame(self, bg=theme.BG)
        content.pack(side="left", fill="both", expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        changed = self._on_data_changed
        self.pages = {
            "dashboard": DashboardPage(content, on_goto=self.show_page),
            "start": StartPage(content, on_session_saved=changed),
            "timer": TimerPage(content, on_session_saved=changed),
            "sessions": SessionsPage(content, on_changed=changed),
            "subjects": SubjectsPage(content, on_changed=changed),
            "reports": ReportsPage(content, on_changed=changed),
            "goals": GoalsPage(content, on_changed=changed),
            "settings": SettingsPage(content, on_changed=changed),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, key):
        if key == self._active_key or key not in self.pages:
            return
        self._active_key = key
        for nav_key, btn in self.nav_buttons.items():
            btn.set_active(nav_key == key)

        page = self.pages[key]
        # Every page is built once up front and simply raised, so switching
        # is a single stacking-order change - no rebuild, no window-level
        # transparency, and therefore nothing showing through from behind.
        if key == "dashboard":
            if self._dashboard_dirty:
                page.refresh()
                self._dashboard_dirty = False
        elif hasattr(page, "on_show"):
            page.on_show()
        page.tkraise()

    def _on_data_changed(self):
        self._dashboard_dirty = True
        self._render_streak()
        if self._active_key == "dashboard":
            self.pages["dashboard"].refresh()
            self._dashboard_dirty = False


if __name__ == "__main__":
    app = StudyTrackerApp()
    app.mainloop()
