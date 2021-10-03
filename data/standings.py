import time

import statsapi

import debug
from data.update import UpdateStatus

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


API_FIELDS = (
    "records,standingsType,teamRecords,team,abbreviation,division,nameShort,divisionRank,gamesBack,"
    "wildCardEliminationNumber,clinched,wins,losses"
)


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
                standings_data = statsapi.get(
                    "standings",
                    {
                        "standingsTypes": "regularSeason",
                        "leagueId": "103,104",
                        "hydrate": "team(division)",
                        "season": self.date.strftime("%Y"),
                        "fields": API_FIELDS,
                    },
                )
            except:
                debug.error("Failed to refresh standings.")
                return UpdateStatus.FAIL
            else:
                self.divisions = [Division(division_data) for division_data in standings_data["records"]]
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
    def __init__(self, data):
        self.name = data["teamRecords"][0]["team"]["division"]["nameShort"]
        self.teams = [Team(team_data) for team_data in data["teamRecords"]]


class Team:
    def __init__(self, data):
        self.rank = data["divisionRank"]
        self.team_abbrev = data["team"]["abbreviation"]
        self.w = data["wins"]
        self.l = data["losses"]  # noqa: E741
        self.gb = data["gamesBack"]
        self.clinched = data.get("clinched", False)
        self.elim = data.get("wildCardEliminationNumber", "") == "E"
