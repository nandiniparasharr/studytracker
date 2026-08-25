"""Shared colors and fonts for the Study Tracker UI.

Base palette
------------
GROUND  #FAFAF8   the page behind everything
RAISED  #FFFFFF   cards sitting on the ground
DOTS    #DEDDD6   hairlines, borders, dividers
INK     #17181B   primary text
MUTED   #6E7076   secondary text
ACCENT  #B8496A   the one highlight color

Everything below is either one of those six or derived from them, so the
whole app can be re-skinned from this file alone.
"""

# --------------------------------------------------------------- base
GROUND = "#FAFAF8"
RAISED = "#FFFFFF"
DOTS = "#DEDDD6"
INK = "#17181B"
MUTED = "#6E7076"
ACCENT = "#B8496A"

# ------------------------------------------------------------ derived
ACCENT_DARK = "#9E3D5A"    # pressed / hover on a filled accent
ACCENT_LIGHT = "#D0718B"   # secondary accent fill
ACCENT_SOFT = "#F7E9ED"    # accent at ~12% over white: icon bubbles, hovers

# --------------------------------------------------------- surfaces
BG = GROUND
CARD = RAISED
BORDER = DOTS
TRACK = "#EFEEE9"          # empty half of a progress bar

# ------------------------------------------------------------- text
TEXT = INK
TEXT_MUTED = MUTED
TEXT_FAINT = "#8A8C91"     # out-of-month dates, column headers

# ---------------------------------------------------------- sidebar
# The sidebar is an INK panel, so its scale runs the other way.
SIDEBAR = INK
SIDEBAR_ACTIVE = "#2A2C31"
SIDEBAR_HOVER = "#212328"
SIDEBAR_TEXT = "#A9AAAE"
SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
SIDEBAR_MUTED = MUTED
SIDEBAR_DIVIDER = "#2A2C31"

# --------------------------------------------------------- feedback
POSITIVE = "#5B7F63"       # "up vs last week" - the palette has no green
DANGER = ACCENT            # destructive actions lean on the accent

FONT_FAMILY = "Segoe UI"

# --------------------------------------------- calendar intensity ramp
CAL_NONE = None
CAL_LOW = "#F0CDD8"
CAL_MED = "#DB90A6"
CAL_HIGH = "#C4627F"
CAL_MAX = "#A03D5B"

CAL_LEGEND = [
    ("No study", CAL_NONE),
    ("< 1h", CAL_LOW),
    ("1 - 2h", CAL_MED),
    ("2 - 3h", CAL_HIGH),
    ("> 3h", CAL_MAX),
]
