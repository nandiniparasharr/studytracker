# Study Tracker

A small local desktop app for tracking how many hours you study during the
week. No install, no account, no internet connection - everything is a
plain Python script and a JSON file on your own computer.

## Setup (Windows)

1. Make sure [Python](https://www.python.org/downloads/) is installed
   (check "Add Python to PATH" during install). Tkinter ships with Python
   by default, so nothing else needs to be installed.
2. Double-click **`setup.bat`**.
   - It finds your Python install, creates a **"Study Tracker"** shortcut
     on your Desktop, and launches the app.
3. From then on, just use the **Study Tracker** icon on your Desktop.

You can also run it directly at any time with:

```
python study_tracker\app.py
```

## Sections

- **Dashboard** - greeting, this week's totals (today, week, session count,
  average session) with week-on-week deltas, a bar chart of daily hours, a
  study calendar (a ring on today, a colored dot on any day you studied -
  darker means more hours), your subject split as a donut, recent sessions,
  and weekly-goal progress. Use the date range control in the top right to
  look back at earlier weeks, or click a calendar day to see just that day.
- **Start** - a stopwatch. Press Start when you begin studying, Pause for a
  break, and **Stop & Save** to log the session.
- **Timer** - a countdown for focused blocks (15/25/45/60m presets). Logs
  automatically when it finishes, or **Stop & Save** to log a partial block.
- **Sessions** - the full log, with the option to delete any entry.
- **Subjects** - add or remove subjects and click a swatch to change its
  color.
- **Reports** - this week vs. last week vs. this month, an eight-week trend,
  and all-time totals per subject.
- **Goals** - set your weekly target and see your current streak.
- **Settings** - display name for the greeting, where your data is stored,
  and a way to clear the log.

**Subjects are optional.** On the Start and Timer screens you can pick a
subject (or add one with `+`) purely to color-code the session on the
dashboard - you are never required to set one to start tracking time.

## Data

Sessions, subjects, and settings are stored as plain JSON files in
`study_tracker/data/`, created automatically the first time you save a
session. Nothing leaves your computer.

## Project layout

```
setup.bat                  installs the Desktop shortcut and launches the app
study_tracker/
  app.py                   entry point - window, sidebar, page switching
  dashboard.py             Dashboard page
  start_page.py            Start page (stopwatch)
  timer_page.py            Timer page (countdown)
  pages.py                 Sessions, Subjects, Reports, Goals, Settings
  widgets.py               cards, nav, charts, calendar, buttons, scrolling
  icons.py                 vector line icons drawn on canvas
  storage.py               JSON persistence and analytics helpers
  theme.py                 shared colors/fonts
  data/                    created at runtime (git-ignored)
```
