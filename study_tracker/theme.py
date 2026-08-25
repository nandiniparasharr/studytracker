"""Shared colors and fonts for the Study Tracker UI (plum / cream theme)."""

# Sidebar
SIDEBAR = "#33182B"
SIDEBAR_ACTIVE = "#4E2742"
SIDEBAR_HOVER = "#42203899"
SIDEBAR_TEXT = "#C9B3C1"
SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
SIDEBAR_MUTED = "#9C8394"
SIDEBAR_DIVIDER = "#4A2340"

# Surfaces
BG = "#FAF7F8"
CARD = "#FFFFFF"
BORDER = "#EFE6EA"
TRACK = "#F0E7EB"

# Brand
PLUM = "#5C2444"
PLUM_MID = "#7B3B5E"
PLUM_LIGHT = "#8E4A6B"
PLUM_SOFT = "#F3E6EC"
PINK = "#C4638F"

# Text
TEXT = "#2E1B2E"
TEXT_MUTED = "#8A7480"
TEXT_FAINT = "#B9A6B0"

# Feedback
GREEN = "#5E8C63"

FONT_FAMILY = "Segoe UI"

# Calendar intensity ramp (matches the dashboard legend)
CAL_NONE = None
CAL_LOW = "#EBC7D8"
CAL_MED = "#C4739B"
CAL_HIGH = "#8E4A6B"
CAL_MAX = "#5C2444"

CAL_LEGEND = [
    ("No study", CAL_NONE),
    ("< 1h", CAL_LOW),
    ("1 - 2h", CAL_MED),
    ("2 - 3h", CAL_HIGH),
    ("> 3h", CAL_MAX),
]
