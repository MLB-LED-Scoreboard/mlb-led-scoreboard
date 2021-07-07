import time

import statsapi

import data.teams
import debug
from data import status
from data.game import Game
from data.update import UpdateStatus

GAMES_REFRESH_RATE = 5 * 60


class Schedule:
    def __init__(self, date, config):
        self.date = date.strftime("%Y-%m-%d")
        self.config = config
        self.starttime = time.time()
        self.current_idx = 0
        self.preferred_over = False
        # all games for the day
        self.__all_games = []
        # the actual (filtered) schedule
        self._games = []
        self.update(True)

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            debug.log("Updating schedule for %s", self.date)
            self.starttime = time.time()
            try:
                self.__all_games = statsapi.schedule(self.date)
            except:
                debug.error("Networking error while refreshing schedule")
                return UpdateStatus.FAIL
            else:
                self._games = self.__all_games

                if self.config.rotation_only_preferred:
                    self._games = Schedule.__filter_list_of_games(self.__all_games, self.config.preferred_teams)
                if self.config.rotation_only_live:
                    games = [g for g in self._games if status.is_live(g["status"]) or status.is_fresh(g["status"])]
                    if games:
                        self._games = games

                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        return endtime - self.starttime >= GAMES_REFRESH_RATE

    # offday code
    def is_offday_for_preferred_team(self):
        if self.config.preferred_teams:
            return not any(
                data.teams.TEAM_FULL[self.config.preferred_teams[0]] in [game["away_name"], game["home_name"]]
                for game in self.__all_games  # only care if preferred team is actually in list
            )
        else:
            return True

    def is_offday(self):
        if self.config.standings_no_games:
            return not len(self.__all_games)  # care about all MLB
        else:  # only care if we can't rotate a game
            return not len(self._games)

    def games_live(self):
        return any(status.is_fresh(g["status"]) or (status.is_live(g["status"])) for g in self._games)

    def num_games(self):
        return len(self._games)

    def get_preferred_game(self):
        team_index = self._game_index_for_preferred_team()
        self.current_idx = team_index
        return self.__current_game()

    def next_game(self):
        # We only need to check the preferred team's game status if we're
        # rotating during mid-innings
        # TODO verify during a double-header
        if (
            not self.config.rotation_preferred_team_live_enabled
            and self.config.rotation_preferred_team_live_mid_inning
            and not self.is_offday_for_preferred_team()
            and not self.preferred_over
        ):
            game_index = self._game_index_for_preferred_team()
            preferred_game = Game.from_ID(self._games[game_index]["game_id"], self.date)
            if preferred_game is not None:
                debug.log(
                    "Preferred Team's Game Status: %s, %s %d",
                    preferred_game.status(),
                    preferred_game.inning_state(),
                    preferred_game.inning_number(),
                )

                if status.is_live(preferred_game.status()) and not status.is_inning_break(
                    preferred_game.inning_state()
                ):
                    self.current_idx = game_index
                    debug.log("Moving to preferred game, index: %d", self.current_idx)
                    return preferred_game
                if status.is_complete(preferred_game.status()):
                    self.preferred_over = True

        self.current_idx = self.__next_game_index()
        return self.__current_game()

    def _game_index_for_preferred_team(self):
        if self.config.preferred_teams:
            team_name = data.teams.TEAM_FULL[self.config.preferred_teams[0]]
            team_index = self.current_idx
            team_idxs = [i for i, game in enumerate(self._games) if team_name in [game["away_name"], game["home_name"]]]
            if len(team_idxs) > 0:
                team_index = next(
                    (i for i in team_idxs if status.is_live(self._games[i]["status"])),
                    team_idxs[0],
                )
            return team_index
        else:
            return self.current_idx

    def __next_game_index(self):
        counter = self.current_idx + 1
        if counter >= len(self._games):
            counter = 0
        debug.log("Going to game index %d", counter)
        return counter

    def __current_game(self):
        if self._games:
            return Game.from_ID(self._games[self.current_idx]["game_id"], self.date)
        return None

    @staticmethod
    def __filter_list_of_games(games, filter_teams):
        teams = [data.teams.TEAM_FULL[t] for t in filter_teams]
        return list(game for game in games if set([game["away_name"], game["home_name"]]).intersection(set(teams)))
