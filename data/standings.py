import time
from datetime import datetime

import statsapi

import debug
from data import teams
from data.update import UpdateStatus
import data.headers

STANDINGS_UPDATE_RATE = 15 * 60  # 15 minutes between standings updates


API_FIELDS = (
    "records,standingsType,teamRecords,team,id,abbreviation,division,league,nameShort,gamesBack,wildCardGamesBack,"
    "wildCardEliminationNumber,clinched,wins,losses"
)


class Standings:
    def __init__(self, config, playoffs_start_date: datetime):
        self.config = config
        self.date = self.config.parse_today()
        self.playoffs_start_date = playoffs_start_date.date()
        self.starttime = time.time()
        self.preferred_divisions = config.preferred_divisions
        self.wild_cards = any("Wild" in division for division in config.preferred_divisions)
        self.current_division_index = 0

        self.standings = []
        self.leagues = {}

        self.update(True)


    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.date = self.config.parse_today()
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

                    divisons_data = statsapi.get("standings", season_params, request_kwargs={"headers": data.headers.API_HEADERS})
                    standings = [Division(division_data) for division_data in divisons_data["records"]]

                    if self.wild_cards:
                        season_params["standingsTypes"] = "wildCard"
                        wc_data = statsapi.get("standings", season_params, request_kwargs={"headers": data.headers.API_HEADERS})
                        standings += [Division(data, wc=True) for data in wc_data["records"]]

                    self.standings = standings

                else:
                    postseason_data = statsapi.get(
                        "schedule_postseason_series",
                        {
                            "season": self.date.strftime("%Y"),
                            "hydrate": "league,team",
                            "fields": "series,id,gameType,games,description,teams,home,away,team,isWinner,name",
                        },
                        request_kwargs={"headers": data.headers.API_HEADERS}
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
        self.team_abbrev = teams.TEAM_ID_ABBR[data["team"]["id"]]
        self.w = data["wins"]
        self.l = data["losses"]  # noqa: E741
        if wc:
            self.gb = data["wildCardGamesBack"]
        else:
            self.gb = data["gamesBack"]
        self.clinched = data.get("clinched", False)
        self.elim = data.get("wildCardEliminationNumber", "") == "E"

NL_IDS = {'wc36': 'F_3', 'wc45': 'F_4', 'dsA': 'D_3', 'dsB': 'D_4', 'cs': 'L_2' }
AL_IDS = {'wc36': 'F_1', 'wc45': 'F_2', 'dsA': 'D_1', 'dsB': 'D_2', 'cs': 'L_1' }

class League:
    """Grabs postseason bracket info for one league based on the schedule"""

    def __init__(self, data, league):
        self.name = league
        if league == 'NL':
            ids = NL_IDS
        else:
            ids = AL_IDS

        self.wc3, self.wc6 = self.get_seeds(data, ids['wc36'])
        self.wc4, self.wc5 = self.get_seeds(data, ids['wc45'])

        self.ds_A_bye, _ = self.get_seeds(data, ids['dsA'])
        self.ds_B_bye, _ = self.get_seeds(data, ids['dsB'])

        self.wc36_winner = self.get_series_winner(data,  ids['wc36'])
        self.wc45_winner = self.get_series_winner(data,  ids['wc45'])
        self.l_two = self.get_series_winner(data, ids['dsA'])
        self.l_one = self.get_series_winner(data, ids['dsB'])
        self.champ = self.get_series_winner(data, ids['cs'])

    def get_series_winner(self, data, ID):
        series = next(
            s
            for s in data["series"]
            if s["series"]["id"] == ID
        )
        game = series["games"][-1]
        if "L" in ID:
            champ = f"{self.name}C"
        elif 'F' in ID:
            if '3' in ID or '1' in ID:
                champ = "W36"
            else:
                champ = "W45"
        else:
            champ = "TBD"
        if game["teams"]["home"].get("isWinner"):
            champ = get_abbr(game["teams"]["home"]["team"]["id"])
        elif game["teams"]["away"].get("isWinner"):
            champ = get_abbr(game["teams"]["away"]["team"]["id"])
        return champ

    @staticmethod
    def get_seeds(data, ID):
        series = next(
            s
            for s in data["series"]
            if s["series"]["id"] == ID
        )
        higher, lower = (
            series["games"][0]["teams"]["home"]["team"]["id"],
            series["games"][0]["teams"]["away"]["team"]["id"],
        )

        return (get_abbr(higher), get_abbr(lower))

    def __str__(self):
        return f"""{self.wc5} ---|
       |--- {self.wc45_winner} ---|
{self.wc6} ---|           | --- {self.l_two} ---|
            {self.ds_B_bye} ---|            |
{self.wc6} ---|                        | {self.champ}
       |--- {self.wc36_winner} ---|            |
{self.wc3} ---|           | --- {self.l_one} ---|
            {self.ds_A_bye} ---|
        """


def get_abbr(id, default="TBD"):
    return f"{teams.TEAM_ID_ABBR.get(id, default):>3}"
