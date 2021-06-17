import sys
import time

import data.scoreboard_config

debug_enabled = False
time_format = "%H"


def set_debug_status(config):
    global debug_enabled
    debug_enabled = config.debug

    global time_format
    time_format = config.time_format


def __debugprint(text):
    print(text)
    sys.stdout.flush()


def log(text):
    if debug_enabled:
        __debugprint("DEBUG ({}): {}".format(__timestamp(), text))


def warning(text):
    __debugprint("WARNING ({}): {}".format(__timestamp(), text))


def error(text):
    __debugprint("ERROR ({}): {}".format(__timestamp(), text))


def info(text):
    __debugprint("INFO ({}): {}".format(__timestamp(), text))


def __timestamp():
    return time.strftime("%H:%M:%S", time.localtime())
