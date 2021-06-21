import re

import statsapi

import debug
import time

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


class Standings:
    def __init__(self, date):

        self.date = date
        self.starttime = time.time()

        self.divisions = []

        self.update(True)

    def update(self, force=False):
        succeeded = True
        if force or self.__should_update():
            debug.log("Refreshing standings for %s", self.date.strftime("%m/%d/%Y"))
            self.starttime = time.time()
            try:
                standings_data = statsapi.standings_data(date=self.date.strftime("%m/%d/%Y"))
                self.divisions = [Division(id, division_data) for (id, division_data) in standings_data.items()]
            except AttributeError:
                debug.error("Failed to refresh standings.")
                succeeded = False

        return succeeded

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= STANDINGS_UPDATE_RATE


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
