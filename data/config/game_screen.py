from enum import Enum
from typing import Optional

from data import game, status
from data import teams as team_metadata
from data.config.other_screens import parse_with_priority


class Requirements(Enum):
    LIVE = "live"
    LIVE_IN_INNING = "live_in_inning"
    PREGAME = "pregame"
    GAME_OVER = "game_over"

    def __str__(self):
        return self.value

    @staticmethod
    def from_str(label):
        for requirement in Requirements:
            if requirement.value == label:
                return requirement
        raise ValueError(f"Unknown requirement: {label}")


def parse_requirements(json) -> Optional[Requirements]:
    json_requirement = json.get("required_status")
    if json_requirement:
        try:
            return Requirements.from_str(json_requirement)
        except ValueError:
            raise ValueError(
                "Invalid game rule in config, unknown required_status '{}'. Rule: {}".format(json_requirement, json)
            )
    return None


class GameScreen:
    DEFAULT_PRIORITY = 0, True

    def __init__(
        self,
        priority: int,
        *,
        requirement: Optional[Requirements] = None,
        passive=False,
        teams: list[str] = [],
    ):
        self.requirement = requirement
        self.when_matched = priority, passive
        self.teams = set(team_metadata.get_team_id(t) for t in teams)

    def priority(self) -> int:
        return self.when_matched[0]

    def matches(self, game) -> tuple[int, bool]:
        if self.teams and not set([game["away_id"], game["home_id"]]).intersection(self.teams):
            return GameScreen.DEFAULT_PRIORITY

        if self.requirement is None:
            return self.when_matched

        if self.requirement == Requirements.PREGAME and status.is_pregame(game["status"]):
            return self.when_matched

        if self.requirement == Requirements.GAME_OVER and status.is_complete(game["status"]):
            return self.when_matched

        if self.requirement == Requirements.LIVE and (
            status.is_fresh(game["status"]) or (status.is_live(game["status"]))
        ):
            return self.when_matched

        if self.requirement == Requirements.LIVE_IN_INNING and (
            status.is_live(game["status"])
            and game["status"] != status.WARMUP
            and not status.is_inning_break(game["inning_state"])
        ):
            return self.when_matched

        return GameScreen.DEFAULT_PRIORITY

    def __repr__(self):
        return (
            f"GameRule(priority={self.when_matched[0]}, requirement={self.requirement}"
            f", passive={self.when_matched[1]}, teams={self.teams})"
        )

    def __eq__(self, other):
        if not isinstance(other, GameScreen):
            return NotImplemented
        return (
            self.requirement == other.requirement
            and self.when_matched == other.when_matched
            and self.teams == other.teams
        )


def parse_game_screen(rule_json) -> list[GameScreen]:
    requirement = parse_requirements(rule_json)
    teams = rule_json.get("teams", [])
    if rule_json["kind"] == "game":
        if "priority" not in rule_json:
            raise ValueError("Invalid game rule in config, missing 'priority' field. Rule: {}".format(rule_json))
        rule = GameScreen(
            priority=rule_json["priority"],
            requirement=requirement,
            passive=False,
            teams=teams,
        )
        return [rule]
    elif rule_json["kind"] == "secondary_game":
        game_rules = []
        for priority in parse_with_priority(rule_json):
            rule = GameScreen(
                priority=priority,
                requirement=requirement,
                passive=True,
                teams=teams,
            )
            game_rules.append(rule)
        return game_rules
    return []
