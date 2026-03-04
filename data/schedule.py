from collections import defaultdict
import time
from typing import Optional

import statsapi

import debug
from data.game import Game
from data.update import UpdateStatus
from data.config import GameRule, Config

GAMES_REFRESH_RATE = 15


class Schedule:
    def __init__(self, config: Config):
        self.config = config
        self.date = self.config.parse_today()
        self.starttime = time.time()
        self.current_idx = 0
        # all games for the day
        self.__all_games = []
        # the actual (filtered) schedule
        self._games = []
        self.update(True)

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.date = self.config.parse_today()
            debug.log("Updating schedule for %s", self.date)
            self.starttime = time.time()
            try:
                self.__all_games = statsapi.schedule(self.date.strftime("%Y-%m-%d"))
            except:
                debug.exception("Networking error while refreshing schedule")
                return UpdateStatus.FAIL
            else:
                games = self.__all_games

                priority, games = self.__filter_rules(self.config.rotation_rules)

                if len(games) > 0:
                    self.current_idx %= len(games)
                else:
                    self.current_idx = 0

                self._games = games
                self.priority = priority
                debug.log("Schedule updated with %d games (priority %d)", len(self._games), priority)
                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        return endtime - self.starttime >= GAMES_REFRESH_RATE

    def num_games(self):
        return len(self._games)

    def next_game(self, *, unless: Optional[Game] = None):
        self.current_idx = self.__next_game_index()
        return self.__current_game(unless)

    def __next_game_index(self):
        counter = self.current_idx + 1
        if counter >= len(self._games):
            counter = 0
        debug.log("Schedule: going to game index %d", counter)
        return counter

    def __current_game(self, unless: Optional[Game] = None):
        try:
            scheduled_game = self._games[self.current_idx]
            if unless and scheduled_game["game_id"] == unless.game_id:
                return unless
            # TODO(bmw): tie config for delay etc to priority somehow?
            return Game.from_scheduled(
                scheduled_game, self.config.preferred_game_delay_multiplier, self.config.api_refresh_rate
            )
        except IndexError:
            return None

    def __filter_rules(self, rules: list[GameRule]) -> tuple[int, list]:
        priorities: defaultdict[int, list] = defaultdict(list)
        non_passive_priorities = set()
        for game in self.__all_games:
            seen = set()
            for rule in rules:
                priority, passive = rule.matches(game)
                if priority:
                    if priority not in seen:
                        priorities[priority].append(game)
                        seen.add(priority)

                    if not passive:
                        non_passive_priorities.add(priority)
        highest = max(non_passive_priorities, default=0)
        return highest, priorities[highest]
