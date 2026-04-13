import logging

from logging.handlers import RotatingFileHandler

LOGGER = logging.getLogger("bullpen")

formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Log to stdout
sh = logging.StreamHandler()
sh.setFormatter(formatter)

LOGGER.addHandler(sh)

LOGGER.propagate = False

def set_log_directory(path):
    # Log to a file, handling rotation at 1MB
    fh = RotatingFileHandler(path, maxBytes=0x100000, backupCount=5)
    fh.setFormatter(formatter)
    LOGGER.addHandler(fh)