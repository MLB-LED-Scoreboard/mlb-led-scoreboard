import sys
import json
from bullpen.util import deep_update

OLD_EXAMPLE = """
{
	"preferred": {
		"teams": ["Cubs"],
		"divisions": ["NL Central", "NL Wild Card"]
	},
	"news_ticker": {
		"team_offday": true,
		"always_display": false,
		"preferred_teams": true,
		"display_no_games_live": false,
		"traderumors": true,
		"mlb_news": true,
		"countdowns": true,
		"date": true,
		"date_format": "%A, %B %-d"
	},
	"standings": {
		"team_offday": false,
		"mlb_offday": true,
		"always_display": false,
		"display_no_games_live": true
	},
	"rotation": {
		"enabled": true,
		"scroll_until_finished": true,
		"only_preferred": false,
		"only_live": true,
		"rates": {
			"live": 15.0,
			"final": 15.0,
			"pregame": 15.0
		},
		"while_preferred_team_live": {
			"enabled": false,
			"during_inning_breaks": false
		},
		"include_standings": true,
		"include_news_ticker": false
	},
	"weather": {
		"apikey": "YOUR_API_KEY_HERE",
		"location": "Chicago,il,us",
		"metric_units": false
	},
	"time_format": "12h",
	"end_of_day": "00:00",
	"full_team_names": true,
	"short_team_names_for_runs_hits": true,
	"preferred_game_delay_multiplier": 0,
	"api_refresh_rate" : 5,
	"pregame_weather": true,
	"scrolling_speed": 2,
	"debug": false,
	"demo_date": false
}
"""

KEPT = [
    "weather",
    "time_format",
    "end_of_day",
    "preferred_game_delay_multiplier",
    "api_refresh_rate",
    "pregame_weather",
    "scrolling_speed",
    "debug",
    "demo_date",
]

NEWS = {"kind": "news", "seconds": 120, "with_priority": 0}
STANDINGS = {"kind": "standings", "seconds": 120, "with_priority": 0}


def build_screens(config):
    if config["news_ticker"]["always_display"]:
        return [NEWS]
    if config["standings"]["always_display"]:
        return [STANDINGS]

    preferred_team, *teams = config["preferred"]["teams"]

    requirement = "live" if config["rotation"]["only_live"] else None

    next_priority = 5
    preferred_game = {
        "kind": "game",
        "teams": [preferred_team],
        "priority": next_priority,
        "required_status": requirement,
    }

    if not config["rotation"]["while_preferred_team_live"]["enabled"]:
        next_priority -= 1
        if config["rotation"]["while_preferred_team_live"]["during_inning_breaks"]:
            preferred_game["required_status"] = "live_in_inning"

    other_games = {
        "kind": "game",
        "priority": next_priority,
        "required_status": requirement,
    }

    if config["rotation"]["only_preferred"]:
        other_games["teams"] = [preferred_team] + teams

    screens = [preferred_game, other_games]
    next_priority -= 1

    if not config["news_ticker"]["display_no_games_live"] and not config["rotation"]["only_preferred"]:
        non_live_games = {
            "kind": "game",
            "priority": next_priority,
        }

        if config["rotation"]["only_preferred"]:
            non_live_games["teams"] = [preferred_team] + teams
        screens.append(non_live_games)

    screens.extend([STANDINGS, NEWS])
    return screens


if __name__ == "__main__":

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"

    with open(config_path, "r") as f:
        config = json.load(f)

    if 'format' in config and config["format"] == 9:
        print("Config is already in format 9, no upgrade needed.")
        sys.exit(0)

    deep_update(config, json.loads(OLD_EXAMPLE))

    new_config = {
        "$schema": "./config.schema.json",
        "format": 9,
    }

    new_config["rotation"] = {
        "scroll_until_finished": config["rotation"]["scroll_until_finished"],
        "rates": config["rotation"]["rates"],
        "screens": build_screens(
            config,
        ),
    }

    preferred_teams = config["preferred"]["teams"]
    preferred_divisions = config["preferred"]["divisions"]

    new_config["news_ticker"] = {
        "teams": preferred_teams if config["news_ticker"]["preferred_teams"] else [],
        "traderumors": config["news_ticker"]["traderumors"],
        "mlb_news": config["news_ticker"]["mlb_news"],
        "countdowns": config["news_ticker"]["countdowns"],
        "date": config["news_ticker"]["date"],
        "date_format": config["news_ticker"]["date_format"],
    }
    new_config["standings"] = {"divisions": preferred_divisions}

    for key in KEPT:
        new_config[key] = config[key]

    with open(config_path + ".new", "w") as f:
        json.dump(new_config, f, indent=4)
