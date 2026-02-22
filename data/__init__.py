from typing import Literal

from data import update
import debug
from data.game import Game
from data.headlines import Headlines
from data.schedule import Schedule
from data.standings import Standings
from data.update import UpdateStatus
from data.weather import Weather
from data.screens import ScreenType


class Data:
    def __init__(self, config) -> None:
        # Save the parsed config
        self.config = config

        # get schedule
        self.schedule: Schedule = Schedule(config)

        # NB: Can return none, but shouldn't matter?
        self.current_game: Game = self.schedule.get_preferred_game()

        # render thread can switch to next
        self.next_game: Game = Game.from_scheduled(
            self.schedule.next_game(), self.config.preferred_game_delay_multiplier, self.config.api_refresh_rate
        )
        self.rendering: Literal["current"] | Literal["next"] = "current"
        self.next_requested = None
        # main thread acknowledges, so it can switch back to current
        self.acknowledged_next_game: bool = False

        if self.current_game is not None:
            self.current_game.print_game_data_debug()

        # Weather info
        self.weather: Weather = Weather(config)

        # News headlines
        self.headlines: Headlines = Headlines(config, self.schedule.date.year)

        # Fetch all standings data for today
        self.standings: Standings = Standings(config, self.headlines.important_dates.playoffs_start_date)

        # Network status state - we useweather condition as a sort of sentinial value
        self.network_issues: bool = self.weather.conditions == "Error"

    def refresh_game(self):
        # handle double buffering
        if self.rendering == "next":
            debug.log("Main thread: acknowledging render thread's request to read 'next', mirroring into 'current'")
            self.current_game = self.next_game
            self.acknowledged_next_game = True

        if self.rendering == "current" and self.acknowledged_next_game:
            self.acknowledged_next_game = False
            debug.log("Main thread: render thread has switched back to 'current', advancing 'next' game")
            if self.next_requested is None:
                self.network_issues = True
            elif self.next_requested["game_id"] != self.next_game.game_id:
                # prefer to keep the old next game if it's the same, for better delay buffering
                next_game = Game.from_scheduled(
                    self.next_requested, self.config.preferred_game_delay_multiplier, self.config.api_refresh_rate
                )
                if next_game is None:
                    self.network_issues = True
                else:
                    self.next_game = next_game
            self.next_requested = None

        # network requests
        self.__process_network_status(update.merge(self.current_game.update(), self.next_game.update()))

    def refresh_standings(self):
        self.__process_network_status(self.standings.update())

    def refresh_weather(self):
        self.__process_network_status(self.weather.update())

    def refresh_news_ticker(self):
        self.__process_network_status(self.headlines.update())

    def refresh_schedule(self, force=False):
        self.__process_network_status(self.schedule.update(force))

    def __process_network_status(self, status):
        if status == UpdateStatus.SUCCESS:
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True

    def get_screen_type(self) -> ScreenType:
        # Always the news
        if self.config.news_ticker_always_display:
            return ScreenType.ALWAYS_NEWS
        # Always the standings
        if self.config.standings_always_display:
            return ScreenType.ALWAYS_STANDINGS
        # Full MLB Offday
        if self.schedule.is_offday():
            return ScreenType.LEAGUE_OFFDAY

        # Preferred Team Offday
        if self.schedule.is_offday_for_preferred_team() and (
            self.config.news_ticker_team_offday or self.config.standings_team_offday
        ):
            return ScreenType.PREFERRED_TEAM_OFFDAY

        # Playball!
        return ScreenType.GAMEDAY

    def get_rendering_game(self) -> Game:
        if self.rendering == "current":
            return self.current_game
        else:
            return self.next_game
