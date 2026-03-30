from enum import Enum
from typing import Iterable


class UpdateStatus(Enum):
    SUCCESS = 2
    DEFERRED = 1
    FAIL = 0


def ok(status: UpdateStatus) -> bool:
    return status in [UpdateStatus.SUCCESS, UpdateStatus.DEFERRED]


def merge(s: Iterable[UpdateStatus]) -> UpdateStatus:
    statuses = set(s)
    if UpdateStatus.FAIL in statuses:
        return UpdateStatus.FAIL
    elif UpdateStatus.SUCCESS in statuses:
        return UpdateStatus.SUCCESS
    else:
        return UpdateStatus.DEFERRED
