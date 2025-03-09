import logging, os
from logging.handlers import RotatingFileHandler

LOGFILE = os.path.abspath(os.path.join(__file__, "..", "logs", "mlbled.log"))

logger = logging.getLogger("mlbled")

formatter = logging.Formatter("{levelname} ({asctime}): {message}", style="{", datefmt="%H:%M:%S")

# Log to stdout
sh = logging.StreamHandler()
sh.setFormatter(formatter)

# Log to a file, handling rotation at 1MB
fh = RotatingFileHandler(LOGFILE, maxBytes=0x100000, backupCount=5)
fh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)

logger.propagate = False

log = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
exception = logger.exception
