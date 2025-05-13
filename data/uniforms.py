import time
import statsapi

import debug

API_FIELDS = "uniforms,home,away,uniformAssets,uniformAssetText"

UPDATE_RATE = 60 * 5  # almost never necessary to update uniforms once set

CITY_CONNECT = "city_connect"

# maybe one day we will also want to support e.g throwback
SPECIAL_UNIFORMS = {CITY_CONNECT: lambda uniformName: "City Connect" in uniformName}


# separate API call and not something we expect to change, so we don't do
# this as part of the Game data updates
class Uniforms:
    def __init__(self, game_id):
        self.game_id = game_id
        self.home_special = None
        self.away_special = None
        self.starttime = time.time()
        self.update(force=True)

    def home_special_uniform(self):
        return self.home_special

    def away_special_uniform(self):
        return self.away_special

    def update(self, force=False):
        if self.away_special is not None or self.home_special is not None:
            # these should never change if already populated for this game
            return
        if not force and not self.__should_update():
            return

        try:
            data = statsapi.get("game_uniforms", {"gamePks": self.game_id, "fields": API_FIELDS})["uniforms"][0]
            for uniform, special_check in SPECIAL_UNIFORMS.items():
                home_uniforms = data.get("home", {}).get("uniformAssets", [])
                away_uniforms = data.get("away", {}).get("uniformAssets", [])

                if not self.home_special and any(
                    special_check(asset["uniformAssetText"]) for asset in home_uniforms
                ):
                    self.home_special = uniform
                if not self.away_special and any(
                    special_check(asset["uniformAssetText"]) for asset in away_uniforms
                ):
                    self.away_special = uniform
        except Exception:
            debug.exception(f"Error while fetching game {self.game_id} uniform data")

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= UPDATE_RATE
