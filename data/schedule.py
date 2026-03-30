import datetime
import time
from collections import defaultdict
from typing import Any, Optional
from math import ceil

import statsapi

import debug
from data.game import Game
from bullpen.api import UpdateStatus
from data.utils.circular_queue import CircularQueue
from data.config import Config

GAMES_REFRESH_RATE = 15


class Schedule:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.date = self.config.parse_today()
        self.starttime = time.time()
        self.current_idx = 0

        delay_required = ceil(self.config.sync_delay_seconds / GAMES_REFRESH_RATE)

        self._data_wait_queue = CircularQueue(delay_required + 1)
        # the (filtered) schedule
        self._games: list[dict[str, Any]] = []
        self.priority = 0
        self.update(True)

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.date = self.config.parse_today()
            debug.log("Updating schedule for %s", self.date)
            self.starttime = time.time()
            try:
                # add sportId=51 to additionally get WBC games
                all_games = statsapi.schedule(self.date.strftime("%Y-%m-%d"), sportId="1,51")
            except:
                debug.exception("Networking error while refreshing schedule")
                return UpdateStatus.FAIL
            else:

                priority, games = self.__filter_games(all_games)
                if priority > self.priority:
                    # going up a priority level should never be delayed
                    self._data_wait_queue.clear()
                self._data_wait_queue.push((priority, games))

                priority, games = self._data_wait_queue.peek()

                if len(games) > 0:
                    self.current_idx %= len(games)
                else:
                    self.current_idx = 0

                self._games = games
                self.priority = priority
                debug.log(
                    "Schedule updated with %d games (priority %d) (current delay %d)",
                    len(self._games),
                    priority,
                    self.current_delay(),
                )
                return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        return endtime - self.starttime >= GAMES_REFRESH_RATE

    def current_delay(self):
        return (len(self._data_wait_queue) - 1) * GAMES_REFRESH_RATE

    def num_games(self):
        return len(self._games)

    def next_game(self, unless: Optional[Game] = None) -> Optional[Game]:
        self.current_idx = self.__next_game_index()
        return self.__current_game(unless)

    def __next_game_index(self):
        counter = self.current_idx + 1
        if counter >= len(self._games):
            counter = 0
        if counter != self.current_idx:
            debug.log("Schedule: going to game index %d", counter)
        return counter

    def __current_game(self, unless: Optional[Game] = None):
        try:
            scheduled_game = self._games[self.current_idx]
            if unless and scheduled_game["game_id"] == unless.game_id:
                return unless
            return Game.from_scheduled(scheduled_game, self.config.sync_amount, self.config.api_refresh_rate)
        except IndexError:
            return None

    def __filter_games(self, all_games: list) -> tuple[int, list]:
        """
        Returns the highest priority level and the games that match that level,
        for the given list of games and current time.
        """
        priorities: defaultdict[int, list] = defaultdict(list)
        highest = 0

        for rule in self.config.rotation_time_rules:
            priority = rule.matches(datetime.datetime.now().time())
            if priority:
                highest = max(highest, priority)

        for game in all_games:
            seen = set()
            for rule in self.config.rotation_game_rules:
                if rule.priority() < highest:
                    continue
                priority, passive = rule.matches(game)
                if priority:
                    if priority not in seen:
                        priorities[priority].append(game)
                        seen.add(priority)

                    if not passive:
                        highest = max(highest, priority)

        return highest, priorities[highest]
