from bullpen.api import UpdateStatus, PluginData
from bullpen.logging import LOGGER
from data.config import Config

from data.schedule import Schedule
from data.utils.double_buffer import DoubleBuffer


class Data:
    def __init__(self, config: Config, plugin_data: dict[str, PluginData]) -> None:
        # Save the parsed config
        self.config: Config = config
        self.network_issues: bool = False
        self.plugin_data = plugin_data

        # get schedule
        self.schedule: Schedule = Schedule(config)
        # Games -- keeps two copies internally to let render thread move asynchronously
        self.games = DoubleBuffer(self.schedule.next_game())

    def refresh_game(self) -> None:
        # handle double buffering
        status = self.games.producer_tick(self.schedule.next_game)
        status = UpdateStatus.merge([status] + [g.update() for g in self.games.items if g is not None])

        # network requests
        self.__process_network_status(status)

    def refresh_schedule(self) -> None:
        self.__process_network_status(self.schedule.update())

    def refresh_plugin(self, name: str) -> None:
        plugin = self.plugin_data[name]
        status = UpdateStatus.FAIL
        try:
            status = plugin.update()
        except KeyboardInterrupt as e:
            raise e
        except:
            LOGGER.exception("Failure while updating plugin %s", name)

        self.__process_network_status(status)

    def __process_network_status(self, status) -> None:
        if status == UpdateStatus.SUCCESS:
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True
