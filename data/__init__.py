import time

import data.config.layout as layout
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
        if self.current_game is not None:
            self.print_game_data_debug()

        self.game_changed_time = time.time()
        if self.current_game is not None:
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
        game = self.current_game
        if not self.config.rotation_enabled:
            return False

        stay_on_preferred_team = self.config.preferred_teams and not self.config.rotation_preferred_team_live_enabled
        if not stay_on_preferred_team:
            return True

        if self.schedule.num_games() < 2:
            if self.config.rotation_only_live and self.schedule.games_live():
                # don't want to get stuck on an dead game
                return not status.is_live(game.status())
            return False

        if game.features_team(self.config.preferred_teams[0]) and status.is_live(game.status()):
            if self.config.rotation_preferred_team_live_mid_inning and status.is_inning_break(game.inning_state()):
                return True
            return False

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
        if game is not None:
            if game.game_id != self.current_game.game_id:
                self.game_changed_time = time.time()
            self.current_game = game
            self.__update_layout_state()
            self.print_game_data_debug()
            self.network_issues = False

        else:
            self.network_issues = True

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

    def get_screen_type(self):
        # Always the news
        if self.config.news_ticker_always_display:
            return "news"
        # Always the standings
        elif self.config.standings_always_display:
            return "standings"

        # Full MLB Offday
        elif self.schedule.is_offday():
            if self.config.standings_mlb_offday:
                return "standings"
            else:
                return "news"
        # Preferred Team Offday
        elif self.schedule.is_offday_for_preferred_team():
            if self.config.news_ticker_team_offday:
                return "news"
            elif self.config.standings_team_offday:
                return "standings"
        # Playball!
        else:
            return "games"

    def __update_layout_state(self):
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
