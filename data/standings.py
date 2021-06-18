import re
import statsapi


class Standings:
    def __init__(self, date):
        standings_data = statsapi.standings_data(date=date.strftime("%m/%d/%Y"))

        self.divisions = [Division(id, division_data) for (id, division_data) in standings_data.items()]


class Division:
    def __init__(self, id, data):
        self.id = id
        self.name = re.sub(r"(ational|merican)\sLeague", "L", data["div_name"])
        self.teams = [Team(team_data) for team_data in data["teams"]]


class Team:
    __TEAM_ABBREVIATIONS = {
        "Arizona Diamondbacks": "ARI",
        "Atlanta Braves": "ATL",
        "Baltimore Orioles": "BAL",
        "Boston Red Sox": "BOS",
        "Chicago Cubs": "CHC",
        "Chicago White Sox": "CHW",
        "Cincinnati Reds": "CIN",
        "Cleveland Indians": "CLE",
        "Colorado Rockies": "COL",
        "Detroit Tigers": "DET",
        "Florida Marlins": "FLA",
        "Houston Astros": "HOU",
        "Kansas City Royals": "KAN",
        "Los Angeles Angels": "LAA",
        "Los Angeles Dodgers": "LAD",
        "Miami Marlins": "MIA",
        "Milwaukee Brewers": "MIL",
        "Minnesota Twins": "MIN",
        "New York Mets": "NYM",
        "New York Yankees": "NYY",
        "Oakland Athletics": "OAK",
        "Philadelphia Phillies": "PHI",
        "Pittsburgh Pirates": "PIT",
        "San Diego Padres": "SD",
        "San Francisco Giants": "SF",
        "Seattle Mariners": "SEA",
        "St. Louis Cardinals": "STL",
        "Tampa Bay Rays": "TB",
        "Texas Rangers": "TEX",
        "Toronto Blue Jays": "TOR",
        "Washington Nationals": "WAS",
    }

    def __init__(self, data):
        self.rank = data["div_rank"]
        self.name = data["name"]
        self.team_abbrev = self.__TEAM_ABBREVIATIONS[self.name]
        self.w = data["w"]
        self.l = data["l"]
        self.gb = data["gb"]
