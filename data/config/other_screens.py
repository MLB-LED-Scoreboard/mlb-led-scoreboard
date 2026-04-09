from datetime import time, datetime
from typing import Optional
import calendar

WEEKDAYS = {day.lower(): n for n, day in enumerate(calendar.day_abbr)} | {
    day.lower(): n for n, day in enumerate(calendar.day_name)
}


class TimeRule:
    def __init__(
        self,
        priority: int,
        *,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        weekdays: list[str] = [],
    ):
        self.priority = priority
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays = set(WEEKDAYS[name.lower()] for name in weekdays)

    def matches(self, now: datetime) -> int:
        if self.weekdays and now.weekday() not in self.weekdays:
            return 0

        time = now.time()
        if self.start_time and time < self.start_time:
            return 0
        if self.end_time and time > self.end_time:
            return 0
        return self.priority

    def __repr__(self):
        return f"TimeRule(priority={self.priority}, start_time={self.start_time}, end_time={self.end_time})"

    def __eq__(self, other):
        return (
            isinstance(other, TimeRule)
            and self.priority == other.priority
            and self.start_time == other.start_time
            and self.end_time == other.end_time
        )


def parse_time_rule(rule_json) -> TimeRule:
    if "priority" not in rule_json:
        raise ValueError(f"Invalid time rule in config, missing 'priority' field. Rule: {rule_json}")
    start_time = None
    end_time = None
    weekdays = []
    if "start_time" in rule_json:
        try:
            start_time = datetime.strptime(rule_json["start_time"], "%H:%M").time()
        except ValueError:
            raise ValueError(f"Invalid time format for 'start_time' in config. Expected HH:MM. Rule: {rule_json}")
    if "end_time" in rule_json:
        try:
            end_time = datetime.strptime(rule_json["end_time"], "%H:%M").time()
        except ValueError:
            raise ValueError(f"Invalid time format for 'end_time' in config. Expected HH:MM. Rule: {rule_json}")
    if "weekdays" in rule_json:
        days = rule_json["weekdays"]
        if isinstance(days, str):
            days = [days]
        if isinstance(days, list) and all(day.lower() in WEEKDAYS for day in days):
            weekdays = days
        else:
            raise ValueError(f"Invalid day in 'weekdays' list. Rule: {rule_json}")
    if not any([start_time, end_time, weekdays]):
        raise ValueError(
            f"Invalid time rule in config, need at least one of 'start_time', 'end_time', or 'weekdays' fields. Rule: {rule_json}"
        )
    return TimeRule(priority=rule_json["priority"], start_time=start_time, end_time=end_time, weekdays=weekdays)


def parse_with_priority(json) -> list[int]:
    with_priority = json.get("with_priority")
    if with_priority is None:
        raise ValueError(f"Invalid screen rule in config, missing 'with_priority' field. Rule: {json}")

    if isinstance(with_priority, int):
        return [with_priority]
    elif isinstance(with_priority, list) and all(isinstance(p, int) for p in with_priority):
        return with_priority
    else:
        raise ValueError(
            f"Invalid screen rule in config, 'with_priority' field should be an integer or list of integers. Rule: {json}"
        )
