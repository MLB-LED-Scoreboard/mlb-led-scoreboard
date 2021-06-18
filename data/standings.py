import re

import requests


# TODO use statsapi
class Standings:
    __URL = "https://statsapi.mlb.com/api/v1/standings?season={year}&leagueId={league_ids}"
    "&date={month:0>2}/{day:0>2}/{year}&division=all"
    AL_LEAGUE_ID = "103"
    NL_LEAGUE_ID = "104"
    __LEAGUE_IDS = ",".join([AL_LEAGUE_ID, NL_LEAGUE_ID])

    @classmethod
    def fetch(cls, year, month, day):
        standings_data = requests.get(
            Standings.__URL.format(day=day, month=month, year=year, league_ids=Standings.__LEAGUE_IDS)
        )

        if standings_data.status_code == 200:
            return Standings(standings_data.json())
        else:
            raise Exception("Could not fetch standings.")

    def __init__(self, data):
        self.__data = data
        self.divisions = self.__fetch_divisions()

    def __fetch_divisions(self):
        return [Division(division_data) for division_data in self.__data["records"]]


class Division:
    def __init__(self, data):
        self.__data = data
        self.id = self.__data["division"]["id"]
        self.name = self.__name()
        self.teams = self.__teams()

    def __name(self):
        division_records = self.__data["teamRecords"][0]["records"]["divisionRecords"]
        full_name = [datum["division"]["name"] for datum in division_records if datum["division"]["id"] == self.id][0]

        # Use some regex to fix the division full name to what the config expects
        return re.sub(r"(ational|merican)\sLeague", "L", full_name)

    def __teams(self):
        return [Team(team_data, self.id) for team_data in self.__data["teamRecords"]]


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

    def __init__(self, data, division_id):
        self.__data = data
        self.__division_standings = self.__data["leagueRecord"]
        self.name = self.__name()
        self.team_abbrev = self.__TEAM_ABBREVIATIONS[self.name]
        self.w = self.__parse_wins()
        self.l = self.__parse_losses()
        self.gb = self.__data["divisionGamesBack"]

    def __find_division(self, division_id):
        for record in self.__data["records"]["divisionRecords"]:
            if record["division"]["id"] == division_id:
                return record

        raise Exception("Could not find division record.")

    def __name(self):
        return self.__data["team"]["name"]

    def __parse_wins(self):
        return self.__division_standings["wins"]

    def __parse_losses(self):
        return self.__division_standings["losses"]
