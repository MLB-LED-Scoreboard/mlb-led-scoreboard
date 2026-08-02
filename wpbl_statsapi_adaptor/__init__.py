import requests
import data.status

BASE_URL = "https://stats.womensprobaseballleague.com/"

ENDPOINTS = {
    "schedule": {
        "url": BASE_URL + "/v1/games",
    },
    "game": {
        "url": BASE_URL + "/v1/games/{gamePk}",
        "path_params": ["gamePk"],
    },
    "boxscore": {
        "url": BASE_URL + "/v1/games/{gamePk}/boxscore",
        "path_params": ["gamePk"],
    },
}


def is_wpbl_game(game_id):
    return not (isinstance(game_id, int) or game_id.isnumeric())


def translate_status(status):
    # TODO more statuses
    match status:
        case "Not Started":
            return data.status.PREGAME
        case "In Progress":
            return data.status.LIVE
        case s if s.startswith("Final"):
            return data.status.FINAL
        case _:
            return data.status.UNKNOWN


def get(endpoint, params={}, *, request_kwargs={}):
    endpoint = ENDPOINTS[endpoint]

    path_params = {}
    query_params = {}
    for key, value in params.items():
        if key in endpoint.get("path_params", []):
            path_params[key] = value
        else:
            query_params[key] = value

    url = endpoint["url"].format(**path_params)
    # if len(query_params) > 0:
    #     for k, v in query_params.items():
    #         sep = "?" if url.find("?") == -1 else "&"
    #         url += sep + k + "=" + v

    r = requests.get(url, **request_kwargs)
    if r.status_code not in [200, 201]:
        r.raise_for_status()
    else:
        return r.json()


def schedule(
    date=None,
    sportId="bsb",
    leagueId=None,
):

    r = get("schedule")
    games = []

    for i, game in enumerate(r.get("games", [])):
        if date is not None and not game["scheduled_start"].startswith(date):
            continue

        game_info = {
            "game_id": game["game_id"],
            "game_datetime": game["scheduled_start"],
            "game_date": game["scheduled_start"].split("T")[0],
            "game_type": game["game_type"][0].upper(),
            "status": translate_status(game["state"]["status"]),
            "away_name": game["away_team_name"],
            "home_name": game["home_team_name"],
            "away_id": game["away_team_id"],
            "home_id": game["home_team_id"],
            "doubleheader": False,  # TODO
            "game_num": i,
            "home_probable_pitcher": "",
            "away_probable_pitcher": "",
            "home_pitcher_note": "",
            "away_score": game["presto_data"]["score"]["away"],
            "home_score": game["presto_data"]["score"]["home"],
            "current_inning": game["state"]["inning"],
            "inning_state": game["state"]["half"].title() or "Top",
            "venue_id": None,  # TODO
            "venue_name": game["presto_data"]["venue"],
            "national_broadcasts": ["ESPN+"],  # TODO
            "series_status": None,  # TODO
            "summary": "",
        }

        games.append(game_info)

    return games


def make_fake_player_id(name):
    return {"ID" + name: {"boxscoreName": name.split(" ")[-1], "fullName": name}}


# TODO consider if this should be alternative Game.py etc?
def game(params, *, request_kwargs={}):
    game = get("game", params, request_kwargs=request_kwargs)
    boxscore = get("boxscore", params, request_kwargs=request_kwargs)["boxscore"]

    boxscore_away_team = boxscore["teams"][0]
    boxscore_home_team = boxscore["teams"][1]
    assert boxscore_home_team["side"] == "home"

    plays = boxscore.get("plays", []) or []

    # TODO: does this ever show mid/end of innings?
    # TODO: due up batters, probable pitchers, winning/losing/save pitcher?
    inning = boxscore["status"]["inning"] or plays[-1]["inning"] if len(plays) > 0 else 1

    return {
        "gameData": {
            "status": {
                "detailedState": translate_status(boxscore["game_status"]),
                "reason": boxscore["game_status"],
                "abstractGameState": "Final" if boxscore["status"]["complete"] else "",
            },
            "game": {"id": boxscore["game_id"]},
            "datetime": {
                "officialDate": game["scheduled_start"].split("T")[0],
                "dateTime": game["scheduled_start"],
            },
            "teams": {
                "home": {
                    "id": game["home_team_id"],
                    "teamName": game["home_team_name"],
                    "abbreviation": "???",
                    "record": (
                        {
                            "wins": boxscore_away_team["record"].split("-")[0],
                            "losses": boxscore_away_team["record"].split("-")[1],
                        }
                        if boxscore_away_team.get("record")
                        else {}
                    ),
                },
                "away": {
                    "id": game["away_team_id"],
                    "teamName": game["away_team_name"],
                    "abbreviation": "???",
                    "record": (
                        {
                            "wins": boxscore_away_team["record"].split("-")[0],
                            "losses": boxscore_away_team["record"].split("-")[1],
                        }
                        if boxscore_away_team.get("record")
                        else {}
                    ),
                },
                "players": make_fake_player_id(boxscore["status"]["pitcher_name"])
                | make_fake_player_id(boxscore["status"]["batter_name"]),
            },
            "flags": {
                "noHitter": inning > 5
                and (boxscore_home_team["totals"]["hits"] == 0 or boxscore_away_team["totals"]["hits"] == 0),
                "perfectGame": False,  # TODO
            },
        },
        "liveData": {
            "linescore": {
                "balls": boxscore["status"]["balls"],
                "strikes": boxscore["status"]["strikes"],
                "outs": boxscore["status"]["outs"],
                "inningState": (
                    boxscore["status"]["half"].title() or plays[-1]["half"].title() if len(plays) > 0 else "Top"
                ),
                "currentInning": inning,
                "currentInningOrdinal": f"{inning}{'st' if inning == 1 else 'nd' if inning == 2 else 'rd' if inning == 3 else 'th'}",
                "offense": {
                    "first": {"id": boxscore["status"]["first_base"]},
                    "second": {"id": boxscore["status"]["second_base"]},
                    "third": {"id": boxscore["status"]["third_base"]},
                    "batter": {"id": boxscore["status"]["batter_name"]},
                },
                "defense": {
                    "pitcher": {"id": boxscore["status"]["pitcher_name"]},
                },
                "teams": {
                    "home": {
                        "runs": boxscore_home_team["totals"]["runs"],
                        "hits": boxscore_home_team["totals"]["hits"],
                        "errors": boxscore_home_team["totals"]["errors"],
                    },
                    "away": {
                        "runs": boxscore_away_team["totals"]["runs"],
                        "hits": boxscore_away_team["totals"]["hits"],
                        "errors": boxscore_away_team["totals"]["errors"],
                    },
                },
            },
            "plays": {
                "currentPlay": {
                    "result": {
                        "eventType": plays[-1]["event_type"] if len(plays) > 0 else "",
                        "description": (
                            "called out on strikes" if len(plays) > 0 and "looking" in plays[-1]["narrative"] else ""
                        ),
                    }
                }
            },
        },
    }
