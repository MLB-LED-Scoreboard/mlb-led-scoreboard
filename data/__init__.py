from typing import Optional


from data.game import Game
from data.headlines import Headlines
from data.schedule import Schedule
from data.standings import Standings
from data import update
from bullpen import UpdateStatus
from data.weather import Weather
from data.config import Config
from data.utils.double_buffer import DoubleBuffer


class Data:
    def __init__(self, config: Config, plugin_data) -> None:
        # Save the parsed config
        self.config: Config = config
        self.plugin_data = plugin_data
        # get schedule
        self.schedule: Schedule = Schedule(config)

        # Games -- keeps two copies internally to let render thread move asynchronously
        self.games = DoubleBuffer(self.schedule.next_game())

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
        self.games.producer_tick(self.schedule.next_game)

        # network requests
        self.__process_network_status(update.merge(g.update() for g in self.games.items))

    def refresh_standings(self):
        self.__process_network_status(self.standings.update())

    def refresh_weather(self):
        self.__process_network_status(self.weather.update())

    def refresh_news_ticker(self):
        self.__process_network_status(self.headlines.update())

    def refresh_schedule(self):
        self.__process_network_status(self.schedule.update())

    def refresh_plugins(self):
        self.__process_network_status(update.merge(plugin.update() for plugin in self.plugin_data.values()))

    def __process_network_status(self, status):
        if status == UpdateStatus.SUCCESS:
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True
