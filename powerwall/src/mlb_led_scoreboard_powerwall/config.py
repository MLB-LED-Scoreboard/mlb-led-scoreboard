import bullpen.api as api
from bullpen.logging import LOGGER


class Config(api.PluginConfig):
    def __init__(self, base: api.MLBConfig) -> None:
        self.scrolling_speed = base.scrolling_speed

        cfg = base.plugin_config
        self.host = cfg.get("host", "")
        self.password = cfg.get("password", "")
        self.email = cfg.get("email", "")
        self.update_interval = cfg.get("update_interval", 30)
        self.verify_ssl = cfg.get("verify_ssl", False)

        if not self.host:
            LOGGER.warning("[POWERWALL] No 'host' configured. Plugin will not be able to fetch data.")
        if not self.password:
            LOGGER.warning("[POWERWALL] No 'password' configured. Plugin will not be able to fetch data.")
