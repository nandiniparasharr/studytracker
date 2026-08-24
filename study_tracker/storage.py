"""Local JSON persistence for study sessions, subjects and settings.

Everything lives next to this file in a `data/` folder so the app is fully
portable - no database server, no network calls.
"""

import json
import os
import uuid

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Subjects are a color-coded extra, never required to start a session.
DEFAULT_PALETTE = [
    "#f5a524", "#3b82f6", "#22c55e", "#ef4444",
    "#a855f7", "#14b8a6", "#eab308", "#ec4899",
]
UNSPECIFIED_COLOR = "#9ca3af"

DEFAULT_SETTINGS = {"weekly_goal_hours": 20}


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


def save_session(subject, color, seconds, started_at, ended_at, kind):
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
    }
    sessions.append(session)
    _save_json(SESSIONS_FILE, sessions)
    return session


def load_subjects():
    return _load_json(SUBJECTS_FILE, [])


def add_subject(name, color):
    subjects = load_subjects()
    if any(s["name"].lower() == name.lower() for s in subjects):
        return subjects
    subjects.append({"name": name, "color": color})
    _save_json(SUBJECTS_FILE, subjects)
    return subjects


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
