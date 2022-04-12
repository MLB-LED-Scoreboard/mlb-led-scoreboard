import time
from datetime import datetime, timedelta

import statsapi

import debug
from data import teams
from data.update import UpdateStatus

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


API_FIELDS = (
    "records,standingsType,teamRecords,team,abbreviation,division,league,nameShort,gamesBack,wildCardGamesBack,"
    "wildCardEliminationNumber,clinched,wins,losses"
)


class Standings:
    def __init__(self, config, playoffs_start_date: datetime):
        self.config = config
        self.date = self.__parse_today()
        self.playoffs_start_date = playoffs_start_date.date()
        self.starttime = time.time()
        self.preferred_divisions = config.preferred_divisions
        self.wild_cards = any("Wild" in division for division in config.preferred_divisions)
        self.current_division_index = 0

        self.standings = []
        self.leagues = {}

        self.update(True)

    def __parse_today(self):
        if self.config.demo_date:
            today = datetime.strptime(self.config.demo_date, "%Y-%m-%d")
        else:
            today = datetime.today()
            end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            if end_of_day > datetime.now():
                today -= timedelta(days=1)
        return today.date()

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.date = self.__parse_today()
            debug.log("Refreshing standings for %s", self.date.strftime("%m/%d/%Y"))
            self.starttime = time.time()
            try:
                if not self.is_postseason():

                    season_params = {
                        "standingsTypes": "regularSeason",
                        "leagueId": "103,104",
                        "hydrate": "division,team,league",
                        "season": self.date.strftime("%Y"),
                        "fields": API_FIELDS,
                    }
                    if self.date != datetime.today().date():
                        season_params["date"] = self.date.strftime("%m/%d/%Y")

                    divisons_data = statsapi.get("standings", season_params)
                    self.standings = [Division(division_data) for division_data in divisons_data["records"]]

                    if self.wild_cards:
                        season_params["standingsTypes"] = "wildCard"
                        wc_data = statsapi.get("standings", season_params)
                        self.standings += [Division(data, wc=True) for data in wc_data["records"]]
                else:
                    postseason_data = statsapi.get(
                        "schedule_postseason_series",
                        {
                            "season": self.date.strftime("%Y"),
                            "hydrate": "league,team",
                            "fields": "series,id,gameType,games,description,teams,home,away,team,isWinner,name",
                        },
                    )
                    self.leagues["AL"] = League(postseason_data, "AL")
                    self.leagues["NL"] = League(postseason_data, "NL")

            except:
                debug.exception("Failed to refresh standings.")
                return UpdateStatus.FAIL
            else:

                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= STANDINGS_UPDATE_RATE

    def populated(self):
        return bool(self.standings) or (bool(self.leagues) and self.is_postseason())

    def is_postseason(self):
        return self.date > self.playoffs_start_date

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


class League:
    """Grabs postseason bracket info for one league based on the schedule"""

    def __init__(self, data, league):
        self.name = league
        self.wc1, self.wc2 = self.get_seeds(data, "F", league)
        self.ds_one, _ = self.get_seeds(data, "D", league, "'A'")
        self.ds_two, self.ds_three = self.get_seeds(data, "D", league, "'B'")

        self.wc_winner = self.get_series_winner(data, "F", league)
        self.l_two = self.get_series_winner(data, "D", league, "'A'")
        self.l_one = self.get_series_winner(data, "D", league, "'B'")
        self.champ = self.get_series_winner(data, "L", league)

    @staticmethod
    def get_series_winner(data, gametype, league, series=""):
        series = next(
            s
            for s in data["series"]
            if s["series"]["gameType"] == gametype and league in s["series"]["id"] and series in s["series"]["id"]
        )
        game = series["games"][-1]

        if gametype == "L":
            champ = f"{league}C"
        elif gametype == "F":
            champ = "WCW"
        else:
            champ = "TBD"

        if game["teams"]["home"].get("isWinner"):
            champ = League.get_abbr(game["teams"]["home"]["team"]["name"])
        elif game["teams"]["away"].get("isWinner"):
            champ = League.get_abbr(game["teams"]["away"]["team"]["name"])
        return champ

    @staticmethod
    def get_seeds(data, gametype, league="", series=""):
        series = next(
            s
            for s in data["series"]
            if s["series"]["gameType"] == gametype and league in s["series"]["id"] and series in s["series"]["id"]
        )
        higher, lower = (
            series["games"][0]["teams"]["home"]["team"]["name"],
            series["games"][0]["teams"]["away"]["team"]["name"],
        )

        return (League.get_abbr(higher), League.get_abbr(lower))

    def __str__(self):
        return f"""{self.wc2} ---|
       |--- {self.wc_winner} ---|
{self.wc1} ---|           | --- {self.l_two} ---|
            {self.ds_one} ---|            |
                                | {self.champ}
            {self.ds_three} ---|            |
                   | --- {self.l_one} ---|
            {self.ds_two} ---|
        """

    @staticmethod
    def get_abbr(name, default="TBD"):
        return f"{teams.TEAM_ABBR_LN.get(name, default):>3}"
