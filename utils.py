from collections.abc import Mapping

import os
import logging

from logging.handlers import RotatingFileHandler

from bullpen.logging import LOGGER


def setup_logger(verbose):
    LOGFILE = os.path.abspath(os.path.join(__file__, "..", "logs", "mlbled.log"))

    formatter = logging.Formatter("{levelname} ({asctime}): {message}", style="{", datefmt="%H:%M:%S")

    # Log to stdout
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    # Log to a file, handling rotation at 1MB
    fh = RotatingFileHandler(LOGFILE, maxBytes=0x100000, backupCount=5)
    fh.setFormatter(formatter)

    LOGGER.addHandler(sh)
    LOGGER.addHandler(fh)

    LOGGER.propagate = False
    if verbose:
        if verbose == "with-statsapi":
            import statsapi

            # Assign the scoreboard logger to statsapi
            statsapi.logger = LOGGER
    else:
        LOGGER.setLevel(logging.WARNING)


def deep_update(source, overrides):
    """Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    for key, value in list(overrides.items()):
        if isinstance(value, Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source
