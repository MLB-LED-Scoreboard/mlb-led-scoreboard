import statsapi
import debug

API_FIELDS = "uniforms,home,away,uniformAssets,uniformAssetText"


CITY_CONNECT = "city_connect"

# maybe one day we will also want to support e.g throwback
SPECIAL_UNIFORMS = {CITY_CONNECT: lambda uniformName: "City Connect" in uniformName}

# separate API call and not something we expect to change, so we don't do
# this as part of the Game data updates
class Uniforms:
    def __init__(self, game_id):
        self.home_special = None
        self.away_special = None
        try:
            data = statsapi.get("game_uniforms", {"gamePks": game_id, "fields": API_FIELDS})["uniforms"][0]
            for (uniform, special_check) in SPECIAL_UNIFORMS.items():
                home_uniforms = data.get("home", {}).get("uniforms", [])
                away_uniforms = data.get("away", {}).get("uniforms", [])

                if not self.home_special and any(special_check(asset['uniformAssetText']) for asset in home_uniforms):
                    self.home_special = uniform
                if not self.away_special and any(special_check(asset['uniformAssetText']) for asset in away_uniforms):
                    self.away_special = uniform

        except Exception:
            debug.exception(f"Error while fetching game {game_id} uniform data")

    def home_special_uniform(self):
        return self.home_special

    def away_special_uniform(self):
        return self.away_special
