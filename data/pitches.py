# A list of mlb pitch types appearing in statcast
# https://www.daktronics.com/en-us/support/kb/DD3312647
# https://developer.sportradar.com/docs/read/baseball/MLB_v7_with_Statcast#frequently-asked-questions
# Dont change the index, but feel free to change
# the descriptions

PITCH_LONG = {
    "AB": "Auto Ball",  # MLB default is "Automatic Ball"
    "AS": "Auto Strike",  # MLB default is "Automatic Strike"
    "CH": "Change-up",
    "CU": "Curveball",
    "CS": "Slow Curve",
    "EP": "Eephus",
    "FC": "Cutter",
    "FA": "Fastball",
    "FF": "Fastball",  # MLB default is "Four-Seam Fastball"
    "FL": "Slutter",
    "FO": "Forkball",
    "FS": "Splitter",
    "FT": "2 Seamer",  # MLB default is "Two-Seam Fastball"
    "GY": "Gyroball",
    "IN": "Int Ball",  # MLB default is "Intentional Ball"
    "KC": "Knuckle Curve",
    "KN": "Knuckleball",
    "NP": "No Pitch",
    "PO": "Pitchout",
    "SC": "Screwball",
    "SI": "Sinker",
    "SL": "Slider",
    "SU": "Slurve",
    "UN": "Unknown",
}

PITCH_SHORT = {
    "AB": "AB",
    "AS": "AS",
    "CH": "CH",
    "CU": "CU",
    "CS": "CS",
    "EP": "EP",
    "FC": "FC",
    "FA": "FA",
    "FF": "FF",
    "FL": "FL",
    "FO": "FO",
    "FS": "FS",
    "FT": "FT",
    "GY": "GY",
    "IN": "IN",
    "KC": "KC",
    "KN": "KN",
    "NP": "NP",
    "PO": "PO",
    "SC": "SC",
    "SI": "SI",
    "SL": "SL",
    "SU": "SU",
    "UN": "UN",
}


def fetch_long(value):
    return PITCH_LONG.get(value, PITCH_LONG["UN"])


def fetch_short(value):
    return PITCH_SHORT.get(value, PITCH_SHORT["UN"])
