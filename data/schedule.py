import time
from datetime import datetime, timedelta

import statsapi

import data.teams
import debug
from data import status
from data.game import Game
from data.update import UpdateStatus

GAMES_REFRESH_RATE = 6 * 60


class Schedule:
    def __init__(self, config):
        self.config = config
        self.date = self.__parse_today()
        self.starttime = time.time()
        self.current_idx = 0
        # all games for the day
        self.__all_games = []
        # the actual (filtered) schedule
        self._games = []
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
        return today

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.date = self.__parse_today()
            debug.log("Updating schedule for %s", self.date)
            self.starttime = time.time()
            try:
                self.__all_games = statsapi.schedule(self.date.strftime("%Y-%m-%d"))
            except:
                debug.exception("Networking error while refreshing schedule")
                return UpdateStatus.FAIL
            else:
                games = self.__all_games

                if self.config.rotation_only_preferred:
                    games = Schedule.__filter_list_of_games(self.__all_games, self.config.preferred_teams)
                if self.config.rotation_only_live:
                    live_games = [g for g in games if status.is_live(g["status"]) or status.is_fresh(g["status"])]
                    if live_games:
                        # we never have games drop down to [], since we may still be indexing into it
                        # but this is fine, since self.games_live() is will work even if we don't do this update
                        games = live_games

                if len(games) > 0:
                    self.current_idx %= len(games)

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
                data.teams.TEAM_NAME_ID[self.config.preferred_teams[0]] in [game["away_id"], game["home_id"]]
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
        if (
            not self.config.rotation_preferred_team_live_enabled
            and self.config.rotation_preferred_team_live_mid_inning
            and not self.is_offday_for_preferred_team()
        ):
            game_index = self._game_index_for_preferred_team()
            if game_index >= 0:  # we return -1 if no live games for preferred team
                scheduled_game = self._games[game_index]
                preferred_game = Game.from_scheduled(scheduled_game, self.config.delay_in_10s_of_seconds)
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


        self.current_idx = self.__next_game_index()
        return self.__current_game()

    def _game_index_for_preferred_team(self):
        if self.config.preferred_teams:
            team_id = data.teams.TEAM_NAME_ID[self.config.preferred_teams[0]]
            return next(
                (
                    i
                    for i, game in enumerate(self._games)
                    if team_id in [game["away_id"], game["home_id"]] and status.is_live(game["status"])
                ),
                -1,  # no live games for preferred team
            )

        return -1  # no preferred team

    def __next_game_index(self):
        counter = self.current_idx + 1
        if counter >= len(self._games):
            counter = 0
        debug.log("Going to game index %d", counter)
        return counter

    def __current_game(self):
        if self._games:
            scheduled_game = self._games[self.current_idx]
            return Game.from_scheduled(scheduled_game, self.config.delay_in_10s_of_seconds)
        return None

    @staticmethod
    def __filter_list_of_games(games, filter_teams):
        teams = set(data.teams.TEAM_NAME_ID[t] for t in filter_teams)
        return list(game for game in games if set([game["away_id"], game["home_id"]]).intersection(teams))
