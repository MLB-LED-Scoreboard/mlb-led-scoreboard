import asyncio
import threading
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
        self.is_charging = False
        self.is_discharging = False
        self.is_grid_active = False
        self.operation_mode = "—"
        self.grid_status = "—"
        self.available = False

        # A single persistent event loop keeps the aiohttp session alive so we
        # only hit the rate-limited login endpoint once.
        self._pw = None
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()

        self.update(force=True)

    def update(self, force: bool = False) -> UpdateStatus:
        if not force and time.time() - self.last_update < self.config.update_interval:
            return UpdateStatus.DEFERRED
        if not self.config.host or not self.config.password:
            return UpdateStatus.DEFERRED

        self.last_update = time.time()
        try:
            future = asyncio.run_coroutine_threadsafe(self._fetch(), self._loop)
            future.result(timeout=30)
            self.available = True
            return UpdateStatus.SUCCESS
        except Exception:
            LOGGER.exception("[POWERWALL] Failed to fetch data from %s", self.config.host)
            self.available = False
            return UpdateStatus.FAIL

    async def _fetch(self) -> None:
        from tesla_powerwall import Powerwall

        if self._pw is None:
            LOGGER.info("[POWERWALL] Opening session with %s", self.config.host)
            self._pw = Powerwall(self.config.host, verify_ssl=self.config.verify_ssl)
            await self._pw.login(self.config.password, self.config.email)

        try:
            meters = await self._pw.get_meters()
            self.solar_kw = float(meters.solar.get_power())
            self.home_kw = float(meters.load.get_power())
            self.grid_kw = float(meters.site.get_power())
            self.battery_kw = float(meters.battery.get_power())
            self.charge_pct = float(await self._pw.get_charge())

            self.is_charging = self.battery_kw < -0.05
            self.is_discharging = self.battery_kw > 0.05
            self.is_grid_active = self.grid_kw > 0.05

            try:
                mode = await self._pw.get_operation_mode()
                self.operation_mode = _humanize(mode)
            except Exception:
                LOGGER.debug("[POWERWALL] get_operation_mode unavailable (gateway-only endpoint)")

            try:
                grid = await self._pw.get_grid_status()
                self.grid_status = _humanize(grid)
            except Exception:
                LOGGER.debug("[POWERWALL] get_grid_status unavailable (gateway-only endpoint)")

        except Exception:
            # Session likely expired — reset so we re-login on the next attempt
            LOGGER.warning("[POWERWALL] Session error, will re-login on next fetch")
            try:
                await self._pw.close()
            except Exception:
                pass
            self._pw = None
            raise


def _humanize(enum_value) -> str:
    raw = getattr(enum_value, "value", str(enum_value))
    return str(raw).replace("_", " ").title()
