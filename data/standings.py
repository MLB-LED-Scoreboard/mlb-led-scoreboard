from datetime import datetime
import time

import statsapi

import debug
from data.update import UpdateStatus

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


API_FIELDS = (
    "records,standingsType,teamRecords,team,abbreviation,division,league,nameShort,gamesBack,wildCardGamesBack,"
    "wildCardEliminationNumber,clinched,wins,losses"
)


class Standings:
    def __init__(self, date: datetime, preferred_divisions):

        self.date = date
        self.starttime = time.time()
        self.preferred_divisions = preferred_divisions
        self.wild_cards = any("Wild" in division for division in preferred_divisions)
        self.current_division_index = 0

        self.standings = []

        self.update(True)

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            debug.log("Refreshing standings for %s", self.date.strftime("%m/%d/%Y"))
            self.starttime = time.time()
            try:
                params = {
                    "standingsTypes": "regularSeason",
                    "leagueId": "103,104",
                    "hydrate": "division,team,league",
                    "season": self.date.strftime("%Y"),
                    "fields": API_FIELDS,
                }
                if self.date.date() != datetime.today().date():
                    params["date"] = self.date.strftime("%m/%d/%Y")

                divisons_data = statsapi.get("standings", params)
                if self.wild_cards:
                    params["standingsTypes"] = "wildCard"
                    wc_data = statsapi.get("standings", params)
            except:
                debug.error("Failed to refresh standings.")
                return UpdateStatus.FAIL
            else:
                self.standings = [Division(division_data) for division_data in divisons_data["records"]]
                if self.wild_cards:
                    self.standings += [Division(data, wc=True) for data in wc_data["records"]]
                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= STANDINGS_UPDATE_RATE

    def standings_for_preferred_division(self):
        return self.__standings_for(self.preferred_divisions[0])

    def __standings_for(self, division_name):
        return next(division for division in self.standings if division.name == division_name)

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
    def __init__(self, data, wc=False):
        if wc:
            self.name = data["league"]["abbreviation"] + " Wild Card"
        else:
            self.name = data["division"]["nameShort"]
        self.teams = [Team(team_data, wc) for team_data in data["teamRecords"][:5]]


class Team:
    def __init__(self, data, wc):
        self.team_abbrev = data["team"]["abbreviation"]
        self.w = data["wins"]
        self.l = data["losses"]  # noqa: E741
        if wc:
            self.gb = data["wildCardGamesBack"]
        else:
            self.gb = data["gamesBack"]
        self.clinched = data.get("clinched", False)
        self.elim = data.get("wildCardEliminationNumber", "") == "E"
