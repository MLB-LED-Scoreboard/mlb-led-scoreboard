import time
from data.screens import ScreenType

import debug
from data import status
from data.game import Game
from data.headlines import Headlines
from data.schedule import Schedule
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from data.standings import Standings
from data.update import UpdateStatus
from data.weather import Weather


class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # get schedule
        self.schedule: Schedule = Schedule(config)
        # NB: Can return none, but shouldn't matter?
        self.current_game: Game = self.schedule.get_preferred_game()

        self.game_changed_time = time.time()
        if self.current_game is not None:
            self.print_game_data_debug()
            self.__update_layout_state()

        # Weather info
        self.weather: Weather = Weather(config)

        # News headlines
        self.headlines: Headlines = Headlines(config, self.schedule.date.year)

        # Fetch all standings data for today
        self.standings: Standings = Standings(config, self.headlines.important_dates.playoffs_start_date)

        # Network status state - we useweather condition as a sort of sentinial value
        self.network_issues: bool = self.weather.conditions == "Error"

        # RENDER ITEMS
        self.scrolling_finished: bool = False

    def should_rotate_to_next_game(self):
        if not self.config.rotation_enabled:
            # never rotate
            return False

        if self.config.rotation_preferred_team_live_enabled or not self.config.preferred_teams:
            # if there's no preferred team, or if we rotate during their games, always rotate
            return True

        game = self.current_game

        if status.is_live(game.status()):
            if self.schedule.num_games() <= 1:
                # don't rotate if this is the only game
                return False

            # if we're here, it means we should pause on the preferred team's games
            if game.features_team(self.config.preferred_teams[0]):
                # unless we're allowed to rotate during mid-inning breaks
                return self.config.rotation_preferred_team_live_mid_inning and status.is_inning_break(game.inning_state())

        # if our current game isn't live, we might as well try to rotate.
        # this should help most issues with games getting stuck
        return True

    def refresh_game(self):
        status = self.current_game.update()
        if status == UpdateStatus.SUCCESS:
            self.__update_layout_state()
            self.print_game_data_debug()
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True


    def advance_to_next_game(self):
        game = self.schedule.next_game()
        if game is None:
            self.network_issues = True
            return

        if game.game_id != self.current_game.game_id:
            self.current_game = game
            self.game_changed_time = time.time()
            self.__update_layout_state()
            self.print_game_data_debug()
            self.network_issues = False

        elif self.current_game is not None:
            # prefer to update the existing game rather than
            # rotating if its the same game.
            # this helps with e.g. the delay logic
            debug.log("Rotating to the same game, refreshing instead")
            self.refresh_game()

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

    def __update_layout_state(self):
        import data.config.layout as layout

        self.config.layout.set_state()
        if self.current_game.status() == status.WARMUP:
            self.config.layout.set_state(layout.LAYOUT_STATE_WARMUP)

        if self.current_game.is_no_hitter():
            self.config.layout.set_state(layout.LAYOUT_STATE_NOHIT)

        if self.current_game.is_perfect_game():
            self.config.layout.set_state(layout.LAYOUT_STATE_PERFECT)

    def print_game_data_debug(self):
        debug.log("Game Data Refreshed: %s", self.current_game._current_data["gameData"]["game"]["id"])
        debug.log("Current game is %d seconds behind", self.current_game.current_delay())
        debug.log("Pre: %s", Pregame(self.current_game, self.config.time_format))
        debug.log("Live: %s", Scoreboard(self.current_game))
        debug.log("Final: %s", Postgame(self.current_game))
