from enum import Enum
from typing import Optional

from data import status
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
    def from_str(label: str) -> Optional["Requirements"]:
        for requirement in Requirements:
            if requirement.value == label:
                return requirement
        raise ValueError(f"Unknown requirement: {label}")

    def matches(self, game) -> bool:
        game_status = game["status"]
        match self:
            case Requirements.PREGAME:
                return status.is_pregame(game_status)
            case Requirements.GAME_OVER:
                return status.is_complete(game_status)
            case Requirements.LIVE:
                return status.is_fresh(game_status) or status.is_live(game_status)
            case Requirements.LIVE_IN_INNING:
                return (
                    status.is_live(game_status)
                    and game_status != status.WARMUP
                    and not status.is_inning_break(game["inning_state"])
                )


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
        if self.teams and not self.teams.intersection([game["away_id"], game["home_id"]]):
            return GameScreen.DEFAULT_PRIORITY

        if self.requirement is None or self.requirement.matches(game):
            return self.when_matched

        return GameScreen.DEFAULT_PRIORITY

    def __repr__(self):
        return (
            f"GameScreen(priority={self.when_matched[0]}, requirement={self.requirement}"
            f", passive={self.when_matched[1]}, teams={self.teams})"
        )

    def __eq__(self, other):
        return (
            isinstance(other, GameScreen)
            and self.requirement == other.requirement
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
