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

## Using the app

The sidebar has three sections:

- **Dashboard** - today's and this week's study hours, a breakdown of time
  per subject (color-coded), a calendar highlighting which days you
  studied (click a day to see that day's sessions), and your most recent
  sessions.
- **Start** - a stopwatch. Press Start when you begin studying, Pause if
  you take a break, and **Stop & Save** to log the session.
- **Timer** - a countdown timer for focused study blocks (e.g. Pomodoro
  sessions). Set the minutes, press Start, and it logs the session
  automatically when it finishes (or press **Stop & Save** to log a
  partial block early).

**Subjects are optional.** On the Start and Timer screens you can pick a
subject (or add a new one with `+ New`) purely to color-code the session
on the dashboard - you are never required to set one to start tracking
time.

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
  widgets.py                rounded cards, sidebar nav, calendar, subject picker
  storage.py                JSON persistence
  theme.py                  shared colors/fonts
  data/                      created at runtime (git-ignored)
```
