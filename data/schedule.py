import datetime
import time
from collections import defaultdict
from typing import Any, Optional
from math import ceil

import statsapi
import wpbl_statsapi_adaptor

from bullpen.logging import LOGGER
from data.game import Game
from bullpen.api import UpdateStatus
from data.utils.circular_queue import CircularQueue
from data.config import Config

GAMES_REFRESH_RATE = 15


class Schedule:
    def __init__(self, config: Config) -> None:
        self.config = config
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
            date = self.config.parse_today().strftime("%Y-%m-%d")
            LOGGER.debug("Updating schedule for %s", date)
            self.starttime = time.time()
            all_games = []
            try:
                if self.config.statsapi_schedule_sport_ids or self.config.statsapi_schedule_league_ids:
                    all_games = statsapi.schedule(
                        date,
                        sportId=self.config.statsapi_schedule_sport_ids,
                        leagueId=self.config.statsapi_schedule_league_ids,
                    )
            except Exception:
                LOGGER.exception("Networking error while refreshing MLB schedule")

            try:
                if self.config.wants_wpbl:
                    wpbl_games = wpbl_statsapi_adaptor.schedule(date)
                    all_games.extend(wpbl_games)
            except Exception:
                LOGGER.exception("Networking error while refreshing WPBL schedule")

            if not all_games:
                return UpdateStatus.FAIL

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
            LOGGER.debug(
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
            LOGGER.debug("Schedule: going to game index %d", counter)
        return counter

    def __current_game(self, unless: Optional[Game] = None) -> Optional[Game]:
        try:
            scheduled_game = self._games[self.current_idx]
            if unless and scheduled_game["game_id"] == unless.game_id:
                return unless
            return Game.from_scheduled(scheduled_game, self.config)
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
            priority = rule.matches(datetime.datetime.now())
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
