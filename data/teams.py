# These are special teams in the league and not present in the api/v1/teams endpoint.
_SPECIAL_TEAMS = {
    159: { "abbr": "AL",  "name": "American League All-Stars" },
    160: { "abbr": "NL",  "name": "National League All-Stars" },
}

# Run this file to retreive the latest team data from the MLB API.
_TEAMS = _SPECIAL_TEAMS | {
    108: { "abbr": "LAA", "name": "Angels" },
    109: { "abbr": "AZ",  "name": "D-backs" },
    110: { "abbr": "BAL", "name": "Orioles" },
    111: { "abbr": "BOS", "name": "Red Sox" },
    112: { "abbr": "CHC", "name": "Cubs" },
    113: { "abbr": "CIN", "name": "Reds" },
    114: { "abbr": "CLE", "name": "Guardians" },
    115: { "abbr": "COL", "name": "Rockies" },
    116: { "abbr": "DET", "name": "Tigers" },
    117: { "abbr": "HOU", "name": "Astros" },
    118: { "abbr": "KC",  "name": "Royals" },
    119: { "abbr": "LAD", "name": "Dodgers" },
    120: { "abbr": "WSH", "name": "Nationals" },
    121: { "abbr": "NYM", "name": "Mets" },
    133: { "abbr": "ATH", "name": "Athletics" },
    134: { "abbr": "PIT", "name": "Pirates" },
    135: { "abbr": "SD",  "name": "Padres" },
    136: { "abbr": "SEA", "name": "Mariners" },
    137: { "abbr": "SF",  "name": "Giants" },
    138: { "abbr": "STL", "name": "Cardinals" },
    139: { "abbr": "TB",  "name": "Rays" },
    140: { "abbr": "TEX", "name": "Rangers" },
    141: { "abbr": "TOR", "name": "Blue Jays" },
    142: { "abbr": "MIN", "name": "Twins" },
    143: { "abbr": "PHI", "name": "Phillies" },
    144: { "abbr": "ATL", "name": "Braves" },
    145: { "abbr": "CWS", "name": "White Sox" },
    146: { "abbr": "MIA", "name": "Marlins" },
    147: { "abbr": "NYY", "name": "Yankees" },
    158: { "abbr": "MIL", "name": "Brewers" },
}

# Convenience dictionaries for quick lookups
TEAM_ID_ABBR  = { ID: t["abbr"] for ID, t in _TEAMS.items() }
TEAM_ID_NAME  = { ID: t["name"] for ID, t in _TEAMS.items() }
_TEAM_NAME_ID = { t["name"]: ID for ID, t in _TEAMS.items() }

def get_team_id(team_name):
    try:
        return _TEAM_NAME_ID[team_name]
    except KeyError:
        # this function is only ever given user's config as input
        # so we provide a more exact error message
        raise ValueError(f"Unknown team name: {team_name}")
    
def _fetch_team_data():
    import json, os, statsapi

    SPORT_ID = "1"
    _teams = statsapi.get("teams", { "sportId": SPORT_ID })["teams"]
    _teams.sort(key=lambda t: t["id"])

    teams = {}

    for team in _teams:
        teams[team["id"]] = {
            "abbr": team["abbreviation"],
            "name": team["name"],
        }

    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "teams.log")
    norm_path = os.path.normpath(log_path)

    with open(norm_path, "w") as f:
        json.dump(teams, f, indent=4)
    
    print(f"Team data written to {norm_path}")

    return teams

if __name__ == "__main__":
    _fetch_team_data()
