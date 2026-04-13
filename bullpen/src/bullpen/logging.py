import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path


LOGGER = logging.getLogger("bullpen")
LOGGER.setLevel(logging.INFO)
_LOGFILE = Path(__file__).parents[3] / "logs" / "bullpen.log"

formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Log to stdout
sh = logging.StreamHandler()
sh.setFormatter(formatter)

# Log to a file, handling rotation at 1MB
fh = RotatingFileHandler(_LOGFILE, maxBytes=0x100000, backupCount=5)
fh.setFormatter(formatter)

LOGGER.addHandler(sh)
LOGGER.addHandler(fh)

LOGGER.propagate = False
