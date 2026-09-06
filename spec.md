# Study Tracker - Specification

A local desktop application for logging and reviewing study time. It runs
entirely on one Windows machine: no account, no server, no network calls.
Sessions are stored as plain JSON files inside the project folder.

This document describes what the tool does, how it is built, and the
decisions behind it. For install steps, see [README.md](README.md).

---

## 1. Purpose and scope

**The problem.** Knowing roughly how much you studied this week is not the
same as knowing it. The tool records study time as it happens and shows the
result as a weekly picture rather than a list of numbers.

**In scope**

- Recording study time two ways: an open-ended stopwatch, and a countdown
  timer for fixed blocks.
- Optional per-subject colour coding.
- A dashboard covering the current week, with history navigable by week.
- Editing and deleting anything already logged.
- A weekly hour target and a day streak.

**Out of scope, deliberately**

- Accounts, sync, sharing, or any network access.
- Task or todo management - this measures time, it does not plan it.
- Reminders and notifications.
- Mobile or web access (see [§10](#10-known-limits)).

**Design principles**

1. *Subjects are never required.* Every screen works with no subject set.
   They exist purely to colour-code, and a session without one is logged as
   "Unspecified" in neutral grey.
2. *The dashboard fits on one screen.* No scrolling to see the week.
3. *Nothing leaves the computer.* No telemetry, no cloud, no update check.
4. *One optional dependency.* The app must run on a stock Python install.

---

## 2. Sections

The app is a fixed left sidebar plus one content page at a time. Eight
sections: Dashboard, Start, Timer, Sessions, Subjects, Reports, then Goals
and Settings below a divider.

### Dashboard

The default view, and the only page built to fit without scrolling.

| Region | Contents |
|---|---|
| Header | Time-of-day greeting with your display name; week range control with back/forward arrows |
| Stat row | Today, This Week, Sessions, Avg. Session - each with a week-on-week or day-on-day delta |
| Bar chart | Daily totals Monday-Sunday for the selected week |
| Calendar | Month grid; today is filled, studied days carry a coloured dot |
| Donut | Share of time per subject, with a legend and percentages |
| Recent Sessions | Last five, newest first; long names ellipsise |
| Weekly Goal | Hours done against target, progress bar, hours remaining |
| Footer | "Dreams don't work unless you do." |

Clicking a calendar day filters the Recent Sessions panel to that day;
clicking it again clears the filter. The week control moves the whole
dashboard - stats, chart and goal - back through history.

**Calendar intensity.** A studied day's dot darkens in two-hour bands, and
one table drives both the dot colour and the legend so the two cannot
drift apart:

| Band | Colour |
|---|---|
| No study | no dot |
| Under 2h | `#F0CDD8` |
| 2 - 4h | `#DB90A6` |
| 4 - 6h | `#C4627F` |
| Over 6h | `#A03D5B` |

### Start - stopwatch

Counts up from zero with no upper bound. **Start** begins, the same button
becomes **Pause** then **Resume**, and **Stop & Save** writes the session
and resets. Anything under 5 seconds is discarded as a misclick. The
subject picker locks while the clock is running so a session cannot change
subject halfway through.

Elapsed time is computed from wall-clock timestamps, not by counting
ticks, so it stays accurate if the UI thread stalls. The display refreshes
every 250 ms and only redraws when the visible text actually changes.

### Timer - countdown

Presets of 15, 25, 45 and 60 minutes, plus **Custom** for any length
entered as hours (0-12) and minutes (0-59), which must come to more than
zero. Logs automatically
when it reaches zero; **Stop & Save** logs a partial block.

A **Count as study time** switch decides whether the block counts. Turned
off, the session still appears in your log but is excluded from every
total, chart, streak and goal - for breaks, admin, or anything you want on
the record but not in the hours. The switch locks while the timer runs, and
the flag can be changed later by editing the session.

### Sessions

The full log, newest first: subject dot, name, date, duration, and a
three-dot menu per row offering **Edit** and **Delete**. Editing changes
the subject, the length (which recomputes the end time), and the
count-as-study-time flag. A zero length is rejected.

### Subjects

Add, edit, recolour or delete subjects. Each row shows its colour and total
hours logged. Editing a subject renames and recolours its past sessions
too, since sessions store their own copy of both. Duplicate names are
refused, case-insensitively.

**Recolor all** reassigns every subject a different palette colour in list
order and pushes the change onto already-logged sessions. It exists for
subjects created before the palette changed; new subjects pick the next
unused colour automatically and never need it.

### Reports

This week, last week and this month as totals; an eight-week trend chart;
and all-time hours per subject.

### Goals

Weekly target picked from 5, 10, 15, 20, 25, 30 or 40 hours, with progress
against it and your current streak - consecutive days with at least one
counted session, ending today or yesterday.

### Settings

Display name for the greeting, the exact folder your data lives in, session
and total counts, and **Clear all sessions** (confirmed, and permanent).

---

## 3. Data model

Three JSON files in `study_tracker/data/`, created on first save. Writes go
to a `.tmp` file and are then atomically renamed, so an interrupted write
cannot corrupt an existing file. Unreadable or missing files fall back to
empty rather than raising.

### `sessions.json`

```json
{
  "id": "3f2a9c...",              // uuid4 hex
  "subject": "Ethics",            // or "Unspecified"
  "color": "#EC8C7A",             // copied, not referenced
  "seconds": 5400,
  "started_at": "2026-09-02T18:30:00",
  "ended_at": "2026-09-02T20:00:00",
  "date": "2026-09-02",           // local date of the start, for grouping
  "kind": "stopwatch",            // or "timer"
  "counts": true                  // false = logged but excluded from totals
}
```

Two decisions worth stating:

- **Sessions copy the subject name and colour** rather than referencing a
  subject record. A deleted subject leaves its history readable and
  correctly coloured. The cost is that renaming or recolouring has to be
  applied to past sessions explicitly, which `edit_subject()` and
  `reassign_palette()` both do.
- **`counts` is absent on sessions saved before the flag existed.** Every
  reader treats a missing value as `true`, so old logs keep working.

### `subjects.json`

```json
{ "name": "Ethics", "color": "#EC8C7A" }
```

### `settings.json`

```json
{ "weekly_goal_hours": 20, "display_name": "" }
```

Defaults are merged over whatever the file contains, so a setting added in
a later version appears without migration.

### Analytics helpers

All live in `storage.py` and all filter through `counted()` first:
`week_bounds`, `sessions_between`, `total_seconds`, `day_totals`,
`subject_totals`, `current_streak`.

---

## 4. Subject palette

Ten colours. They were not picked by eye - they are the result of
maximising the smallest pairwise [CIEDE2000](https://en.wikipedia.org/wiki/Color_difference#CIEDE2000)
distance under three constraints:

1. One hue family each, no two within 24 degrees.
2. Chroma held to C\* 28-43, so none reads as a primary (primaries sit at
   C\* 60-105).
3. At least dE 20 from the UI accent, so a subject dot never looks like
   accent chrome.

The closest pair is **dE 22.3**; above 10 is clearly different at a glance,
above 20 is unmistakable.

| | Hex | Name | | Hex | Name |
|---|---|---|---|---|---|
| 1 | `#EC8C7A` | coral | 6 | `#1F7F7B` | teal |
| 2 | `#A06431` | tobacco | 7 | `#29B3DE` | cerulean |
| 3 | `#C1A257` | wheat | 8 | `#2E75BA` | denim |
| 4 | `#6E7646` | olive | 9 | `#7E6997` | amethyst |
| 5 | `#6CB67A` | sage | 10 | `#E28ABF` | orchid |

Sessions with no subject use `#A9AAAE`, a neutral grey chosen so it does
not read as an eleventh colour.

**Known limit.** This optimises for normal colour vision. Under
deuteranopia the nearest pair falls to dE 3.8. Enforcing a colour-vision
floor was tried and rejected: it cut normal-vision separation to dE 12 and
collapsed the set into five near-identical greens, which is worse against
the stated goal. Anyone who needs it should pick their own colours - every
subject's colour is editable.

---

## 5. Theme

Six base tokens in `theme.py`; everything else derives from them, so the
whole app re-skins from that one file.

| Token | Value | Role |
|---|---|---|
| `GROUND` | `#FAFAF8` | the page behind everything |
| `RAISED` | `#FFFFFF` | cards on the ground |
| `DOTS` | `#DEDDD6` | hairlines, borders, dividers |
| `INK` | `#17181B` | primary text, and the sidebar panel |
| `MUTED` | `#6E7076` | secondary text |
| `ACCENT` | `#B8496A` | the single highlight colour |

The sidebar is an INK panel, so its scale runs the other way: idle nav text
`#D5D6DA`, active `#FFFFFF`, secondary `#8C8E95`. `MUTED` is tuned for
light cards and is too dim on the dark panel, which is why the sidebar has
its own value.

Typography is Segoe UI throughout, 8pt (section labels) to 25pt (page
titles).

---

## 6. Architecture

```
setup.bat                  installs the Desktop shortcut, launches the app
create_shortcut.ps1        resolves the real Desktop path, makes the shortcut
create_shortcut.vbs        same, for when PowerShell is unavailable
study_tracker/
  app.py         188 lines  entry point: window, sidebar, page switching
  dashboard.py   402        Dashboard
  start_page.py  129        Start (stopwatch)
  timer_page.py  249        Timer (countdown)
  pages.py       515        Sessions, Subjects, Reports, Goals, Settings
  widgets.py    1395        cards, nav, charts, calendar, dialogs, popups
  icons.py       339        14 vector line icons from one declarative table
  aa.py          278        anti-aliased shape rasteriser (optional Pillow)
  storage.py     273        JSON persistence and analytics
  theme.py        84        colours and fonts
  data/                     created at runtime, git-ignored
```

**Layering.** `storage.py` and `theme.py` import no GUI code at all -
`storage.py` needs only `json`, `os`, `uuid` and `datetime`. Everything
above them is Tkinter. That split is what makes a future web backend
tractable ([§10](#10-known-limits)).

**Pages** are all built once at startup and stacked; switching calls
`tkraise()`. Each exposes `on_show()` to refresh itself when raised, so
data edited on one page appears on the others without a global event bus.

### Why the custom widgets

Tk's native widgets look like Windows 95 and cannot be styled far enough,
so cards, buttons, charts, the calendar, dropdowns and menus are all drawn
on canvases. Two consequences shaped the codebase:

**No anti-aliasing.** Tk's canvas draws ovals, arcs and polygons with hard
binary edges - text is smooth because a font renderer handles it, but a
circle stair-steps. `aa.py` works around this by rasterising shapes with
Pillow at 4x and downsampling with LANCZOS into a `PhotoImage`. Discs,
rings, rounded-rectangle corner tiles, donuts, pills, wedges and icons all
go through it, cached by argument tuple with a 400-entry ceiling.

**Pillow is optional.** Every `aa` helper returns `None` when Pillow is
absent and each caller falls back to the plain canvas primitive. The app is
fully functional either way; the curves are just jagged. Both paths are
tested.

**No native menus.** `tk.Menu` renders with the OS's own look. Dropdowns
and row menus are `StyledPopup`, a borderless toplevel holding one canvas.

### Windows specifics

- **DPI awareness.** `SetProcessDpiAwareness(1)` at startup, falling back
  to `SetProcessDPIAware()`. Without it Windows bitmap-stretches the whole
  window on any scaled display - which is what makes text look blurry on
  essentially every modern laptop.
- **Desktop path.** `%USERPROFILE%\Desktop` frequently does not exist once
  OneDrive backs up your folders. Shortcut creation asks Windows for the
  real path, then falls back through the registry, `%OneDrive%`, and
  finally `%USERPROFILE%`.
- **Dropdowns are not layered windows.** An earlier version keyed a colour
  out to transparent for rounded corners. On Windows that makes a layered
  window, and layered + borderless can come up entirely unpainted - a
  dropdown that opens and shows nothing. Corners now sit on the page
  background, and the panel lifts itself topmost once placed.

---

## 7. Requirements

- **Windows**, with Python 3.8 or newer on PATH. Tkinter ships with the
  standard Windows installer.
- **Pillow**, optional. `setup.bat` installs it; without it the app runs
  with jagged curves.
- No other third-party packages, at all.

The code has no Windows-only imports at module level and runs on Linux and
macOS; only the DPI call and the shortcut scripts are Windows-specific.

---

## 8. Install

Double-click `setup.bat`. It locates Python, installs Pillow if missing,
creates a **Study Tracker** shortcut on the Desktop, and launches the app.
After that, use the Desktop icon.

Direct launch: `python study_tracker\app.py`.

Updating in place with `git pull` preserves your log, because `data/` is
git-ignored and lives inside the project folder. Re-downloading the project
as a ZIP does **not** - copy the old `data/` folder across.

---

## 9. Testing

There is no unit-test suite in the repository. Verification is done by
driving the real application under a virtual display (xvfb) and asserting
against live widget state, plus screenshots, because the failures that
matter here are visual: text clipped by a fixed-width label, a card
collapsed to one pixel, a canvas taking Tk's default size instead of the
one it was measured for.

Eleven scripts cover: every page rendering; the stopwatch and timer
lifecycles; session and subject editing; the count-as-study-time flag and
its effect on every total; palette properties and assignment; the dropdown
opening with real dimensions on an empty subject list; the dashboard
fitting without scrolling at four window sizes; sidebar contrast and the
greeting; and the whole app both with and without Pillow - that last one runs
twice, once down each path.

Each test points `storage` at a throwaway directory, so tests neither
touch a real log nor inherit state from each other.

---

## 10. Known limits

- **One machine, one person.** No sync and no accounts. To use it from more
  than one Windows machine, put the project folder in OneDrive - `data/`
  syncs with it.
- **No web or mobile version.** Tkinter draws through the OS windowing
  system and has no browser equivalent; it does not survive a port to
  Pyodide either. A web version means rewriting the UI. The
  roughly 360 lines of `storage.py` and `theme.py` carry over untouched;
  the roughly 3,500 lines of Tkinter do not, though much of that exists
  only because Tk has no CSS and would collapse to a fraction of the size.
  Three things get genuinely harder: durable storage (JSON files on an
  ephemeral host are lost on redeploy), authentication, and running the
  stopwatch from a stored start timestamp rather than a client-side loop.
- **Deuteranopia**, as described in [§4](#4-subject-palette).
- **No import or export.** The JSON files are readable and portable by
  hand, but there is no CSV export.
- **Time zones and DST.** Sessions record local wall-clock time with no
  offset. A session spanning a DST change records the elapsed seconds
  correctly, since elapsed time is measured by subtraction, but the stored
  timestamps are ambiguous during the repeated hour.
