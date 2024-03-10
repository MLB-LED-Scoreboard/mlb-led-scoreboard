from enum import Enum


class Status(Enum):
    SUCCESS = 2
    DEFERRED = 1
    FAIL = 0


def ok(status):
    return status in [Status.SUCCESS, Status.DEFERRED]


def fail(status):
    return status in [Status.FAIL]
