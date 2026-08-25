"""Local JSON persistence for study sessions, subjects and settings.

Everything lives next to this file in a `data/` folder so the app is fully
portable - no database server, no network calls.
"""

import json
import os
import uuid
from datetime import date, datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Subjects are a color-coded extra, never required to start a session.
# Twelve hues, each distinguishable from the others at dot size on a white
# card - so a dozen subjects can all be told apart on the dashboard.
DEFAULT_PALETTE = [
    "#5C2444",  # plum
    "#7D9B7E",  # sage
    "#E8A85C",  # amber
    "#E3A0BC",  # blush
    "#2F8A82",  # teal
    "#6B8CAE",  # steel blue
    "#D4886A",  # terracotta
    "#8E5FA8",  # orchid
    "#7A8C3F",  # olive
    "#8F3A38",  # brick
    "#3F4E8C",  # indigo
    "#8C6A56",  # cocoa
]
# Neutral grey so an unlabelled session reads as "no subject"
# rather than as one more color in the palette.
UNSPECIFIED_COLOR = "#A9AAAE"

DEFAULT_SETTINGS = {"weekly_goal_hours": 20, "display_name": ""}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path, data):
    _ensure_data_dir()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load_sessions():
    return _load_json(SESSIONS_FILE, [])


def save_session(subject, color, seconds, started_at, ended_at, kind, counts=True):
    """`counts=False` logs the block but keeps it out of every study total -
    for breaks, admin, anything you want on the record but not in the hours.
    """
    sessions = load_sessions()
    session = {
        "id": uuid.uuid4().hex,
        "subject": subject or "Unspecified",
        "color": color or UNSPECIFIED_COLOR,
        "seconds": int(seconds),
        "started_at": started_at.isoformat(timespec="seconds"),
        "ended_at": ended_at.isoformat(timespec="seconds"),
        "date": started_at.date().isoformat(),
        "kind": kind,
        "counts": bool(counts),
    }
    sessions.append(session)
    _save_json(SESSIONS_FILE, sessions)
    return session


def delete_session(session_id):
    sessions = [s for s in load_sessions() if s["id"] != session_id]
    _save_json(SESSIONS_FILE, sessions)
    return sessions


def update_session(session_id, subject=None, color=None, seconds=None, counts=None):
    sessions = load_sessions()
    for s in sessions:
        if s["id"] != session_id:
            continue
        if subject is not None:
            s["subject"] = subject
        if counts is not None:
            s["counts"] = bool(counts)
        if color is not None:
            s["color"] = color
        if seconds is not None:
            s["seconds"] = int(seconds)
            # Keep end = start + length so the Sessions list stays consistent.
            started = parse_time(s.get("started_at"))
            if started:
                s["ended_at"] = (started + timedelta(seconds=int(seconds))).isoformat(
                    timespec="seconds")
        break
    _save_json(SESSIONS_FILE, sessions)
    return sessions


def load_subjects():
    return _load_json(SUBJECTS_FILE, [])


def add_subject(name, color):
    subjects = load_subjects()
    if any(s["name"].lower() == name.lower() for s in subjects):
        return subjects
    subjects.append({"name": name, "color": color})
    _save_json(SUBJECTS_FILE, subjects)
    return subjects


def delete_subject(name):
    subjects = [s for s in load_subjects() if s["name"] != name]
    _save_json(SUBJECTS_FILE, subjects)
    return subjects


def set_subject_color(name, color):
    subjects = load_subjects()
    for s in subjects:
        if s["name"] == name:
            s["color"] = color
    _save_json(SUBJECTS_FILE, subjects)
    return subjects


def edit_subject(old_name, new_name, color):
    """Rename/recolor a subject and carry the change onto its past sessions.

    Sessions store their own copy of the label and color (so a deleted
    subject keeps its history readable), which means an edit has to be
    applied to them explicitly.
    """
    subjects = load_subjects()
    if new_name != old_name and any(s["name"].lower() == new_name.lower() for s in subjects):
        return False
    for s in subjects:
        if s["name"] == old_name:
            s["name"] = new_name
            s["color"] = color
    _save_json(SUBJECTS_FILE, subjects)

    sessions = load_sessions()
    for s in sessions:
        if s["subject"] == old_name:
            s["subject"] = new_name
            s["color"] = color
    _save_json(SESSIONS_FILE, sessions)
    return True


def next_color(existing_subjects):
    used = {s["color"] for s in existing_subjects}
    for c in DEFAULT_PALETTE:
        if c not in used:
            return c
    return DEFAULT_PALETTE[len(existing_subjects) % len(DEFAULT_PALETTE)]


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    settings.update(_load_json(SETTINGS_FILE, {}))
    return settings


def save_settings(settings):
    _save_json(SETTINGS_FILE, settings)


# ---------------------------------------------------------------- analytics

def week_bounds(anchor=None):
    """Monday-Sunday range containing `anchor` (defaults to today)."""
    anchor = anchor or date.today()
    start = anchor - timedelta(days=anchor.weekday())
    return start, start + timedelta(days=6)


def counts_toward_study(session):
    """Sessions saved before this flag existed are study time."""
    return session.get("counts", True)


def counted(sessions):
    return [s for s in sessions if counts_toward_study(s)]


def sessions_between(sessions, start, end):
    return [s for s in sessions if start.isoformat() <= s["date"] <= end.isoformat()]


def total_seconds(sessions):
    return sum(s["seconds"] for s in counted(sessions))


def day_totals(sessions):
    totals = {}
    for s in counted(sessions):
        totals[s["date"]] = totals.get(s["date"], 0) + s["seconds"]
    return totals


def subject_totals(sessions):
    totals = {}
    for s in counted(sessions):
        entry = totals.setdefault(s["subject"], {"seconds": 0, "color": s["color"]})
        entry["seconds"] += s["seconds"]
    return totals


def current_streak(sessions):
    """Consecutive days (ending today or yesterday) with at least one session."""
    logged = set(day_totals(sessions))
    if not logged:
        return 0
    today = date.today()
    cursor = today if today.isoformat() in logged else today - timedelta(days=1)
    if cursor.isoformat() not in logged:
        return 0
    streak = 0
    while cursor.isoformat() in logged:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
