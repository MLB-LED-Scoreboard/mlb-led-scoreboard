# the following were created like so
# import statsapi
# _teams = statsapi.get('teams', {'sportIds':1})['teams']
# TEAM_ID_ABBR = {t["id"]: t["abbreviation"] for t in _teams}
# TEAM_ID_NAME = {t["id"]: t["teamName"] for t in _teams}
# TEAM_NAME_ID = {t["teamName"]: t["id"] for t in _teams}

# Can be customized, but will require changing in colors/teams.json as well
TEAM_ID_ABBR = {
    133: "ATH",
    134: "PIT",
    135: "SD",
    136: "SEA",
    137: "SF",
    138: "STL",
    139: "TB",
    140: "TEX",
    141: "TOR",
    142: "MIN",
    143: "PHI",
    144: "ATL",
    145: "CWS",
    146: "MIA",
    147: "NYY",
    158: "MIL",
    108: "LAA",
    109: "AZ",
    110: "BAL",
    111: "BOS",
    112: "CHC",
    113: "CIN",
    114: "CLE",
    115: "COL",
    116: "DET",
    117: "HOU",
    118: "KC",
    119: "LAD",
    120: "WSH",
    121: "NYM",
}

# Can be customized
TEAM_ID_NAME = {
    133: "Athletics",
    134: "Pirates",
    135: "Padres",
    136: "Mariners",
    137: "Giants",
    138: "Cardinals",
    139: "Rays",
    140: "Rangers",
    141: "Blue Jays",
    142: "Twins",
    143: "Phillies",
    144: "Braves",
    145: "White Sox",
    146: "Marlins",
    147: "Yankees",
    158: "Brewers",
    108: "Angels",
    109: "D-backs",
    110: "Orioles",
    111: "Red Sox",
    112: "Cubs",
    113: "Reds",
    114: "Guardians",
    115: "Rockies",
    116: "Tigers",
    117: "Astros",
    118: "Royals",
    119: "Dodgers",
    120: "Nationals",
    121: "Mets",
}


# Can be customized, but names in the config.json file must match
_TEAM_NAME_ID = {
    "Athletics": 133,
    "Pirates": 134,
    "Padres": 135,
    "Mariners": 136,
    "Giants": 137,
    "Cardinals": 138,
    "Rays": 139,
    "Rangers": 140,
    "Blue Jays": 141,
    "Twins": 142,
    "Phillies": 143,
    "Braves": 144,
    "White Sox": 145,
    "Marlins": 146,
    "Yankees": 147,
    "Brewers": 158,
    "Angels": 108,
    "D-backs": 109,
    "Orioles": 110,
    "Red Sox": 111,
    "Cubs": 112,
    "Reds": 113,
    "Guardians": 114,
    "Rockies": 115,
    "Tigers": 116,
    "Astros": 117,
    "Royals": 118,
    "Dodgers": 119,
    "Nationals": 120,
    "Mets": 121,
}

def get_team_id(team_name):
    try:
        return _TEAM_NAME_ID[team_name]
    except KeyError:
        # this function is only ever given user's config as input
        # so we provide a more exact error message
        raise ValueError(f"Unknown team name: {team_name}")
