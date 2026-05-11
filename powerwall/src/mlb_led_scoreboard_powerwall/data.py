import asyncio
import time

from bullpen.api import PluginData, UpdateStatus
from bullpen.logging import LOGGER

from .config import Config


class PowerwallData(PluginData):
    def __init__(self, config: Config) -> None:
        self.config = config
        self.last_update = 0.0

        self.solar_kw = 0.0
        self.home_kw = 0.0
        self.grid_kw = 0.0
        self.battery_kw = 0.0
        self.charge_pct = 0.0
        self.operation_mode = "—"
        self.grid_status = "—"
        self.available = False

        self.update(force=True)

    def update(self, force: bool = False) -> UpdateStatus:
        if not force and time.time() - self.last_update < self.config.update_interval:
            return UpdateStatus.DEFERRED
        if not self.config.host or not self.config.password:
            return UpdateStatus.DEFERRED

        self.last_update = time.time()
        try:
            asyncio.run(self._fetch())
            self.available = True
            return UpdateStatus.SUCCESS
        except Exception:
            LOGGER.exception("[POWERWALL] Failed to fetch data from %s", self.config.host)
            self.available = False
            return UpdateStatus.FAIL

    async def _fetch(self) -> None:
        from tesla_powerwall import Powerwall

        pw = Powerwall(self.config.host, verify_ssl=self.config.verify_ssl)
        try:
            await pw.login(self.config.password, self.config.email)

            meters = await pw.get_meters()
            self.solar_kw = float(meters.solar.get_power())
            self.home_kw = float(meters.load.get_power())
            self.grid_kw = float(meters.site.get_power())
            self.battery_kw = float(meters.battery.get_power())

            self.charge_pct = float(await pw.get_charge())

            mode = await pw.get_operation_mode()
            self.operation_mode = _humanize(mode)

            grid = await pw.get_grid_status()
            self.grid_status = _humanize(grid)
        finally:
            try:
                await pw.close()
            except Exception:
                LOGGER.debug("[POWERWALL] Error closing Powerwall session", exc_info=True)


def _humanize(enum_value) -> str:
    raw = getattr(enum_value, "value", str(enum_value))
    return str(raw).replace("_", " ").title()
