from enum import Enum


class UpdateStatus(Enum):
    SUCCESS = 2
    DEFERRED = 1
    FAIL = 0


def ok(status):
    return status in [UpdateStatus.SUCCESS, UpdateStatus.DEFERRED]


def fail(status):
    return status in [UpdateStatus.FAIL]
