import re
import time

import statsapi

import debug
from data.update import UpdateStatus

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


class Standings:
    def __init__(self, date, preferred_divisions):

        self.date = date
        self.starttime = time.time()
        self.preferred_divisions = preferred_divisions
        self.current_division_index = 0

        self.divisions = []

        self.update(True)

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            debug.log("Refreshing standings for %s", self.date.strftime("%m/%d/%Y"))
            self.starttime = time.time()
            try:
                standings_data = statsapi.standings_data(date=self.date.strftime("%m/%d/%Y"))
            except:
                debug.error("Failed to refresh standings.")
                return UpdateStatus.FAIL
            else:
                self.divisions = [Division(id, division_data) for (id, division_data) in standings_data.items()]
                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= STANDINGS_UPDATE_RATE

    def standings_for_preferred_division(self):
        return self.__standings_for(self.preferred_divisions[0])

    def __standings_for(self, division_name):
        return next(division for division in self.divisions if division.name == division_name)

    def current_standings(self):
        return self.__standings_for(self.preferred_divisions[self.current_division_index])

    def advance_to_next_standings(self):
        self.current_division_index = self.__next_division_index()
        return self.current_standings()

    def __next_division_index(self):
        counter = self.current_division_index + 1
        if counter >= len(self.preferred_divisions):
            counter = 0
        return counter


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
        self.l = data["l"]  # noqa: E741
        self.gb = data["gb"]
